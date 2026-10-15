"""Bounded report checks; no crawler, cleaning, product tests or data writes."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[5]
DATA = PROJECT / "data/TomatoAI/data"


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique)


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def protected():
    roots = [DATA / "raw", DATA / "processed", DATA / "reports/integration",
             PROJECT / "planning", PROJECT / "_bmad", PROJECT / "_bmad-output"]
    paths = [DATA / "dataset-registry.json", PROJECT / "AGENTS.md"]
    for root in roots:
        paths.extend(p for p in root.rglob("*") if p.is_file())
    rows = []
    for path in sorted(set(paths)):
        stat = path.stat()
        row = [path.relative_to(PROJECT).as_posix(), stat.st_size, stat.st_mtime_ns]
        # Hash small control/review/planning files; media bytes are not rehashed.
        if "raw" not in path.parts and "processed" not in path.parts:
            row.append(hashlib.sha256(path.read_bytes()).hexdigest())
        rows.append(row)
    return rows


class Index(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.heading = None
        self.heading_text = ""
        self.group = ""
        self.link = None
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("h1", "h2", "h3"):
            self.heading, self.heading_text = tag, ""
        if self.active and tag == "a" and attrs.get("href"):
            self.link = [attrs["href"], "", self.group]

    def handle_data(self, data):
        if self.active and data.strip() == "Feedback":
            self.active = False
        if self.heading:
            self.heading_text += data
        if self.link:
            self.link[1] += data

    def handle_endtag(self, tag):
        if tag == self.heading:
            title = " ".join(self.heading_text.split())
            if self.heading == "h1" and title == "Tomato":
                self.active = True
            if self.active and self.heading == "h2":
                self.group = title
            if self.active and title == "Publication Information":
                self.group = title
            if title == "Feedback":
                self.active = False
            self.heading = None
        if tag == "a" and self.link:
            self.link[1] = " ".join(self.link[1].split())
            if self.link[1]:
                self.links.append(self.link)
            self.link = None


def verify():
    inventory = load(HERE / "source-inventory.json")
    rows = list(csv.DictReader((HERE / "coverage-matrix.csv").open(encoding="utf-8-sig", newline="")))
    registry = load(DATA / "dataset-registry.json")
    manifest = DATA / registry["datasets"]["PlantVillage"]["processed"] / "manifest.csv"
    counts = Counter()
    codes = {}
    with manifest.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            counts[row["label_original"]] += 1
            codes.setdefault(row["label_original"], set()).add(row["status_code"])
    assert len(rows) == len(counts) == 10
    assert set(counts) == {r["label_original"] for r in rows}
    assert len({r["canonical_condition_id"] for r in rows}) == 10
    for row in rows:
        assert codes[row["label_original"]] == {row["canonical_condition_id"]}
        assert int(row["manifest_records"]) == counts[row["label_original"]]
    mapping = {r["label_original"]: r for r in load(DATA / "reports/integration/ir-20261014-v1/mapping.json")}
    for row in rows:
        assert row["existing_project_mapping"] == mapping[row["label_original"]]["relation"]
        assert row["canonical_condition_id"] == mapping[row["label_original"]]["canonical_condition_id"]
        assert row["project_expert_review"] == "pending" and row["display_allowed"] == "false"
    pages = inventory["pages"]
    assert len({p["source_id"] for p in pages}) == len(pages)
    assert len({p["canonical_url"] for p in pages}) == len(pages)
    known = {p["canonical_url"] for p in pages}
    known_report_urls = {p[k] for p in pages for k in ("original_url", "canonical_url", "final_url") if p.get(k)}
    for page in pages:
        assert urlparse(page["canonical_url"]).scheme in {"https", "http"}
        assert "//" not in urlparse(page["canonical_url"]).path
        assert page["snapshot_sha256"] is None
        if page["read_depth"] == "not_opened":
            assert page["final_url"] is None and page["access"]["status"] == "not_opened"
    for row in rows:
        assert all(u in known for u in row["uc_ipm_urls"].split(" | ") if u)
    claims = inventory["claim_sample"]
    ledger = {c["claim_id"]: c for c in load(DATA / "reports/integration/ir-20261014-v1/claim-ledger.json")}
    assert len(claims) == 12 and len({c["claim_id"] for c in claims}) == len(claims)
    for claim in claims:
        assert claim["text_en"] == ledger[claim["claim_id"]]["text_en"]
        assert claim["original_pointer"] == ledger[claim["claim_id"]]["pointer"]
        assert claim["canonical_condition_id"] == ledger[claim["claim_id"]]["canonical_condition_id"]
        assert claim["card_id"] == ledger[claim["claim_id"]]["card_id"]
        assert claim["existing_source_check"] == ledger[claim["claim_id"]]["source_check"]
        assert claim["existing_evidence"] == ledger[claim["claim_id"]]["evidence"]
        assert set(claim["uc_ipm_urls"]) <= known
        assert claim["display_allowed"] is False
        assert claim["domain_review"] == "pending" and claim["translation_review"] == "not_translated"
    assert inventory["counts"]["existing_ledger"] == dict(Counter(c["source_check"] for c in ledger.values()))
    assert inventory["counts"]["deep_content_pages"] == sum(p["read_depth"] == "deep" for p in pages)
    assert inventory["counts"]["deep_content_pages"] <= 30
    depths = Counter(p["read_depth"] for p in pages)
    assert depths == {"deep": 25, "metadata_only": 1, "rights": 7, "not_opened": 95}
    assert inventory["counts"]["unique_nonrights_content_pages_read"] == depths["deep"] + depths["metadata_only"]
    assert inventory["counts"]["unique_pages_read_total"] == depths["deep"] + depths["metadata_only"] + depths["rights"]
    assert inventory["counts"]["unopened_toc_links"] == depths["not_opened"]
    assert sum(p["source_id"].startswith("ucipm:toc:") for p in pages) == 115
    assert sum(inventory["counts"]["toc_groups"].values()) == 115
    selected = {p["canonical_url"] for p in pages if p["decision"] == "candidate_text_acquisition_after_scope_and_rights_check"}
    assert len(selected) == inventory["counts"]["future_html_allowlist"] == 21
    assert all(p["read_depth"] == "deep" for p in pages if p["canonical_url"] in selected)
    plan = (HERE / "acquisition-cleaning-plan.md").read_text(encoding="utf-8")
    allowlist_section = plan.split("## 6. Allowlist cụ thể", 1)[1].split("### Điều kiện", 1)[0]
    planned = re.findall(r"\]\((https?://[^)]+)\)", allowlist_section)
    assert len(planned) == len(selected) and set(planned) == selected
    baseline = load(HERE / "integrity-baseline.json")
    assert protected() == baseline["files"], "protected inputs changed"
    for filename in ("README.md", "acquisition-cleaning-plan.md"):
        text = (HERE / filename).read_text(encoding="utf-8")
        assert "\ufffd" not in text and text.strip()
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if urlparse(link).scheme in {"https", "http"}:
                assert link in known_report_urls, f"uncatalogued report URL: {link}"
            else:
                target = (HERE / urldefrag(link)[0]).resolve()
                # This run creates the verification artifact after all checks pass.
                assert target.exists() or target == HERE / "verification.json", f"missing local report link: {link}"
    result = {"verified_utc": datetime.now(timezone.utc).isoformat(), "passed": True,
              "classifier_classes": len(counts), "manifest_records": sum(counts.values()),
              "coverage_rows": len(rows), "claim_sample": len(claims), "inventory_pages": len(pages),
              "deep_content_pages": inventory["counts"]["deep_content_pages"],
              "nonrights_pages_read": depths["deep"] + depths["metadata_only"],
              "rights_pages_read": depths["rights"], "unopened_toc_links": depths["not_opened"],
              "future_html_allowlist": len(selected), "local_markdown_links_checked": True,
              "protected_files_stat_checked": len(baseline["files"]),
              "control_files_sha256_checked": sum(len(r) == 4 for r in baseline["files"]),
              "media_byte_hash_recheck": False, "network_url_recheck": False,
              "scope": "metadata/schema/IDs/references/protected local inputs; no product or pipeline tests"}
    save(HERE / "verification.json", result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["baseline", "index", "verify"])
    action = parser.parse_args().action
    if action == "baseline":
        path = HERE / "integrity-baseline.json"
        if path.exists():
            raise FileExistsError(path)
        save(path, {"created_utc": datetime.now(timezone.utc).isoformat(), "files": protected()})
        print("protected baseline recorded")
    elif action == "index":
        url = "https://ipm.ucanr.edu/agriculture/tomato/"
        request = Request(url, headers={"User-Agent": "TomatoAI-SourceSurvey/1.0 (academic evaluation; single index request)"})
        with urlopen(request, timeout=30) as response:
            html = response.read().decode(response.headers.get_content_charset() or "utf-8")
            index = Index()
            index.feed(html)
            links = [{"title": title, "url": urldefrag(urljoin(url, href))[0], "group": group}
                     for href, title, group in index.links]
            save(HERE / "index-metadata.json", {"url": url, "final_url": response.url,
                 "status": response.status, "accessed_utc": datetime.now(timezone.utc).isoformat(), "links": links})
            print(json.dumps({"status": response.status, "links": len(links), "groups": dict(Counter(l["group"] for l in links))}))
    else:
        verify()
