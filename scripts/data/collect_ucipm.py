"""Bounded research-only UC IPM HTML acquisition and faithful offline extraction.

No media, recursive crawl, advice approval, translation, model or product changes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import random
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urldefrag, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup, Tag
from clean_plantexpert import digest, pairs_unique, write_json

PARSER_VERSION = "ucipm-html-1.0"
USES = ("research_copy", "technical_processing", "adaptation_translation",
        "app_repo_demo_distribution", "media_ml")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=pairs_unique)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def local(project, relative):
    path = (project / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(project) or path == project:
        raise ValueError("Path must stay below project")
    return path


def robots_allowed(text, url, agent):
    """Longest path wins; Allow wins ties; specific user-agent groups win wildcard."""
    groups, agents, rules = [], [], []
    for raw in text.splitlines() + ["User-agent: __end__"]:
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, value = (s.strip() for s in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if rules:
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(value.lower())
        elif key in ("allow", "disallow") and agents and value:
            rules.append((key, value))
    matches = []
    for names, directives in groups:
        scores = [0 if n == "*" else len(n) for n in names if n == "*" or n in agent.lower()]
        if scores:
            matches.append((max(scores), directives))
    if not matches:
        return True
    best = max(score for score, _ in matches)
    path = unquote(urlsplit(url).path or "/")
    if urlsplit(url).query:
        path += "?" + urlsplit(url).query
    hits = []
    for score, directives in matches:
        if score != best:
            continue
        for key, pattern in directives:
            end = pattern.endswith("$")
            body = pattern[:-1] if end else pattern
            regex = "^" + ".*".join(re.escape(unquote(s)) for s in body.split("*")) + ("$" if end else "")
            if re.search(regex, path):
                hits.append((len(body.replace("*", "")), key == "allow"))
    return max(hits)[1] if hits else True


class StopBatch(Exception):
    def __init__(self, reason, metadata=None):
        self.reason, self.metadata = reason, metadata or {}
        super().__init__(reason)


class Fetcher:
    """One synchronous request, bounded decoded bytes, manual redirect and checkpoint."""
    def __init__(self, config, session=None, clock=time.monotonic, sleep=time.sleep):
        self.config = config
        self.session = session or requests.Session()
        self.clock, self.sleep = clock, sleep
        self.finished = None
        self.total = 0
        self.events = []
        self.robot_text = {}

    def fetch(self, url, allowed, cache=None, robots=True, text=False):
        if url not in allowed:
            raise ValueError("URL outside explicit allowlist")
        original, hops = url, []
        while True:
            host = urlsplit(url).netloc
            if urlsplit(url).scheme != "https" or urlsplit(url).username:
                raise ValueError("Only HTTPS with no userinfo")
            if robots:
                if host not in self.robot_text:
                    raise StopBatch("robots_unverified", {"url": url})
                if not robots_allowed(self.robot_text[host], url, self.config["user_agent"]):
                    raise StopBatch("robots_deny", {"url": url})
            for attempt in range(3):
                if attempt:
                    self.sleep((10, 30)[attempt - 1] + random.uniform(0, 0.25))
                if self.finished is not None:
                    self.sleep(max(0, self.config["delay_seconds"] - (self.clock() - self.finished)))
                start = self.clock()
                headers = {"User-Agent": self.config["user_agent"], "Accept": "text/plain" if text else "text/html"}
                if cache and cache.get("final_url") == url:
                    if cache.get("etag"):
                        headers["If-None-Match"] = cache["etag"]
                    if cache.get("last_modified"):
                        headers["If-Modified-Since"] = cache["last_modified"]
                meta = {"original_url": original, "final_url": url, "accessed_at": now(),
                        "http_status": None, "redirects": list(hops), "snapshot_sha256": None,
                        "bytes": None, "attempt": attempt + 1}
                try:
                    with self.session.get(url, headers=headers, timeout=self.config["timeout_seconds"],
                                          stream=True, allow_redirects=False) as response:
                        meta.update(http_status=response.status_code,
                                    content_type=response.headers.get("Content-Type", ""),
                                    etag=response.headers.get("ETag"),
                                    last_modified=response.headers.get("Last-Modified"),
                                    retry_after=response.headers.get("Retry-After"))
                        status = response.status_code
                        if status in (403, 429):
                            raise StopBatch("http_" + str(status), meta)
                        if status in (301, 302, 303, 307, 308):
                            destination = urldefrag(urljoin(url, response.headers.get("Location", "")))[0]
                            if destination not in allowed or urlsplit(destination).netloc != host:
                                return dict(meta, acquisition="blocked", reason="redirect_review", redirect_target=destination), None
                            if len(hops) >= 3 or destination == url or destination in hops:
                                return dict(meta, acquisition="blocked", reason="redirect_limit"), None
                            hops.append(url)
                            url = destination
                            break
                        if status == 304:
                            if not cache or not cache.get("path"):
                                return dict(meta, acquisition="blocked", reason="304_without_cache"), None
                            path = Path(cache["path"])
                            if not path.is_file() or digest(path) != cache.get("snapshot_sha256"):
                                return dict(meta, acquisition="blocked", reason="304_invalid_cache"), None
                            data = path.read_bytes()
                            if len(data) > self.config["item_limit_bytes"]:
                                return dict(meta, acquisition="blocked", reason="cache_limit"), None
                            return dict(meta, acquisition="reused", bytes=len(data),
                                        content_type=cache.get("content_type"),
                                        snapshot_sha256=cache["snapshot_sha256"]), data
                        if 500 <= status <= 599:
                            if attempt < 2:
                                continue
                            return dict(meta, acquisition="blocked", reason="http_5xx_exhausted"), None
                        if status != 200:
                            return dict(meta, acquisition="blocked", reason="http_error"), None
                        ctype = meta["content_type"].split(";", 1)[0].strip().lower()
                        expected = ("text/plain",) if text else ("text/html", "application/xhtml+xml")
                        if ctype not in expected or "attachment" in response.headers.get("Content-Disposition", "").lower():
                            return dict(meta, acquisition="blocked", reason="not_html_or_attachment"), None
                        size, chunks = 0, []
                        for chunk in response.iter_content(chunk_size=16384):
                            size += len(chunk)
                            self.total += len(chunk)
                            if size > self.config["item_limit_bytes"]:
                                return dict(meta, acquisition="blocked", reason="item_byte_limit"), None
                            if self.total > self.config["batch_limit_bytes"]:
                                raise StopBatch("batch_byte_limit", meta)
                            if self.clock() - start > self.config["timeout_seconds"]:
                                raise requests.Timeout("request_deadline")
                            chunks.append(chunk)
                        data = b"".join(chunks)
                        if not data:
                            return dict(meta, acquisition="blocked", reason="empty_body"), None
                        if not text:
                            beginning = data[:16384].decode("ascii", "ignore").lower()
                            if any(marker in beginning for marker in ("cf-chl-", "g-recaptcha", "hcaptcha", "verify you are human")):
                                raise StopBatch("captcha", meta)
                            if not re.search(r"<!doctype\s+html|<html(?:\s|>)", beginning):
                                return dict(meta, acquisition="blocked", reason="not_html_payload"), None
                            title = BeautifulSoup(data, "html.parser").title
                            if title and re.search(r"access denied|forbidden|page not found|\b404\b|server error", title.get_text(), re.I):
                                return dict(meta, acquisition="blocked", reason="error_page"), None
                        return dict(meta, acquisition="downloaded", bytes=size,
                                    snapshot_sha256=hashlib.sha256(data).hexdigest()), data
                except StopBatch:
                    raise
                except (requests.Timeout, requests.ConnectionError) as error:
                    meta["error"] = type(error).__name__
                    if isinstance(error, requests.exceptions.SSLError):
                        return dict(meta, acquisition="blocked", reason="tls_error"), None
                    if attempt == 2:
                        return dict(meta, acquisition="blocked", reason="connection_exhausted"), None
                except requests.RequestException as error:
                    return dict(meta, acquisition="blocked", reason="response_error", error=type(error).__name__), None
                finally:
                    self.finished = self.clock()
                    self.events.append(meta)
            else:
                raise RuntimeError("fetch attempts exhausted")


def text_en(node):
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()


def locator(node):
    parts = []
    while isinstance(node, Tag) and node.name != "[document]":
        siblings = [n for n in node.parent.find_all(node.name, recursive=False)] if node.parent else [node]
        parts.append(node.name + ":nth-of-type(" + str(next(i for i, n in enumerate(siblings, 1) if n is node)) + ")")
        node = node.parent
    return " > ".join(reversed(parts))


def flags_for(text):
    flags = []
    for flag, pattern in (("quantitative", r"\d|percent|acre|gallon|ppm"),
                          ("chemical", r"fungicide|insecticide|pesticide|copper|bleach|sulfur|soap|oil spray"),
                          ("destructive_action", r"rogue|uproot|destroy|remove.{0,30}plant"),
                          ("conditional", r"\bif\b|might|may|possible|depending"),
                          ("negation", r"\bnot\b|\bno\b|never|avoid"),
                          ("organic_not_nonchemical", r"organic")):
        if re.search(pattern, text, re.I):
            flags.append(flag)
    return flags


def categories(path, text):
    context = " ".join(path).lower()
    result = []
    for kind, words in (("symptom_agent", ("symptom", "signs", "identification", "description")),
                        ("observation", ("monitor", "sampling")),
                        ("preventive_cultural", ("cultural", "water", "soil", "planting", "management")),
                        ("biological", ("biological", "natural enem")),
                        ("chemical", ("chemical", "treatment"))):
        if any(word in context for word in words):
            result.append(kind)
    if "chemical" in flags_for(text) and "chemical" not in result:
        result.append("chemical")
    return result or ["unclassified_review"]


def extract(data, item, metadata):
    """Conservative structural derivative: questionable extraction never passes clean."""
    charset_match = re.search(r"charset\s*=\s*[\"']?([^;\s\"']+)", metadata.get("content_type") or "", re.I)
    charset = charset_match.group(1) if charset_match else None
    if not charset:
        match = re.search(br"charset\s*=\s*[\"']?([a-zA-Z0-9_-]+)", data[:8192], re.I)
        charset = match.group(1).decode("ascii") if match else "utf-8"
    decoded = data.decode(charset, errors="strict")
    soup = BeautifulSoup(decoded, "html.parser")
    issues = []
    if "\ufffd" in decoded or re.search(r"Ã.|â€|Â©", decoded):
        issues.append("encoding_suspect")
    notices = [text_en(n) for n in soup.select("footer, [class*='copyright'], [id*='copyright'], [class*='disclaimer'], [class*='credit']")]
    notices += [s.strip() for s in soup.stripped_strings if re.search(r"copyright|©|all rights reserved|no endorsement", s, re.I)]
    notices = list(dict.fromkeys(n for n in notices if n))
    if any(re.search(r"third.party|used with permission|do not reproduce|no reproduction", n, re.I) for n in notices):
        issues.append("resource_specific_rights_notice_requires_review")
    content = soup.select_one("main") or soup.select_one("[role='main']") or soup.select_one("article")
    if content is None:
        raise ValueError("main_content_missing_requires_parser_review")
    # Locators refer to the untouched decoded DOM, not the reduced tree.
    locations = {id(n): locator(n) for n in content.find_all(True)}
    for n in content.select("script, style, iframe, form, nav, footer, noscript, button, [role='navigation']"):
        n.decompose()
    title = content.find("h1")
    if title is None or item["title"].casefold() not in text_en(title).casefold():
        issues.append("title_missing_or_mismatch")
    headings, blocks, section = [], [], []

    def common(node, kind):
        value = text_en(node)
        return {"kind": kind, "section_path": [s[1] for s in section],
                "section_locator": locations.get(id(node)), "anchor": node.get("id"),
                "text_en": value, "categories": categories([s[1] for s in section], value),
                "flags": flags_for(value),
                "links": [{"text_en": text_en(a), "href_original": a.get("href"),
                           "resolved_url": urljoin(metadata["final_url"], a.get("href", ""))} for a in node.find_all("a", href=True)],
                "emphasis": [{"tag": n.name, "text_en": text_en(n)} for n in node.find_all(["em", "i", "strong", "b", "sub", "sup"])]}

    def visit(node):
        if not isinstance(node, Tag):
            if str(node).strip():
                blocks.append({"kind": "text", "section_path": [s[1] for s in section],
                               "section_locator": locations.get(id(node.parent)), "anchor": None,
                               "text_en": re.sub(r"\s+", " ", str(node)).strip(),
                               "categories": categories([s[1] for s in section], str(node)),
                               "flags": flags_for(str(node)), "links": [], "emphasis": []})
            return
        if node.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level, heading = int(node.name[1]), text_en(node)
            while section and section[-1][0] >= level:
                section.pop()
            section.append((level, heading))
            headings.append(heading)
            blocks.append(dict(common(node, "heading"), level=level))
        elif node.name in ("ul", "ol"):
            def list_tree(container):
                entries = []
                for li in container.find_all("li", recursive=False):
                    entry = common(li, "list_item")
                    entry["children"] = [list_tree(n) for n in li.find_all(["ul", "ol"], recursive=False)]
                    entry["value"] = li.get("value")
                    entries.append(entry)
                return {"ordered": container.name == "ol", "start_original": container.get("start"),
                        "reversed": container.has_attr("reversed"), "items": entries}
            blocks.append(dict(common(node, "list"), structure=list_tree(node)))
        elif node.name == "table":
            table = common(node, "table")
            table["rows"] = []
            for tr in node.find_all("tr"):
                if tr.find_parent("table") is not node:
                    continue
                cells = []
                for cell in tr.find_all(["td", "th"], recursive=False):
                    try:
                        row_span, col_span = int(cell.get("rowspan", 1)), int(cell.get("colspan", 1))
                    except ValueError:
                        issues.append("invalid_table_span")
                        row_span, col_span = None, None
                    cells.append(dict(common(cell, cell.name), rowspan=row_span, colspan=col_span,
                                      rowspan_original=cell.get("rowspan"), colspan_original=cell.get("colspan"),
                                      headers=cell.get("headers"), scope=cell.get("scope"), id=cell.get("id")))
                    if cell.find("table"):
                        issues.append("nested_table_requires_review")
                if not cells:
                    issues.append("table_row_without_cells")
                table["rows"].append({"group": tr.parent.name, "cells": cells})
            table["caption"] = text_en(node.caption) if node.caption else None
            table["cell_count"] = sum(len(row["cells"]) for row in table["rows"])
            source_cells = [n for n in node.find_all(["td", "th"]) if n.find_parent("table") is node]
            if len(source_cells) != table["cell_count"]:
                issues.append("table_cell_loss")
            table["footnotes"] = []
            for a in node.find_all("a", href=True):
                if a["href"].startswith("#"):
                    target = soup.find(id=a["href"][1:]) or soup.find(attrs={"name": a["href"][1:]})
                    if target is None:
                        issues.append("missing_table_footnote:" + a["href"])
                    else:
                        table["footnotes"].append({"href": a["href"], "text_en": text_en(target), "locator": locations.get(id(target))})
            table["html_without_active_content"] = str(node)
            blocks.append(table)
        elif node.name in ("p", "dt", "dd", "blockquote", "pre", "figcaption"):
            blocks.append(common(node, node.name))
        else:
            for child in node.children:
                visit(child)

    visit(content)
    for expected in item.get("sections", []):
        leaf = expected.split(">")[-1].strip().casefold()
        if not any(leaf in heading.casefold() for heading in headings):
            issues.append("expected_section_missing:" + expected)
    if not blocks:
        issues.append("empty_extraction")
    if not notices:
        issues.append("attribution_notice_missing")
    return {"charset": charset, "notices": notices, "blocks": blocks,
            "issues": list(dict.fromkeys(issues)), "title_observed": text_en(title) if title else None}


def rights(item, observations=None):
    return {"scope": "this HTML text only; resource-specific review; no domain-wide license assigned",
            "license": None, "by_use": {key: "pending" for key in USES},
            "basis": {"survey_rights_status": item.get("rights_status"),
                      "archived": "https://ipm.ucanr.edu/GENERAL/copyright.html",
                      "current": "https://ucanr.edu/copyright",
                      "technical_scope": "faithful research extraction only; no translation/editorial changes",
                      "observed_notices": observations or []},
            "restrictions": ["research_only", "exclude_from_release", "retain_copyright_credits",
                             "no_media_acquisition", "no_advice_or_training_approval"],
            "reviewer": None}


def select_items(config, survey):
    items = [p for p in survey["pages"] if p.get("decision") == "candidate_text_acquisition_after_scope_and_rights_check"]
    plan_urls = re.findall(r"\]\((https://[^)]+)\)", config["plan_allowlist_text"])
    if len(items) != 21 or len(config["allowlist"]) != 21 or len(set(config["allowlist"])) != 21:
        raise ValueError("Exactly 21 unique corpus URLs required")
    if {p["final_url"] for p in items} != set(config["allowlist"]) or set(plan_urls) != set(config["allowlist"]):
        raise ValueError("Plan/config/inventory URL sets differ")
    if len({p["source_id"] for p in items}) != 21:
        raise ValueError("Duplicate corpus source IDs")
    by_url = {p["final_url"]: p for p in items}
    return [by_url[url] for url in config["allowlist"]]


def protected(project, root):
    rows = []
    roots = [root / "raw", root / "processed", root / "reports", project / "planning", project / "_bmad", project / "_bmad-output"]
    paths = [project / "AGENTS.md"]
    for scope in roots:
        paths.extend(p for p in scope.rglob("*") if p.is_file()
                     and not ("uc-ipm-tomato" in p.parts and "ucipm-20261014-v1" not in p.parts))
    for path in sorted(set(paths)):
        stat = path.stat()
        row = {"file": path.relative_to(project).as_posix(), "bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}
        if ("raw" not in path.parts and "processed" not in path.parts) or "plantexpert" in path.parts:
            row["sha256"] = digest(path)
        rows.append(row)
    return rows


def derive(project, config, items, rows, raw, processed, report):
    records, queue = [], []
    transformations = []
    for item, row in zip(items, rows):
        row["rights"] = rights(item)
        row["processing"] = "not_applicable"
        row["flags"] = ["research_only", "exclude_from_release"]
        row["review"] = {"domain": "pending", "translation": "not_translated", "reviewer": None,
                         "display_allowed": False, "safe_for_advice": False, "ready_for_training": False}
        if row.get("snapshot_file"):
            path = raw / row["snapshot_file"]
            if digest(path) != row["snapshot_sha256"]:
                raise ValueError("Raw snapshot hash mismatch")
            row["processing"] = "processing_pending"
            try:
                parsed = extract(path.read_bytes(), item, row)
                row["charset"] = parsed["charset"]
                row["rights"] = rights(item, parsed["notices"])
                permitted = config.get("rights_by_item", {}).get(item["source_id"], {})
                # An explicit evidence record is required; being public or an educational project is insufficient.
                for use, decision in permitted.items():
                    if use in USES and decision.get("status") == "conditional_allowed" and decision.get("evidence_url"):
                        row["rights"]["by_use"][use] = decision["status"]
                        row["rights"]["basis"][use] = decision
                issues = parsed["issues"]
                if row["rights"]["by_use"]["technical_processing"] != "conditional_allowed":
                    issues.append("technical_processing_rights_pending")
                for issue in issues:
                    queue.append({"source_id": item["source_id"], "url": row["final_url"], "reason": issue, "reviewer": None, "status": "pending"})
                if "technical_processing_rights_pending" not in issues:
                    record = {"schema_version": "ucipm-research-1.0", "record_id": item["source_id"],
                              "source_id": item["source_id"], "publication_id": item.get("publication_id"),
                              "document_part": urlsplit(item["final_url"]).path, "URL": item["final_url"],
                              "title": item["title"], "authors": item.get("authors", []),
                              "authors_scope": item.get("authors_scope"), "credits": parsed["notices"],
                              "accessed_at": row["accessed_at"], "updated_original": item.get("text_updated_original"),
                              "updated_basis": "prior_survey; not replaced with HTTP/footer date", "parsed_date": None,
                              "snapshot_sha256": row["snapshot_sha256"],
                              "source": {"file": path.relative_to(project).as_posix(), "sha256": row["snapshot_sha256"]},
                              "text_en": "\n".join(b["text_en"] for b in parsed["blocks"]),
                              "section_locator": "per-block original DOM locator", "blocks": parsed["blocks"],
                              "context": {"geography": "California", "role": item["role"],
                                          "production_system": "garden/general hosts" if "home-and-landscape" in item["final_url"] else "California agriculture; page-specific applicability pending",
                                          "growth_stage": None, "cultivar": None, "soil": None},
                              "rights": row["rights"], "flags": row["flags"], "review": row["review"],
                              "transformation_log": ["strict charset decoding", "remove active content/chrome after collecting notices",
                                                     "collapse whitespace only; no translation or knowledge editing", "retain list/table/link/emphasis structure"],
                              "processing": "failed" if issues else "cleaned_technical"}
                    name = item["source_id"].replace(":", "-") + ".json"
                    write_json(processed / name, record)
                    row["processed_file"] = name
                    row["processing"] = record["processing"]
                    records.append(record)
                    transformations.append({"source_id": item["source_id"], "snapshot_sha256": row["snapshot_sha256"],
                                            "parser": PARSER_VERSION, "actions": record["transformation_log"]})
            except (UnicodeError, LookupError, ValueError) as error:
                row["processing"] = "failed"
                queue.append({"source_id": item["source_id"], "reason": str(error), "status": "pending", "reviewer": None})
        else:
            queue.append({"source_id": item["source_id"], "url": item["final_url"],
                          "reason": row.get("reason", "no_snapshot"), "status": "pending", "reviewer": None})
        if item.get("text_updated_original"):
            queue.append({"source_id": item["source_id"], "reason": "date_original_preserved_unparsed", "status": "pending", "reviewer": None})
    with local(project, config["coverage"]).open(encoding="utf-8-sig", newline="") as stream:
        mapping = list(csv.DictReader(stream))
    base_mapping = load(local(project, config["integration"]) / "mapping.json")
    base_by_label = {row["label_original"]: row for row in base_mapping}
    for mapping_row in mapping:
        if base_by_label[mapping_row["label_original"]]["canonical_condition_id"] != mapping_row["canonical_condition_id"]:
            raise ValueError("Canonical condition changed")
        mapping_row.update(domain_review="pending", reviewer=None, display_allowed=False, safe_for_advice=False,
                           source_reference_scope="survey metadata includes rejected comparisons; only snapshot_evidence carries acquired text provenance; no identity or image-label approval",
                           snapshot_evidence=[{"source_id": r["source_id"], "snapshot_sha256": r.get("snapshot_sha256"),
                                               "acquisition": r["acquisition"], "processing": r["processing"]} for r in rows
                                              if r.get("snapshot_sha256") is not None
                                              and r["original_url"] in mapping_row["uc_ipm_urls"].split(" | ")
                                              and next(i for i in items if i["source_id"] == r["source_id"])["role"] != "index"])
    sample = load(local(project, config["inventory"]))["claim_sample"]
    ledger = {c["claim_id"]: c for c in load(local(project, config["integration"]) / "claim-ledger.json")}
    for claim in sample:
        old = ledger[claim["claim_id"]]
        if claim["text_en"] != old["text_en"] or claim["canonical_condition_id"] != old["canonical_condition_id"]:
            raise ValueError("Claim identity/text differs from original ledger")
        claim.update(current_run_check="not_rechecked_without_snapshot", domain_review="pending", reviewer=None,
                     display_allowed=False, safe_for_advice=False, original_source_sha256=old["source_sha256"],
                     original_card_sha256=old["card_sha256"], new_evidence=[])
    write_json(processed / "mapping-sidecar.json", mapping)
    write_json(processed / "claim-evidence-sidecar.json", sample)
    write_json(report / "review-queue.json", queue)
    write_json(report / "transformation-log.json", transformations)
    write_json(report / "attribution-rights-ledger.json", [{"source_id": r["source_id"], "authors": item.get("authors", []),
                                                             "authors_basis": "prior survey; current resource not verified unless notices present",
                                                             "rights": r["rights"], "review": r["review"]} for item, r in zip(items, rows)])
    return records


def preflight(fetcher, config, raw):
    entries = []
    urls = set(config["preflight_urls"])
    for url in config["preflight_urls"]:
        is_robot = url.endswith("robots.txt")
        meta, body = fetcher.fetch(url, urls, robots=False, text=is_robot)
        entries.append(meta)
        if body is None:
            raise StopBatch("preflight_incomplete", {"url": url, "entries": entries})
        name = "preflight-" + str(len(entries)) + (".txt" if is_robot else ".html")
        (raw / name).write_bytes(body)
        meta["snapshot_file"] = name
        if is_robot:
            fetcher.robot_text[urlsplit(url).netloc] = body.decode("utf-8", "strict")
    return {"accessed_at": now(), "batch_stop": False, "entries": entries}


def seal(raw, processed, report):
    return [{"scope": scope, "file": p.relative_to(folder).as_posix(), "sha256": digest(p)}
            for scope, folder in (("raw", raw), ("processed", processed), ("report", report))
            for p in sorted(folder.rglob("*")) if p.is_file() and p.name != "artifact-seal.json"]


def run(config_path, project, run_id, blocked_preflight=None, live=False, transform_only=False):
    project = project.resolve()
    config = load(config_path)
    if not (config["delay_seconds"] >= 5 and 0 < config["timeout_seconds"] <= 30
            and 0 < config["item_limit_bytes"] <= 2 * 1024 * 1024
            and 0 < config["batch_limit_bytes"] <= 50 * 1024 * 1024):
        raise ValueError("Config may tighten but cannot relax acquisition limits")
    if not re.fullmatch(r"ucipm-[a-z0-9-]+", run_id):
        raise ValueError("Unsafe run ID")
    root = local(project, config["dataset_root"])
    survey = load(local(project, config["inventory"]))
    config["plan_allowlist_text"] = local(project, config["plan"]).read_text(encoding="utf-8").split("## 6.", 1)[1].split("### Điều kiện", 1)[0]
    items = select_items(config, survey)
    raw, processed, report = [root / scope / "uc-ipm-tomato" / run_id for scope in ("raw", "processed", "reports")]
    input_hash = fingerprint({"config": config, "inventory": digest(local(project, config["inventory"])),
                              "coverage": digest(local(project, config["coverage"])),
                              "integration": {n: digest(local(project, config["integration"]) / n) for n in ("mapping.json", "claim-ledger.json")},
                              "parser": digest(Path(__file__)),
                              "schema": digest(config_path.with_name("ucipm-schema.json")),
                              "helper": digest(Path(__file__).with_name("clean_plantexpert.py")),
                              "blocked_preflight": digest(blocked_preflight) if blocked_preflight else None})
    if (report / "artifact-seal.json").exists():
        if load(report / "checkpoint.json")["input_hash"] != input_hash:
            raise ValueError("Input changed; use new run")
        if load(report / "artifact-seal.json") != seal(raw, processed, report):
            raise ValueError("Sealed artifacts changed")
        if transform_only:
            before = {p.name: digest(p) for p in raw.glob("*") if p.is_file()}
            with tempfile.TemporaryDirectory(prefix="ucipm-offline-") as directory:
                temp_processed, temp_report = Path(directory) / "processed", Path(directory) / "reports"
                temp_processed.mkdir()
                temp_report.mkdir()
                rows = load(report / "source-processed-manifest.json")
                derive(project, config, items, rows, raw, temp_processed, temp_report)
                for path in temp_processed.glob("*"):
                    if digest(path) != digest(processed / path.name):
                        raise ValueError("Offline derivative mismatch: " + path.name)
                for path in temp_report.glob("*"):
                    if digest(path) != digest(report / path.name):
                        raise ValueError("Offline report mismatch: " + path.name)
            if before != {p.name: digest(p) for p in raw.glob("*") if p.is_file()}:
                raise ValueError("Raw mutated")
        return {"run": run_id, "reused": True, "offline_transform_check": transform_only,
                "counts": load(report / "summary.json")["counts"]}
    if any(folder.exists() for folder in (raw, processed, report)):
        raise ValueError("Unsealed run exists; inspect checkpoint, use new version")
    if not live and not blocked_preflight:
        raise ValueError("Choose live acquisition or record an observed blocking preflight")
    for folder in (raw, processed, report):
        folder.mkdir(parents=True)
    baseline = protected(project, root)
    write_json(report / "preservation-before.json", baseline)
    write_json(report / "registry-before.json", load(root / "dataset-registry.json"))
    write_json(report / "config.json", config)
    rows = [{"source_id": item["source_id"], "original_url": item["final_url"], "final_url": None,
             "accessed_at": None, "http_status": None, "snapshot_sha256": None, "snapshot_file": None,
             "bytes": None, "acquisition": "not_attempted_batch_stopped", "reason": "preflight_blocked"} for item in items]
    fetcher, stop = Fetcher(config), None
    write_json(report / "checkpoint.json", {"input_hash": input_hash, "status": "started", "rows": rows})
    if blocked_preflight:
        evidence = load(blocked_preflight)
        if evidence.get("batch_stop") is not True or evidence.get("blocker", {}).get("http_status") not in (403, 429):
            raise ValueError("Only an observed blocking receipt can replace network preflight")
        stop = evidence["blocker"]
    else:
        evidence = {"entries": []}
        try:
            evidence = preflight(fetcher, config, raw)
            for item, row in zip(items, rows):
                permission = config.get("rights_by_item", {}).get(item["source_id"], {}).get("research_copy", {})
                if permission.get("status") != "conditional_allowed" or not permission.get("evidence_url"):
                    row.update(acquisition="metadata_only", reason="research_copy_rights_pending")
                    continue
                try:
                    meta, body = fetcher.fetch(item["final_url"], set(config["allowlist"]))
                    row.update(meta)
                    if body is not None:
                        name = item["source_id"].replace(":", "-") + ".html"
                        (raw / name).write_bytes(body)
                        row["snapshot_file"] = name
                        row["reason"] = "snapshot_retained"
                except StopBatch as error:
                    row.update(error.metadata, acquisition="blocked", reason=error.reason)
                    raise
                write_json(report / "checkpoint.json", {"input_hash": input_hash, "status": "acquiring", "rows": rows})
        except StopBatch as error:
            stop = dict(error.metadata, reason=error.reason)
            evidence.update(batch_stop=True, blocker=stop)
    write_json(report / "preflight.json", evidence)
    write_json(report / "request-log.json", fetcher.events)
    hashes_before = {p.name: digest(p) for p in raw.glob("*") if p.is_file()}
    records = derive(project, config, items, rows, raw, processed, report)
    hashes_after = {p.name: digest(p) for p in raw.glob("*") if p.is_file()}
    if hashes_before != hashes_after:
        raise ValueError("Raw mutation during extraction")
    write_json(report / "source-processed-manifest.json", rows)
    schema = load(config_path.with_name("ucipm-schema.json"))
    import jsonschema
    for record in records:
        jsonschema.validate(record, schema)
        if record["source_id"] != record["record_id"] or record["source"]["sha256"] != record["snapshot_sha256"]:
            raise ValueError("Provenance/identity mismatch")
    write_json(report / "schema.json", schema)
    after = protected(project, root)
    write_json(report / "preservation-after.json", after)
    if baseline != after:
        raise ValueError("Protected old dataset/report/planning files changed")
    counts = {"acquisition": dict(Counter(r["acquisition"] for r in rows)),
              "processing": dict(Counter(r["processing"] for r in rows))}
    summary = {"run": run_id, "generated_at": now(), "status": "blocked" if stop else "research_only_review_pending",
               "blocker": stop, "counts": counts, "corpus_items": 21, "processed_documents": len(records),
               "claim_sample": 12, "full_172_claim_review": False, "parser_live_validated": bool(records),
               "preservation": {"stat_files": len(after), "hash_files": sum("sha256" in r for r in after),
                                "media_rehashed": False, "raw_hashes_before": hashes_before, "raw_hashes_after": hashes_after}}
    write_json(report / "summary.json", summary)
    dictionary = {
        "schema_version": "ucipm-research-1.0", "parser": PARSER_VERSION,
        "source_id": "stable survey source ID; publication/part separate; representations are not independent votes",
        "snapshot_sha256": "SHA-256 of actual HTML bytes only; null when no snapshot; policy preflight not corpus",
        "section_locator": "DOM CSS nth-of-type path before chrome removal; anchor retained when present",
        "text_en": "original English; whitespace normalization only; no scientific/units/negation editing",
        "blocks": "headings, paragraphs, nested ordered/unordered lists, table rows/cells/spans/header IDs/footnotes and links",
        "updated_original": "prior survey string with explicit basis; parsed_date null; never HTTP Last-Modified/footer year",
        "rights": "five purpose-specific statuses; no generic domain license; resource evidence required",
        "context": "California and surveyed role; field/garden scope differs; missing inputs not inferred from labels",
        "review": "domain pending; translation not_translated; reviewer null; display/advice/training false",
        "processing": "cleaned_technical only after structural/schema checks and processing rights; no advice-ready implication",
        "acquisition": "downloaded/reused/metadata_only/blocked/not_attempted_batch_stopped; mutually exclusive per corpus item",
        "flags": "overlapping indicators; never added to resource counts"
    }
    write_json(report / "data-dictionary.json", dictionary)
    command = f"python scripts/data/collect_ucipm.py --run {run_id}"
    if blocked_preflight:
        command += " --blocked-preflight " + str(blocked_preflight).replace("\\", "/")
    (report / "README.md").write_text(
        f"# UC IPM bounded research run {run_id}\n\n"
        f"Status: **{summary['status']}**. Corpus: 21 selected HTML items. Counts: `{json.dumps(counts)}`.\n\n"
        f"Blocker: `{json.dumps(stop, ensure_ascii=False)}`. No corpus request after preflight stop.\n\n"
        "Snapshot bytes remain immutable and exclude media. This run has no distribution, translation, advice or training approval. "
        "All original datasets, integration mapping/ledger/class order, survey and policies are preserved. "
        "See preservation-before/after.json: file list/size/mtime plus scoped control and PlantExpert hashes; images are not rehashed.\n\n"
        "Mapping sidecar keeps 4 exact disease pages, 2 broad groups, Healthy care and 3 gaps distinct. "
        "TMV/ToMV not synonyms; spider mite not russet mite; Gray Mold does not replace Leaf Mold; Early Blight does not replace Target Spot. "
        "Claim sidecar retains only 12 previously surveyed examples and conflicts; no fresh source-check without a snapshot, no full review of 172 claims.\n\n"
        "## Windows commands (project root)\n\n```powershell\n"
        f"{command}\n{command} --transform-only\n"
        "python -m unittest discover -s scripts/data -p test_collect_ucipm.py -v\n```\n\n"
        "Same sealed input/parser reuses artifacts without network. Changed input/parser requires a new run. "
        "A future live run uses --live with a new run ID and checks current robots/terms first; it never bypasses 403/CAPTCHA/429. "
        "Per-item rights_by_item decisions need evidence_url and conditional_allowed for research_copy; technical_processing has a separate gate. "
        "Empty rights decisions retain metadata, never imply a blanket CC license.\n\n"
        "Dependencies: existing requests, beautifulsoup4 and jsonschema; standard unittest. No install, model/API translation or product dependency. "
        "Parser live layout remains unverified when corpus snapshots are absent. UI e2e is not a Python CLI test; e2e.config.ts/mts absent, no UI flow changed.\n",
        encoding="utf-8")
    write_json(report / "checkpoint.json", {"input_hash": input_hash, "status": summary["status"], "blocker": stop, "rows": rows})
    write_json(report / "artifact-seal.json", seal(raw, processed, report))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("ucipm-config.json"))
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--run", required=True)
    parser.add_argument("--blocked-preflight", type=Path)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--transform-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.project, args.run, args.blocked_preflight,
                         args.live, args.transform_only), indent=2, ensure_ascii=False))
