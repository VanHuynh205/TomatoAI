"""CLI behavior and independent checks of sealed PlantExpert artifacts.

Fixtures copy a real card into temporary roots; they are never training data.
Production verification requires PLANTEXPERT_REPORT and PLANTEXPERT_PROJECT_ROOT.
"""
import copy
import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
BASE = json.loads((PROJECT / "data/TomatoAI/data/raw/plantexpert/disease_kb/tomato/early_blight.json").read_text(encoding="utf-8"))


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_file(path):
    return json.loads(path.read_text(encoding="utf-8"))


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "data/raw/plantexpert"
        self.cards = self.source / "disease_kb/tomato"
        self.cards.mkdir(parents=True)
        (self.source / "README.md").write_text("source declaration only", encoding="utf-8")
        (self.source / "intake.zip").write_bytes(b"immutable intake archive")
        self.config = json_file(HERE / "plantexpert-config.json")
        self.config.update(source_root="data/raw/plantexpert", processed_root="data/processed/pex", report_root="data/reports/pex", image_label_mapping="labels.json", mapping_basis="basis.md", labels=[self.config["labels"][1]])
        (self.root / "labels.json").write_text(json.dumps({"labels": {"Tomato___Early_blight": "TOM_EARLY_BLIGHT"}}), encoding="utf-8")
        (self.root / "basis.md").write_text("existing draft mapping", encoding="utf-8")
        self.write_card("early_blight.json", BASE)

    def write_card(self, name, card):
        (self.cards / name).write_text(json.dumps(card, ensure_ascii=False), encoding="utf-8")

    def execute(self, ok=True):
        config = self.root / "config.json"
        config.write_text(json.dumps(self.config, ensure_ascii=False), encoding="utf-8")
        result = subprocess.run([sys.executable, str(HERE / "clean_plantexpert.py"), "--config", str(config), "--project-root", str(self.root)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode == 0, ok, result.stderr)
        if not ok:
            return result
        event = json.loads(result.stdout.splitlines()[-1])
        report = Path(event["report"])
        summary = json_file(report / "summary.json")
        processed = self.root / self.config["processed_root"] / summary["run_id"]
        rows = [json.loads(line) for line in (processed / "manifest.jsonl").read_text(encoding="utf-8").splitlines()]
        return event, report, processed, rows

    def test_provenance_en_and_zero_empty_values_are_preserved(self):
        card = copy.deepcopy(BASE)
        card["environmental_risk"]["leaf_wetness_hours_threshold"] = 0
        card["condition"]["scientific_name"] = None
        self.write_card("early_blight.json", card)
        before = {p.relative_to(self.source).as_posix(): p.read_bytes() for p in self.source.rglob("*") if p.is_file()}
        _, report, processed, rows = self.execute()
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["schema_ok"])
        envelope = json_file(processed / rows[0]["processed_file"])
        self.assertEqual(envelope["content_en"], card)
        self.assertFalse(envelope["review"]["safe_for_advice"])
        self.assertFalse(rows[0]["ready_for_training"])
        self.assertEqual({p.relative_to(self.source).as_posix(): p.read_bytes() for p in self.source.rglob("*") if p.is_file()}, before)
        self.assertEqual((processed / rows[0]["raw_copy"]).read_bytes(), before[rows[0]["source_file"]])
        self.assertGreater(json_file(report / "summary.json")["numeric_zero_occurrences_preserved"], 0)

    def test_unicode_nfc_does_not_change_raw_or_keys(self):
        card = copy.deepcopy(BASE)
        card["management"]["notes"] = "cafe\u0301; do not apply 0.5 g without review"
        card["extra_e\u0301"] = "e\u0301"
        self.write_card("early_blight.json", card)
        _, _, processed, rows = self.execute()
        envelope = json_file(processed / rows[0]["processed_file"])
        self.assertEqual(envelope["content_en"]["management"]["notes"], "café; do not apply 0.5 g without review")
        self.assertEqual(envelope["content_en"]["extra_e\u0301"], "é")
        self.assertEqual(len(rows[0]["transformations"]), 2)
        self.assertIn("e\u0301", (processed / rows[0]["raw_copy"]).read_text(encoding="utf-8"))

    def test_malformed_duplicate_keys_nan_overflow_and_encoding_quarantine(self):
        for name, payload in {"duplicate.json": b'{"disease_id":"a","disease_id":"b"}', "nan.json": b'{"x":NaN}', "overflow.json": b'{"x":1e9999}', "broken.json": b'{', "encoding.json": b'\xff\xfe'}.items():
            (self.cards / name).write_bytes(payload)
        _, report, processed, rows = self.execute()
        self.assertEqual(len(rows), 6)
        bad = [r for r in rows if not r["parse_ok"]]
        self.assertEqual(len(bad), 5)
        self.assertEqual(len(json_file(report / "quarantine.json")), 5)
        for row in bad:
            self.assertIsNone(row["processed_file"])
            self.assertEqual((processed / row["raw_copy"]).read_bytes(), (self.source / row["source_file"]).read_bytes())

    def test_missing_field_wrong_type_and_wrong_crop_are_not_schema_ready(self):
        absent = copy.deepcopy(BASE)
        absent.pop("management")
        self.write_card("absent.json", absent)
        wrong = copy.deepcopy(BASE)
        wrong["data_requirements"]["min_resolution_px"] = True
        self.write_card("wrong.json", wrong)
        other = copy.deepcopy(BASE)
        other["crop"]["common_name"] = "apple"
        self.write_card("apple.json", other)
        _, _, _, rows = self.execute()
        self.assertEqual(sum(r["schema_ok"] for r in rows), 1)
        self.assertEqual(sum(r["record_status"] == "quarantined_technical" for r in rows), 3)

    def test_unresolved_reference_and_taxonomy_are_not_auto_corrected(self):
        card = copy.deepcopy(BASE)
        card["lookalikes"][0]["condition_id"] = "tomato.fungal.early_blight"
        card["condition"]["pathogen"]["type"] = "disease_oomycete"
        self.write_card("early_blight.json", card)
        _, report, processed, rows = self.execute()
        envelope = json_file(processed / rows[0]["processed_file"])
        self.assertEqual(envelope["content_en"], card)
        link = json_file(report / "reference-links.json")[0]
        self.assertEqual(link["status"], "unresolved_reference")
        self.assertEqual(link["candidate_record_ids"], [rows[0]["record_id"]])
        self.assertIsNone(link["resolved_record_id"])
        self.assertFalse(link["candidates_applied"])
        self.assertIn("type_vocabulary_difference", rows[0]["flags"])

    def test_exact_duplicate_ids_and_shared_text_are_retained_for_review(self):
        self.write_card("second.json", BASE)
        _, report, processed, rows = self.execute()
        self.assertEqual(len(rows), 2)
        self.assertTrue(all("duplicate_disease_id" in r["flags"] for r in rows))
        self.assertTrue(all((processed / r["raw_copy"]).is_file() for r in rows))
        self.assertEqual(len(json_file(report / "duplicate-groups.json")), 2)
        self.assertGreater(len(json_file(report / "repeated-text.json")), 0)
        self.assertEqual(json_file(processed / "label-knowledge-mapping.json")[0]["link_status"], "mapping_needs_review")

    def test_mapping_keeps_existing_ids_and_vi_unapproved(self):
        _, _, processed, _ = self.execute()
        mapping = json_file(processed / "label-knowledge-mapping.json")[0]
        self.assertEqual(mapping["status_code"], "TOM_EARLY_BLIGHT")
        self.assertEqual(mapping["label_original"], "Tomato___Early_blight")
        self.assertFalse(mapping["approved_for_advice"])
        term = json_file(processed / "glossary-vi-draft.json")[0]
        self.assertEqual(term["term_vi_draft"], "Đốm vòng (early blight)")
        self.assertIsNone(term["reviewer"])
        self.assertEqual(term["review_status"], "needs_review")

    def test_idempotency_verifies_hashes_and_refuses_tampering(self):
        _, report, processed, _ = self.execute()
        times = {p: p.stat().st_mtime_ns for root in (report, processed) for p in root.rglob("*") if p.is_file()}
        event, _, _, _ = self.execute()
        self.assertEqual(event["status"], "reused_verified")
        self.assertEqual({p: p.stat().st_mtime_ns for p in times}, times)
        (processed / "glossary-vi-draft.json").write_text("[]", encoding="utf-8")
        result = self.execute(False)
        self.assertIn("Existing artifact hash changed; refusing overwrite", result.stderr)

    def test_raw_output_boundary_limit_and_incomplete_checkpoint(self):
        self.config["processed_root"] = "data/raw/plantexpert/processed"
        result = self.execute(False)
        self.assertIn("disjoint", result.stderr)
        self.config["processed_root"] = "data/processed/pex"
        self.config["max_json_bytes"] = 1
        _, report, _, rows = self.execute()
        self.assertFalse(rows[0]["parse_ok"])
        (report / "output-artifacts.json").unlink()
        self.assertIn("Incomplete checkpoint exists", self.execute(False).stderr)


REPORT = os.environ.get("PLANTEXPERT_REPORT")
ROOT = os.environ.get("PLANTEXPERT_PROJECT_ROOT")


@unittest.skipUnless(REPORT and ROOT, "production report not specified")
class ProductionOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = Path(REPORT)
        cls.root = Path(ROOT)
        cls.summary = json_file(cls.report / "summary.json")
        cls.processed = cls.root / "data/TomatoAI/data/processed/plantexpert-tomato" / cls.summary["run_id"]
        cls.source = cls.root / "data/TomatoAI/data/raw/plantexpert"
        cls.rows = [json.loads(line) for line in (cls.processed / "manifest.jsonl").read_text(encoding="utf-8").splitlines()]

    def test_full_raw_hashes_and_count_conservation(self):
        def snapshot_csv(name):
            with (self.report / name).open(encoding="utf-8", newline="") as stream:
                return list(csv.DictReader(stream))
        before, after = snapshot_csv("raw-before.csv"), snapshot_csv("raw-after.csv")
        self.assertEqual(before, after)
        actual = {p.relative_to(self.source).as_posix() for p in self.source.rglob("*") if p.is_file()}
        self.assertEqual({r["source_file"] for r in before}, actual)
        for row in before:
            self.assertEqual(hash_file(self.source / row["source_file"]), row["sha256"])
        self.assertEqual(len(self.rows), self.summary["source_card_records"])
        self.assertEqual(len(self.rows), len({r["record_id"] for r in self.rows}))
        self.assertEqual(sum(self.summary["record_status_counts"].values()), len(self.rows))
        self.assertEqual(self.summary["retained_normalized_records"] + sum(not r["schema_ok"] for r in self.rows), len(self.rows))

    def test_all_original_and_normalized_english_content_has_lineage(self):
        def nfc(value):
            if isinstance(value, dict):
                return {k: nfc(v) for k, v in value.items()}
            if isinstance(value, list):
                return [nfc(v) for v in value]
            return unicodedata.normalize("NFC", value) if isinstance(value, str) else value
        for row in self.rows:
            original = self.source / row["source_file"]
            self.assertEqual((self.processed / row["raw_copy"]).read_bytes(), original.read_bytes())
            self.assertEqual(hash_file(original), row["source_sha256"])
            if row["schema_ok"]:
                raw = json_file(original)
                envelope = json_file(self.processed / row["processed_file"])
                self.assertEqual(envelope["content_en"], nfc(raw))
                self.assertEqual(envelope["source"]["disease_id_original"], raw["disease_id"])
                self.assertEqual(envelope["content_en"]["management"], nfc(raw["management"]))
                self.assertFalse(envelope["review"]["safe_for_advice"])

    def test_reference_endpoints_and_candidates_never_change_original_ids(self):
        ids = {r["disease_id_original"]: r["record_id"] for r in self.rows}
        endpoints = {r["record_id"] for r in self.rows}
        for entry in json_file(self.report / "reference-links.json"):
            original = json_file(self.source / entry["source_file"])
            index = int(entry["source_pointer"].split("/")[2])
            self.assertEqual(original["lookalikes"][index]["condition_id"], entry["target_id_original"])
            self.assertFalse(entry["candidates_applied"])
            self.assertTrue(set(entry["candidate_record_ids"]) <= endpoints)
            if entry["status"] == "exact_reference":
                self.assertEqual(entry["resolved_record_id"], ids[entry["target_id_original"]])
            else:
                self.assertIsNone(entry["resolved_record_id"])

    def test_image_mapping_coverage_and_review_gates(self):
        labels = json_file(self.root / "data/TomatoAI/data/processed/plantvillage/pv-d9e4c21eec8e9172/label-mapping.json")["labels"]
        mapping = json_file(self.processed / "label-knowledge-mapping.json")
        self.assertEqual({m["label_original"]: m["status_code"] for m in mapping}, labels)
        self.assertEqual(len(mapping), 10)
        self.assertTrue(all(not m["approved_for_advice"] for m in mapping))
        self.assertTrue(all(not r["ready_for_training"] and not r["safe_for_advice"] for r in self.rows))
        for entry in json_file(self.report / "review-queue.json"):
            self.assertIn(entry["record_id"], {r["record_id"] for r in self.rows})
            self.assertEqual(entry["review_status"], "pending")
        for term in json_file(self.processed / "glossary-vi-draft.json"):
            self.assertEqual(term["review_status"], "needs_review")
            self.assertIsNone(term["reviewer"])

    def test_sealed_artifacts_and_reference_inputs_are_unchanged(self):
        for item in json_file(self.report / "output-artifacts.json"):
            root = self.processed if item["scope"] == "processed" else self.report
            self.assertEqual(hash_file(root / item["path"]), item["sha256"])
        for item in json_file(self.report / "reference-inputs.json").values():
            self.assertEqual(hash_file(self.root / item["path"]), item["sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
