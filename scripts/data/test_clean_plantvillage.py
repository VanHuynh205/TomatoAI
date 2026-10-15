"""CLI/output tests; synthetic images only inside temporary directories."""
import csv
import hashlib
import json
import os
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).with_name("clean_plantvillage.py")
A = "Tomato___healthy"
B = "Tomato___Early_blight"
TARGET = "Tomato___Target_Spot"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "raw"
        (self.source / "raw/color").mkdir(parents=True)
        (self.source / "leaf_grouping/filtered_leafmaps").mkdir(parents=True)
        self.map = {}
        self.csvs = {}
        self.config = self.root / "config.json"
        self.config.write_text(json.dumps({"schema_version": "1.0", "source_root": "raw", "processed_root": "processed", "report_root": "reports", "source_url": "synthetic-test-only", "license_declared": "synthetic", "near_hash_radius": 4, "near_pair_limit": 100, "labels": {A: "TOM_HEALTHY", B: "TOM_EARLY_BLIGHT", TARGET: "TOM_TARGET_SPOT"}}), encoding="utf-8")

    def image(self, label, name, leaf=None, seed=1, variant="color", uniform=False):
        path = self.source / "raw" / variant / label / name
        path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGB", (256, 256), (20, 30, 40))
        if not uniform:
            rng = random.Random(seed)
            image.putdata([(rng.randrange(256), rng.randrange(256), rng.randrange(256)) for _ in range(256 * 256)])
        image.save(path)
        if leaf is not None:
            source_name = name.split("___", 1)[-1]
            lookup = Path(source_name).stem.casefold()
            self.map.setdefault(lookup, []).append(f"{label}:::{leaf}.0")
            self.csvs.setdefault(label, []).append([source_name, f"{leaf}.0"])
        return path

    def metadata(self, second=None):
        for name, value in (("leaf-map.json", self.map), ("leaf_grouping/leaf-map.json", self.map if second is None else second)):
            (self.source / name).write_text(json.dumps(value), encoding="utf-8")
        for label, rows in self.csvs.items():
            with (self.source / "leaf_grouping/filtered_leafmaps" / (label + ".csv")).open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["File Name", "Leaf #"])
                writer.writerows(rows)

    def cli(self, expect_ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), "--config", str(self.config), "--project-root", str(self.root)], text=True, capture_output=True)
        if expect_ok:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            outcome = json.loads(result.stdout.splitlines()[-1])
            report, processed = Path(outcome["report"]), Path(outcome["processed"])
            rows = [json.loads(line) for line in (processed / "manifest.jsonl").read_text(encoding="utf-8").splitlines()]
            return outcome, report, processed, rows
        self.assertNotEqual(result.returncode, 0)
        return result

    def test_counts_provenance_decode_and_same_label_exact_dedup(self):
        original = self.image(A, "id___RS_HL 1.png", 1)
        duplicate = self.source / "raw/color" / A / "id2___RS_HL 2.png"
        duplicate.write_bytes(original.read_bytes())
        self.map["rs_hl 2"] = [f"{A}:::1.0"]
        self.csvs[A].append(["RS_HL 2.png", "1.0"])
        broken = self.source / "raw/color" / A / "broken.JPG"
        broken.write_bytes(b"not a jpeg")
        self.metadata()
        before = {p.relative_to(self.source).as_posix(): digest(p) for p in self.source.rglob("*") if p.is_file()}
        _, report, processed, rows = self.cli()
        summary = json.loads((report / "summary.json").read_text())
        self.assertEqual(summary["source_records"], 3)
        self.assertEqual(summary["record_status_counts"], {"excluded_invalid": 1, "ready_for_split": 1, "excluded_exact_duplicate": 1})
        self.assertEqual(summary["retained_copies"], 1)
        self.assertFalse(summary["training_ready"])
        self.assertFalse(summary["split_created"])
        self.assertEqual(before, {p.relative_to(self.source).as_posix(): digest(p) for p in self.source.rglob("*") if p.is_file()})
        valid = next(r for r in rows if r["processed_file"])
        self.assertEqual(digest(processed / valid["processed_file"]), digest(original))
        self.assertTrue(valid["group_evidence"])
        self.assertEqual(valid["status_code"], "TOM_HEALTHY")
        self.assertEqual(valid["leaf_group_id"], f"{A}:::1")

    def test_conflicting_metadata_never_becomes_ready(self):
        self.image(A, "id___RS_HL 1.png", 1)
        self.metadata({"rs_hl 1": [f"{A}:::2.0"]})
        _, _, _, rows = self.cli()
        self.assertEqual(rows[0]["record_status"], "needs_review")
        self.assertEqual(rows[0]["leaf_group_id"], "")
        self.assertIn("group_metadata_conflict_or_incomplete", rows[0]["flags"])

    def test_zero_and_prefixed_leaf_ids_are_not_missing_or_schema_errors(self):
        self.image(A, "a___RS_HL 1.png", 0)
        self.image(A, "b___RS_HL 2.png", seed=3)
        self.map["rs_hl 2"] = [f"{A}:::OCT_563.0"]
        self.csvs[A].append(["RS_HL 2.png", "OCT_563.0"])
        self.metadata()
        _, report, _, rows = self.cli()
        self.assertEqual({r["leaf_group_id"] for r in rows}, {f"{A}:::0", f"{A}:::OCT_563.0"})
        self.assertEqual({r["record_status"] for r in rows}, {"ready_for_split"})
        self.assertEqual(json.loads((report / "summary.json").read_text())["grouping"]["metadata_issues"], 0)

    def test_cross_label_exact_conflict_is_retained_for_review_not_deduped(self):
        a = self.image(A, "a___RS_HL 1.png", 1)
        b = self.image(B, "b___RS_EB 1.png", 1)
        b.write_bytes(a.read_bytes())
        self.metadata()
        _, _, _, rows = self.cli()
        self.assertEqual({r["record_status"] for r in rows}, {"needs_review"})
        self.assertEqual(len({r["split_component_id"] for r in rows}), 1)
        self.assertTrue(all(r["processed_file"] for r in rows))
        self.assertTrue(all("cross_label_exact_or_variant_conflict" in r["flags"] for r in rows))

    def test_near_candidate_hash_never_deletes_or_merges_leaf_groups(self):
        self.image(A, "a___RS_HL 1.png", 1, uniform=True)
        b = self.image(A, "b___RS_HL 2.png", 2, uniform=True)
        with Image.open(b) as image:
            image.putpixel((100, 100), (21, 30, 40))
            image.save(b)
        self.metadata()
        _, report, _, rows = self.cli()
        self.assertEqual(len({r["split_component_id"] for r in rows}), 2)
        self.assertEqual({r["record_status"] for r in rows}, {"needs_review"})
        self.assertTrue(all(r["processed_file"] for r in rows))
        self.assertEqual(json.loads((report / "summary.json").read_text())["near_candidates"]["pairs"], 1)

    def test_target_prefix_numeric_alias_stays_unapplied(self):
        self.image(TARGET, "id___Com.G_TgS_FL 0004.png")
        self.map["com.g_fl 0004"] = [f"{TARGET}:::1.0"]
        self.csvs[TARGET] = [["Com.G_FL 0004.png", "1.0"]]
        self.metadata()
        _, report, _, rows = self.cli()
        aliases = json.loads((report / "alias-candidates.json").read_text())
        self.assertEqual(len(aliases), 1)
        self.assertFalse(aliases[0]["applied"])
        self.assertEqual(rows[0]["leaf_group_id"], "")
        self.assertEqual(rows[0]["record_status"], "needs_review")

    def test_unmapped_named_leaf_does_not_get_a_filename_fallback(self):
        self.image(A, "id___GH_HL Leaf 259.1.JPG")
        self.metadata()
        _, _, processed, rows = self.cli()
        self.assertEqual(rows[0]["leaf_group_id"], "")
        self.assertEqual(rows[0]["record_status"], "needs_review")
        with (processed / "benchmark-candidates.csv").open() as f:
            self.assertEqual(list(csv.DictReader(f)), [])

    def test_variants_share_component_and_pending_blocks_entire_component(self):
        name = "000146ff-92a4-4db6-90ad-8fce2ae4fddd___RS_HL 1.png"
        self.image(A, name, 1, variant="color")
        other = self.image(A, name, variant="grayscale")
        with Image.open(other) as image:
            image.convert("L").save(other)
        self.metadata()
        _, _, processed, rows = self.cli()
        self.assertEqual(len({r["split_component_id"] for r in rows}), 1)
        self.assertEqual({r["record_status"] for r in rows}, {"needs_review"})
        with (processed / "benchmark-candidates.csv").open() as f:
            self.assertEqual(list(csv.DictReader(f)), [])

    def test_idempotent_reuse_and_tamper_refusal(self):
        self.image(A, "id___RS_HL 1.png", 1)
        self.metadata()
        first, report, processed, rows = self.cli()
        before = {str(p): (digest(p), p.stat().st_mtime_ns) for root in (report, processed) for p in root.rglob("*") if p.is_file()}
        second, _, _, _ = self.cli()
        self.assertEqual(second["status"], "reused_verified")
        self.assertEqual(second["run_id"], first["run_id"])
        self.assertEqual(before, {str(p): (digest(p), p.stat().st_mtime_ns) for root in (report, processed) for p in root.rglob("*") if p.is_file()})
        (processed / rows[0]["processed_file"]).write_bytes(b"tampered")
        failed = self.cli(expect_ok=False)
        self.assertIn("Existing output hash mismatch", failed.stderr)

    def test_near_budget_exhaustion_is_visible_and_blocks_ready_subset(self):
        for i in range(3):
            path = self.image(A, f"id{i}___RS_HL {i}.png", i + 1, uniform=True)
            with Image.open(path) as image:
                image.putpixel((100, 100), (21 + i, 30, 40))
                image.save(path)
        self.metadata()
        config = json.loads(self.config.read_text())
        config["near_pair_limit"] = 1
        self.config.write_text(json.dumps(config))
        _, report, _, rows = self.cli()
        self.assertTrue(json.loads((report / "summary.json").read_text())["near_candidates"]["truncated"])
        self.assertEqual({r["record_status"] for r in rows}, {"needs_review"})
        self.assertTrue(all("near_scan_budget_reached" in r["flags"] for r in rows))

    def test_output_path_inside_source_is_rejected_without_source_writes(self):
        self.image(A, "id___RS_HL 1.png", 1)
        self.metadata()
        config = json.loads(self.config.read_text())
        config["processed_root"] = "raw/processed"
        self.config.write_text(json.dumps(config))
        result = self.cli(expect_ok=False)
        self.assertIn("roots must be disjoint", result.stderr)
        self.assertFalse((self.source / "processed").exists())


@unittest.skipUnless(os.environ.get("PLANTVILLAGE_REPORT"), "Set PLANTVILLAGE_REPORT to verify actual outputs")
class ProductionOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = Path(os.environ["PLANTVILLAGE_REPORT"])
        cls.summary = json.loads((cls.report / "summary.json").read_text(encoding="utf-8"))
        cls.config = json.loads((cls.report / "config.json").read_text(encoding="utf-8"))
        cls.project = Path(os.environ["PLANTVILLAGE_PROJECT_ROOT"])
        cls.source = cls.project / cls.config["source_root"]
        cls.processed = cls.project / cls.config["processed_root"] / cls.summary["run_id"]
        cls.rows = [json.loads(line) for line in (cls.processed / "manifest.jsonl").read_text(encoding="utf-8").splitlines()]
        cls.by_id = {r["record_id"]: r for r in cls.rows}

    def read_csv(self, path):
        with path.open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def test_manifest_schema_unique_ids_and_source_count_conservation(self):
        original = [p for variant in (self.source / "raw").iterdir() if variant.is_dir() for label in variant.iterdir() if label.is_dir() and label.name.startswith("Tomato") for p in label.rglob("*") if p.is_file()]
        self.assertEqual(len(original), len(self.rows))
        self.assertEqual(len(self.by_id), len(self.rows))
        self.assertEqual(sum(self.summary["record_status_counts"].values()), len(self.rows))
        for row in self.rows:
            self.assertEqual(row["schema_version"], "1.0")
            self.assertIn(row["record_status"], {"ready_for_split", "needs_review", "excluded_invalid", "excluded_exact_duplicate"})
            self.assertIsInstance(row["flags"], list)
            self.assertIsInstance(row["group_evidence"], list)
            self.assertIs(row["ready_for_training"], False)
            self.assertEqual(row["status_code"], self.config["labels"].get(row["label_original"], ""))

    def test_raw_before_after_full_hashes_and_manifest_lineage(self):
        before = self.read_csv(self.report / "raw-before.csv")
        after = self.read_csv(self.report / "raw-after.csv")
        self.assertEqual(before, after)
        actual_paths = {p.relative_to(self.source).as_posix() for p in self.source.rglob("*") if p.is_file() and not any(x in {".git", ".cache", "__pycache__"} for x in p.relative_to(self.source).parts)}
        self.assertEqual(actual_paths, {r["source_file"] for r in before})
        inventory = {r["source_file"]: r for r in after}
        for row in self.rows:
            self.assertEqual(row["sha256"], inventory[row["source_file"]]["sha256"])
            self.assertEqual(row["bytes"], int(inventory[row["source_file"]]["bytes"]))
            self.assertTrue((self.source / row["source_file"]).is_file())

    def test_every_derived_image_is_byte_identical_and_exclusions_have_no_copy(self):
        expected = set()
        for row in self.rows:
            if row["record_status"].startswith("excluded"):
                self.assertEqual(row["processed_file"], "")
            else:
                path = self.processed / row["processed_file"]
                self.assertEqual(digest(path), row["sha256"])
                expected.add(path.relative_to(self.processed / "images").as_posix())
        actual = {p.relative_to(self.processed / "images").as_posix() for p in (self.processed / "images").rglob("*") if p.is_file()}
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), self.summary["retained_copies"])

    def test_group_edges_and_pending_records_cannot_cross_benchmark_boundary(self):
        for edge in self.read_csv(self.report / "group-edges.csv"):
            self.assertEqual(self.by_id[edge["record_a"]]["split_component_id"], self.by_id[edge["record_b"]]["split_component_id"])
        candidates = self.read_csv(self.processed / "benchmark-candidates.csv")
        self.assertEqual({r["record_id"] for r in candidates}, {r["record_id"] for r in self.rows if r["record_status"] == "ready_for_split"})
        blocked = {r["split_component_id"] for r in self.rows if r["flags"]}
        for row in candidates:
            record = self.by_id[row["record_id"]]
            self.assertTrue(record["leaf_group_id"])
            self.assertTrue(record["group_evidence"])
            self.assertEqual(record["flags"], [])
            self.assertNotIn(record["split_component_id"], blocked)
        self.assertFalse(self.summary["split_created"])
        self.assertFalse(self.summary["training_ready"])

    def test_review_alias_and_near_queues_have_real_endpoints_and_no_auto_resolution(self):
        review = json.loads((self.report / "review-queue.json").read_text(encoding="utf-8"))
        self.assertEqual({r["record_id"] for r in review}, {r["record_id"] for r in self.rows if r["flags"]})
        for row in json.loads((self.report / "alias-candidates.json").read_text(encoding="utf-8")):
            self.assertIs(row["applied"], False)
            self.assertEqual(self.by_id[row["record_id"]]["leaf_group_id"], "")
        for pair in self.read_csv(self.report / "near-candidates.csv"):
            a, b = self.by_id[pair["record_a"]], self.by_id[pair["record_b"]]
            self.assertNotEqual(a["split_component_id"], b["split_component_id"])
            self.assertNotEqual(a["pixel_sha256"], b["pixel_sha256"])
            self.assertLessEqual(int(pair["distance"]), self.config["near_hash_radius"])
            self.assertIn("cross_component_near_candidate", a["flags"])
            self.assertIn("cross_component_near_candidate", b["flags"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
