"""Offline regression fixtures only; these tests never contact UC IPM."""
import copy
import gzip
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import jsonschema
import requests

import collect_ucipm as uc

HERE = Path(__file__).parent
PROJECT = HERE.resolve().parents[1]
CONFIG = uc.load(HERE / "ucipm-config.json")
URL = CONFIG["allowlist"][0]
HTML = b'''<!doctype html><html><head><title>Introduction</title></head><body>
<nav>Navigation should vanish</nav><main><h1>Introduction</h1><h2>Management</h2>
<p>If possible, do not wet leaves. <em>Phytophthora infestans</em> might occur at 12/13.</p>
<ol start="3"><li>First observation<ul><li>Conditional nested item</li></ul></li><li>Second observation</li></ol>
<h3>Cultural Control</h3><p>Organic copper is chemical; do not use 10% bleach without context.</p>
<table><caption>Rates and restrictions</caption><thead><tr><th rowspan="2" id="a">Product</th><th colspan="2">Limits</th></tr>
<tr><th id="r">Rate</th><th>PHI</th></tr></thead><tbody><tr><td headers="a">Copper</td>
<td headers="r">0.5 lb/acre <a href="#fn1"><sup>1</sup></a></td><td>0</td></tr></tbody></table>
<p id="fn1">1. If registered, follow the label.</p><h2>Authors and Credits</h2><p>Fixture author, SYNTHETIC.</p>
<iframe>Tracker</iframe><script>bad()</script><form>feedback</form>
</main><footer>Copyright 2026 Regents. SYNTHETIC fixture; no real permission.</footer></body></html>'''


class Clock:
    def __init__(self):
        self.value = 0
        self.sleeps = []

    def __call__(self):
        return self.value

    def sleep(self, value):
        self.sleeps.append(value)
        self.value += value


class Response:
    def __init__(self, status=200, body=HTML, headers=None, chunks=None):
        self.status_code = status
        self.body = body
        self.headers = headers or {"Content-Type": "text/html; charset=utf-8"}
        self.chunks = chunks
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def iter_content(self, chunk_size):
        yield from self.chunks if self.chunks is not None else [self.body]


class Session:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def fetcher(responses, **limits):
    config = dict(CONFIG, **limits)
    clock, session = Clock(), Session(responses)
    client = uc.Fetcher(config, session, clock, clock.sleep)
    client.robot_text["ipm.ucanr.edu"] = "User-agent: *\nDisallow: /PDF\nAllow: /PDF/PUBS\n"
    return client, session, clock


class CollectorTests(unittest.TestCase):
    def test_plan_and_inventory_exactly_21(self):
        survey = uc.load(PROJECT / CONFIG["inventory"])
        config = dict(CONFIG, plan_allowlist_text=(PROJECT / CONFIG["plan"]).read_text(encoding="utf-8").split("## 6.")[1].split("### Điều kiện")[0])
        self.assertEqual(len(uc.select_items(config, survey)), 21)
        config["allowlist"] = config["allowlist"][:-1]
        with self.assertRaisesRegex(ValueError, "21"):
            uc.select_items(config, survey)

    def test_robots_longest_allow_tie_and_case(self):
        text = "User-agent: *\nDisallow: /PDF\nAllow: /PDF/PUBS\nDisallow: /same\nAllow: /same\n"
        self.assertFalse(uc.robots_allowed(text, "https://ipm.ucanr.edu/PDF/a", "TomatoAI"))
        self.assertTrue(uc.robots_allowed(text, "https://ipm.ucanr.edu/PDF/PUBS/a", "TomatoAI"))
        self.assertTrue(uc.robots_allowed(text, "https://ipm.ucanr.edu/pdf/a", "TomatoAI"))
        self.assertTrue(uc.robots_allowed(text, "https://ipm.ucanr.edu/same", "TomatoAI"))

    def test_robots_specific_agent_and_wildcard(self):
        text = "User-agent: *\nDisallow: /\nUser-agent: TomatoAI\nDisallow: /private/*\nAllow: /public$\n"
        self.assertTrue(uc.robots_allowed(text, "https://ipm.ucanr.edu/public", "TomatoAI-AcademicSourceSurvey"))
        self.assertFalse(uc.robots_allowed(text, "https://ipm.ucanr.edu/private/a", "TomatoAI-AcademicSourceSurvey"))
        self.assertFalse(uc.robots_allowed(text, "https://ipm.ucanr.edu/public", "OtherBot"))

    def test_robots_denied_or_unverified_no_request(self):
        client, session, _ = fetcher([])
        client.robot_text["ipm.ucanr.edu"] = "User-agent: *\nDisallow: /"
        with self.assertRaisesRegex(uc.StopBatch, "robots_deny"):
            client.fetch(URL, {URL})
        client.robot_text.clear()
        with self.assertRaisesRegex(uc.StopBatch, "robots_unverified"):
            client.fetch(URL, {URL})
        self.assertEqual(session.calls, [])

    def test_outside_allowlist_never_requested(self):
        client, session, _ = fetcher([])
        with self.assertRaisesRegex(ValueError, "allowlist"):
            client.fetch("https://ipm.ucanr.edu/PDF/a.pdf", {URL})
        self.assertEqual(session.calls, [])

    def test_html_hash_headers_and_request_settings(self):
        response = Response(headers={"Content-Type": "text/html; charset=utf-8", "ETag": "fixture-tag", "Last-Modified": "Wed, 14 Oct 2026 00:00:00 GMT"})
        client, session, _ = fetcher([response])
        meta, data = client.fetch(URL, {URL})
        self.assertEqual(data, HTML)
        self.assertEqual(meta["snapshot_sha256"], hashlib.sha256(HTML).hexdigest())
        self.assertEqual(meta["bytes"], len(HTML))
        self.assertEqual(meta["etag"], "fixture-tag")
        self.assertTrue(meta["accessed_at"].endswith("+00:00"))
        self.assertEqual(session.calls[0][1]["timeout"], 30)
        self.assertFalse(session.calls[0][1]["allow_redirects"])
        self.assertTrue(response.closed)

    def test_cadence_after_completed_request(self):
        client, session, clock = fetcher([Response(), Response()])
        client.fetch(URL, {URL})
        client.fetch(URL, {URL})
        self.assertEqual(clock.sleeps, [5])
        self.assertEqual(len(session.calls), 2)

    def test_decompressed_body_cap(self):
        compressed = gzip.compress(b"x" * 1024)
        response = Response(chunks=[gzip.decompress(compressed)], headers={"Content-Type": "text/html", "Content-Encoding": "gzip"})
        client, _, _ = fetcher([response], item_limit_bytes=100)
        meta, data = client.fetch(URL, {URL})
        self.assertIsNone(data)
        self.assertEqual(meta["reason"], "item_byte_limit")
        self.assertIsNone(meta["snapshot_sha256"])

    def test_batch_limit_stops(self):
        client, _, _ = fetcher([Response(body=b"x" * 50)], batch_limit_bytes=40)
        with self.assertRaisesRegex(uc.StopBatch, "batch_byte_limit"):
            client.fetch(URL, {URL})

    def test_error_media_and_attachment_not_snapshots(self):
        for response, expected in [(Response(404), "http_error"),
                                   (Response(body=b"PDF", headers={"Content-Type": "application/pdf"}), "not_html_or_attachment"),
                                   (Response(headers={"Content-Type": "text/html", "Content-Disposition": "attachment; filename=a.html"}), "not_html_or_attachment"),
                                   (Response(body=b"<html><title>Page not found 404</title></html>"), "error_page"),
                                   (Response(body=b"%PDF-1.0 mislabeled as HTML"), "not_html_payload"),
                                   (Response(body=b""), "empty_body")]:
            with self.subTest(expected=expected):
                client, _, _ = fetcher([response])
                meta, data = client.fetch(URL, {URL})
                self.assertIsNone(data)
                self.assertEqual(meta["reason"], expected)
                self.assertIsNone(meta["snapshot_sha256"])

    def test_403_429_captcha_stop_without_retry(self):
        for response, expected in [(Response(403), "http_403"),
                                   (Response(429, headers={"Retry-After": "3600"}), "http_429"),
                                   (Response(body=b"<html>verify you are human</html>"), "captcha")]:
            client, session, _ = fetcher([response])
            with self.assertRaisesRegex(uc.StopBatch, expected) as caught:
                client.fetch(URL, {URL})
            self.assertEqual(len(session.calls), 1)
            if expected == "http_429":
                self.assertEqual(caught.exception.metadata["retry_after"], "3600")

    def test_redirect_outside_or_cross_host_review(self):
        for destination in ("https://ipm.ucanr.edu/agriculture/tomato/unopened/", "https://evil.example/test"):
            client, session, _ = fetcher([Response(302, headers={"Location": destination})])
            meta, data = client.fetch(URL, {URL, destination} if "evil" in destination else {URL})
            self.assertEqual(meta["reason"], "redirect_review")
            self.assertIsNone(data)
            self.assertEqual(len(session.calls), 1)

    def test_redirect_fragment_same_resource_does_not_fetch_twice(self):
        client, session, _ = fetcher([Response(302, headers={"Location": URL + "#section"})])
        meta, _ = client.fetch(URL, {URL})
        self.assertEqual(meta["reason"], "redirect_limit")
        self.assertEqual(len(session.calls), 1)

    def test_three_hop_limit(self):
        urls = ["https://ipm.ucanr.edu/x" + str(i) for i in range(5)]
        client, session, _ = fetcher([Response(302, headers={"Location": url}) for url in urls[1:]])
        meta, _ = client.fetch(urls[0], set(urls))
        self.assertEqual(meta["reason"], "redirect_limit")
        self.assertEqual(len(session.calls), 4)

    def test_valid_allowlisted_redirect(self):
        destination = CONFIG["allowlist"][1]
        client, session, _ = fetcher([Response(301, headers={"Location": destination}), Response()])
        meta, body = client.fetch(URL, {URL, destination})
        self.assertEqual(meta["final_url"], destination)
        self.assertEqual(meta["original_url"], URL)
        self.assertEqual(meta["redirects"], [URL])
        self.assertEqual(body, HTML)
        self.assertEqual(len(session.calls), 2)

    def test_retry_only_temporary_errors_with_backoff(self):
        client, session, clock = fetcher([requests.Timeout(), Response(503), Response()])
        meta, body = client.fetch(URL, {URL})
        self.assertEqual(meta["acquisition"], "downloaded")
        self.assertEqual(body, HTML)
        self.assertEqual(len(session.calls), 3)
        self.assertTrue(any(10 <= n <= 10.25 for n in clock.sleeps))
        self.assertTrue(any(30 <= n <= 30.25 for n in clock.sleeps))

    def test_exhausted_retries(self):
        client, session, _ = fetcher([Response(500)] * 3)
        meta, body = client.fetch(URL, {URL})
        self.assertEqual(meta["reason"], "http_5xx_exhausted")
        self.assertIsNone(body)
        self.assertEqual(len(session.calls), 3)

    def test_304_requires_verified_real_cache(self):
        client, _, _ = fetcher([Response(304)])
        self.assertEqual(client.fetch(URL, {URL})[0]["reason"], "304_without_cache")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.html"
            path.write_bytes(HTML)
            cache = {"path": path, "snapshot_sha256": uc.digest(path), "content_type": "text/html", "final_url": URL, "etag": "cached"}
            client, session, _ = fetcher([Response(304)])
            meta, body = client.fetch(URL, {URL}, cache)
            self.assertEqual(meta["acquisition"], "reused")
            self.assertEqual(body, HTML)
            self.assertEqual(session.calls[0][1]["headers"]["If-None-Match"], "cached")
            path.write_bytes(b"tampered")
            client, _, _ = fetcher([Response(304)])
            self.assertEqual(client.fetch(URL, {URL}, cache)[0]["reason"], "304_invalid_cache")


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.item = {"title": "Introduction", "sections": ["Introduction", "Authors and Credits", "Management > Cultural Control"]}
        self.meta = {"content_type": "text/html; charset=utf-8", "final_url": URL}

    def test_headings_lists_negation_condition_scientific_name(self):
        parsed = uc.extract(HTML, self.item, self.meta)
        self.assertEqual(parsed["issues"], [])
        body = " ".join(block["text_en"] for block in parsed["blocks"])
        self.assertIn("If possible, do not wet leaves.", body)
        self.assertIn("Phytophthora infestans", body)
        self.assertIn("might occur at 12/13", body)
        self.assertNotIn("bad()", body)
        self.assertNotIn("feedback", body)
        self.assertNotIn("Navigation should vanish", body)
        listing = next(b for b in parsed["blocks"] if b["kind"] == "list")
        self.assertEqual(listing["structure"]["start_original"], "3")
        self.assertTrue(listing["structure"]["ordered"])
        self.assertEqual(len(listing["structure"]["items"]), 2)
        self.assertEqual(listing["structure"]["items"][0]["children"][0]["items"][0]["text_en"], "Conditional nested item")
        paragraph = next(b for b in parsed["blocks"] if "Organic copper" in b["text_en"])
        self.assertIn("chemical", paragraph["flags"])
        self.assertIn("organic_not_nonchemical", paragraph["flags"])
        self.assertEqual(paragraph["section_path"], ["Introduction", "Management", "Cultural Control"])

    def test_table_headers_spans_cells_zero_units_footnotes(self):
        parsed = uc.extract(HTML, self.item, self.meta)
        table = next(b for b in parsed["blocks"] if b["kind"] == "table")
        self.assertEqual(table["cell_count"], 7)
        self.assertEqual(table["rows"][0]["cells"][0]["rowspan"], 2)
        self.assertEqual(table["rows"][0]["cells"][1]["colspan"], 2)
        self.assertEqual(table["rows"][2]["cells"][1]["headers"], ["r"])
        self.assertEqual(table["rows"][2]["cells"][2]["text_en"], "0")
        self.assertIn("0.5 lb/acre", table["rows"][2]["cells"][1]["text_en"])
        self.assertEqual(table["footnotes"][0]["text_en"], "1. If registered, follow the label.")
        self.assertIn("rowspan=", table["html_without_active_content"])

    def test_missing_footnote_section_and_encoding_review(self):
        parsed = uc.extract(HTML.replace(b'id="fn1"', b'id="different"'), self.item, self.meta)
        self.assertIn("missing_table_footnote:#fn1", parsed["issues"])
        parsed = uc.extract(HTML, dict(self.item, sections=["Missing section"]), self.meta)
        self.assertIn("expected_section_missing:Missing section", parsed["issues"])
        with self.assertRaises(UnicodeDecodeError):
            uc.extract(HTML + b"\xff", self.item, self.meta)

    def test_missing_main_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "main_content_missing"):
            uc.extract(b"<html><h1>Introduction</h1></html>", self.item, self.meta)

    def test_third_party_notice_needs_review(self):
        parsed = uc.extract(HTML.replace(b"Copyright 2026", b"Third-party figure used with permission. Copyright 2026"), self.item, self.meta)
        self.assertIn("resource_specific_rights_notice_requires_review", parsed["issues"])

    def test_rights_separate_purposes_no_blanket_license(self):
        rights = uc.rights({"rights_status": "unverified"})
        self.assertEqual(set(rights["by_use"]), set(uc.USES))
        self.assertEqual(set(rights["by_use"].values()), {"pending"})
        self.assertIsNone(rights["license"])
        self.assertIn("exclude_from_release", rights["restrictions"])


class RunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        self.config_path = self.project / "scripts/data/ucipm-config.json"
        self.config_path.parent.mkdir(parents=True)
        uc.write_json(self.config_path, CONFIG)
        (self.config_path.parent / "ucipm-schema.json").write_bytes((HERE / "ucipm-schema.json").read_bytes())
        for key in ("inventory", "coverage", "plan"):
            path = self.project / CONFIG[key]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((PROJECT / CONFIG[key]).read_bytes())
        for name in ("mapping.json", "claim-ledger.json"):
            path = self.project / CONFIG["integration"] / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((PROJECT / CONFIG["integration"] / name).read_bytes())
        root = self.project / CONFIG["dataset_root"]
        root.mkdir(exist_ok=True)
        uc.write_json(root / "dataset-registry.json", {"datasets": {"old": {"current_run": "unchanged"}}})
        (self.project / "AGENTS.md").write_text("fixture instructions")
        old = root / "raw/plantexpert/old.json"
        old.parent.mkdir(parents=True)
        old.write_text("immutable fixture")
        self.receipt = self.project / "blocking.json"
        uc.write_json(self.receipt, {"batch_stop": True, "blocker": {"http_status": 403, "url": "https://ucanr.edu/dept/anr-publishing/permissions"}})
        self.run_id = "ucipm-fixture-1"
        self.report = root / "reports/uc-ipm-tomato" / self.run_id
        self.processed = root / "processed/uc-ipm-tomato" / self.run_id

    def tearDown(self):
        self.temp.cleanup()

    def test_blocked_preflight_all_21_and_idempotency_offline(self):
        with patch.object(requests.Session, "get", side_effect=AssertionError("NETWORK FORBIDDEN")):
            summary = uc.run(self.config_path, self.project, self.run_id, self.receipt)
            self.assertEqual(summary["counts"], {"acquisition": {"not_attempted_batch_stopped": 21}, "processing": {"not_applicable": 21}})
            self.assertEqual(summary["processed_documents"], 0)
            self.assertEqual(uc.load(self.report / "preservation-before.json"), uc.load(self.report / "preservation-after.json"))
            sealed = (self.report / "artifact-seal.json").read_bytes()
            self.assertTrue(uc.run(self.config_path, self.project, self.run_id, self.receipt)["reused"])
            self.assertTrue(uc.run(self.config_path, self.project, self.run_id, self.receipt, transform_only=True)["offline_transform_check"])
            self.assertEqual(sealed, (self.report / "artifact-seal.json").read_bytes())
        rows = uc.load(self.report / "source-processed-manifest.json")
        self.assertEqual(len({r["source_id"] for r in rows}), 21)
        self.assertTrue(all(r["snapshot_sha256"] is None and r["accessed_at"] is None for r in rows))

    def test_sidecar_condition_labels_gaps_and_12_claims_preserved(self):
        uc.run(self.config_path, self.project, self.run_id, self.receipt)
        mapping = uc.load(self.processed / "mapping-sidecar.json")
        self.assertEqual(len(mapping), 10)
        by_id = {r["canonical_condition_id"]: r for r in mapping}
        self.assertEqual(by_id["TOM_MOSAIC"]["existing_project_mapping"], "candidate_pending")
        for name in ("TOM_LEAF_MOLD", "TOM_SEPTORIA", "TOM_TARGET_SPOT"):
            self.assertEqual(by_id[name]["snapshot_evidence"], [])
        # The original survey deliberately lists russet mite as an excluded comparison.
        # Preserve that metadata, but never make it acquired identity evidence.
        self.assertIn("russet", by_id["TOM_SPIDER_MITE"]["uc_ipm_urls"])
        self.assertEqual(by_id["TOM_SPIDER_MITE"]["snapshot_evidence"], [])
        self.assertIn("rejected comparisons", by_id["TOM_SPIDER_MITE"]["source_reference_scope"])
        claims = uc.load(self.processed / "claim-evidence-sidecar.json")
        self.assertEqual(len(claims), 12)
        old = {c["claim_id"]: c for c in uc.load(self.project / CONFIG["integration"] / "claim-ledger.json")}
        for claim in claims:
            self.assertEqual(claim["text_en"], old[claim["claim_id"]]["text_en"])
            self.assertEqual(claim["original_source_sha256"], old[claim["claim_id"]]["source_sha256"])
            self.assertFalse(claim["display_allowed"])
            self.assertEqual(claim["new_evidence"], [])
        self.assertIn("contradicts_vector_assumption", [c["survey_result"] for c in claims])
        self.assertIn("context_conflict_unresolved", [c["survey_result"] for c in claims])

    def test_tamper_seal_and_input_change_refused(self):
        uc.run(self.config_path, self.project, self.run_id, self.receipt)
        original = (self.processed / "mapping-sidecar.json").read_bytes()
        (self.processed / "mapping-sidecar.json").write_text("[]")
        with self.assertRaisesRegex(ValueError, "Sealed artifacts"):
            uc.run(self.config_path, self.project, self.run_id, self.receipt)
        (self.processed / "mapping-sidecar.json").write_bytes(original)
        config = uc.load(self.config_path)
        config["user_agent"] += " new version"
        uc.write_json(self.config_path, config)
        with self.assertRaisesRegex(ValueError, "Input changed"):
            uc.run(self.config_path, self.project, self.run_id, self.receipt)

    def test_no_loosened_limits_or_path_escape(self):
        config = uc.load(self.config_path)
        config["delay_seconds"] = 0
        uc.write_json(self.config_path, config)
        with self.assertRaisesRegex(ValueError, "cannot relax"):
            uc.run(self.config_path, self.project, self.run_id, self.receipt)
        with self.assertRaisesRegex(ValueError, "below project"):
            uc.local(self.project, "../outside")

    def test_synthetic_download_transform_replay_schema_raw_immutable(self):
        config = uc.load(self.config_path)
        source_id = uc.load(self.project / CONFIG["inventory"])["pages"][0]["source_id"]
        config["rights_by_item"] = {source_id: {use: {"status": "conditional_allowed", "evidence_url": "https://example.invalid/SYNTHETIC-PERMISSION"} for use in ("research_copy", "technical_processing")}}
        uc.write_json(self.config_path, config)

        def fake_preflight(client, configuration, raw):
            client.robot_text["ipm.ucanr.edu"] = "User-agent: *\nAllow: /"
            return {"batch_stop": False, "entries": [], "fixture": "SYNTHETIC; no real rights"}

        with patch.object(uc, "preflight", side_effect=fake_preflight), patch.object(requests.Session, "get", return_value=Response()):
            summary = uc.run(self.config_path, self.project, self.run_id, live=True)
        self.assertEqual(summary["counts"]["acquisition"], {"downloaded": 1, "metadata_only": 20})
        self.assertEqual(summary["counts"]["processing"], {"cleaned_technical": 1, "not_applicable": 20})
        records = [p for p in self.processed.glob("ucipm-*.json")]
        self.assertEqual(len(records), 1)
        record = uc.load(records[0])
        self.assertEqual(record["updated_original"], "12/13")
        self.assertIsNone(record["parsed_date"])
        self.assertFalse(record["review"]["safe_for_advice"])
        jsonschema.validate(record, uc.load(HERE / "ucipm-schema.json"))
        bad = copy.deepcopy(record)
        bad["review"]["display_allowed"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(bad, uc.load(HERE / "ucipm-schema.json"))
        with patch.object(requests.Session, "get", side_effect=AssertionError("NETWORK FORBIDDEN")):
            replay = uc.run(self.config_path, self.project, self.run_id, transform_only=True)
        self.assertTrue(replay["offline_transform_check"])
        self.assertEqual(summary["preservation"]["raw_hashes_before"], summary["preservation"]["raw_hashes_after"])

    def test_429_checkpoint_then_no_other_request(self):
        config = uc.load(self.config_path)
        items = [i for i in uc.load(self.project / CONFIG["inventory"])["pages"] if i.get("decision") == "candidate_text_acquisition_after_scope_and_rights_check"]
        config["rights_by_item"] = {i["source_id"]: {"research_copy": {"status": "conditional_allowed", "evidence_url": "https://example.invalid/SYNTHETIC"}} for i in items}
        uc.write_json(self.config_path, config)

        def fake_preflight(client, configuration, raw):
            client.robot_text["ipm.ucanr.edu"] = "User-agent: *\nAllow: /"
            return {"batch_stop": False}

        with patch.object(uc, "preflight", side_effect=fake_preflight), patch.object(requests.Session, "get", return_value=Response(429, headers={"Retry-After": "Wed, 14 Oct 2026 15:00:00 GMT"})) as request:
            summary = uc.run(self.config_path, self.project, self.run_id, live=True)
        self.assertEqual(request.call_count, 1)
        self.assertEqual(summary["counts"]["acquisition"], {"blocked": 1, "not_attempted_batch_stopped": 20})
        checkpoint = uc.load(self.report / "checkpoint.json")
        self.assertEqual(checkpoint["blocker"]["retry_after"], "Wed, 14 Oct 2026 15:00:00 GMT")

    def test_copy_permission_does_not_imply_processing(self):
        config = uc.load(self.config_path)
        source_id = uc.load(self.project / CONFIG["inventory"])["pages"][0]["source_id"]
        config["rights_by_item"] = {source_id: {"research_copy": {"status": "conditional_allowed", "evidence_url": "https://example.invalid/SYNTHETIC"}}}
        uc.write_json(self.config_path, config)

        def fake_preflight(client, configuration, raw):
            client.robot_text["ipm.ucanr.edu"] = "User-agent: *\nAllow: /"
            return {"batch_stop": False}

        with patch.object(uc, "preflight", side_effect=fake_preflight), patch.object(requests.Session, "get", return_value=Response()):
            summary = uc.run(self.config_path, self.project, self.run_id, live=True)
        self.assertEqual(summary["counts"]["processing"], {"processing_pending": 1, "not_applicable": 20})
        self.assertEqual(summary["processed_documents"], 0)
        self.assertEqual(list(self.processed.glob("ucipm-*.json")), [])
        queue = uc.load(self.report / "review-queue.json")
        self.assertIn("technical_processing_rights_pending", [r["reason"] for r in queue])


if __name__ == "__main__":
    unittest.main()
