"""Real temporary artifacts exercise the benchmark's read-only trust boundaries."""
import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts/data"))
import prepare_benchmark as benchmark


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, allow_nan=False), encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.root = self.project / "data/TomatoAI/data"
        self.raw = self.root / "raw/pv"
        self.processed = self.root / "processed/pv/run1"
        self.report = self.root / "reports/pv/run1"
        for p in (self.raw, self.processed, self.report):
            p.mkdir(parents=True)
        (self.raw / "image.txt").write_bytes(b"raw image stand-in, no image decoding in inventory")
        (self.processed / "image.txt").write_bytes((self.raw / "image.txt").read_bytes())
        row = {"record_id": "pv:1", "source_file": "image.txt", "sha256": digest(self.raw / "image.txt"),
               "processed_file": "image.txt", "label_original": "A", "record_status": "ready_for_split",
               "leaf_group_id": "leaf1", "split_component_id": "old1", "group_evidence": [{"source_file": "map.json", "source_record": "one"}],
               "pixel_sha256": "1" * 64, "duplicate_of": "", "flags": [], "ready_for_training": False}
        (self.processed / "manifest.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
        with (self.processed / "manifest.csv").open("w", newline="", encoding="utf-8") as s:
            writer = csv.DictWriter(s, fieldnames=["record_id", "source_file", "sha256", "processed_file", "record_status"])
            writer.writeheader()
            writer.writerow({k: row[k] for k in writer.fieldnames})
        with (self.report / "raw-before.csv").open("w", newline="", encoding="utf-8") as s:
            writer = csv.DictWriter(s, fieldnames=["source_file", "bytes", "sha256"])
            writer.writeheader()
            writer.writerow({"source_file": "image.txt", "bytes": (self.raw / "image.txt").stat().st_size, "sha256": row["sha256"]})
        write(self.report / "config.json", {"source_root": "data/TomatoAI/data/raw/pv"})
        write(self.report / "checkpoint.json", {"run_id": "run1", "status": "complete"})
        write(self.report / "summary.json", {"run_id": "run1", "source_records": 1, "record_status_counts": {"ready_for_split": 1}, "retained_copies": 1, "training_ready": False})
        write(self.report / "review-queue.json", [])
        write(self.report / "alias-candidates.json", [])
        (self.report / "near-candidates.csv").write_text("record_a,record_b,distance\n", encoding="utf-8")
        (self.report / "group-edges.csv").write_text("record_a,record_b,evidence_type,evidence_value\n", encoding="utf-8")
        self.registry = self.root / "dataset-registry.json"
        self.entry = {"current_run": "run1", "source_root": "raw/pv", "processed": "processed/pv/run1", "checkpoint": "reports/pv/run1/checkpoint.json", "counts": {"source_images": 1, "retained_copies": 1}, "blockers": [], "training_ready": False}
        write(self.registry, {"datasets": {"PlantVillage": self.entry}})
        self.rights = self.project / "docs/development/assets-rights.json"
        write(self.rights, {"assets": [{"id": "dataset:PlantVillage", "selected_run": "run1", "training_approved": False, "outstanding": ["rights pending"]}]})
        self.seal()

    def seal(self):
        write(self.report / "output-artifacts.json", [
            {"scope": scope, "path": p.relative_to(folder).as_posix(), "sha256": digest(p)}
            for scope, folder in (("processed", self.processed), ("report", self.report))
            for p in sorted(folder.rglob("*")) if p.is_file() and p.name != "output-artifacts.json"])

    def inventory(self):
        return benchmark.build_inventory(self.registry)

    def test_selected_run_counts_provenance_and_no_raw_writes(self):
        before = digest(self.raw / "image.txt")
        report = self.inventory()
        self.assertEqual(report.errors, [])
        entry = report.datasets[0]
        self.assertEqual(entry["selected_run"], "run1")
        self.assertEqual(entry["observed"]["manifest_records"], 1)
        self.assertEqual(entry["observed"]["retained"], 1)
        self.assertEqual(entry["role"], "image_benchmark_candidate")
        self.assertFalse(entry["training_eligible"])
        self.assertEqual(report.raw_writes, 0)
        self.assertEqual(digest(self.raw / "image.txt"), before)

    def test_missing_checkpoint_names_exact_artifact_without_fallback(self):
        (self.report / "checkpoint.json").unlink()
        write(self.report.parent / "newer/checkpoint.json", {"run_id": "newer"})
        report = self.inventory()
        self.assertEqual(len(report.errors), 1)
        self.assertIn("run1/checkpoint.json", report.errors[0])
        self.assertEqual(report.datasets, [])

    def test_run_mismatch_rejected(self):
        write(self.report / "summary.json", {"run_id": "newer"})
        self.seal()
        self.assertIn("run_id", " ".join(self.inventory().errors))

    def test_missing_provenance_rejected(self):
        with (self.processed / "manifest.csv").open("w", encoding="utf-8") as s:
            s.write("record_id,source_file,sha256,processed_file,record_status\npv:1,image.txt,,image.txt,ready_for_split\n")
        self.seal()
        self.assertIn("source hash", " ".join(self.inventory().errors))

    def test_raw_change_rejected(self):
        (self.raw / "image.txt").write_bytes(b"changed")
        self.assertIn("raw", " ".join(self.inventory().errors))

    def test_changed_sealed_output_rejected(self):
        (self.processed / "image.txt").write_bytes(b"changed")
        self.assertIn("hash", " ".join(self.inventory().errors).lower())

    def test_traversal_in_registry_rejected(self):
        self.entry["processed"] = "../../outside/run1"
        write(self.registry, {"datasets": {"PlantVillage": self.entry}})
        self.assertIn("outside", " ".join(self.inventory().errors))

    def test_missing_rights_is_error_not_approval(self):
        self.rights.unlink()
        self.assertIn("assets-rights.json", " ".join(self.inventory().errors))

    def test_registry_count_drift_rejected(self):
        self.entry["counts"]["source_images"] = 2
        write(self.registry, {"datasets": {"PlantVillage": self.entry}})
        self.assertIn("count", " ".join(self.inventory().errors))

    def test_nonstandard_json_rejected(self):
        self.registry.write_text('{"datasets":NaN}', encoding="utf-8")
        self.assertTrue(self.inventory().errors)

    def test_unrecorded_raw_file_rejected(self):
        (self.raw / "new.txt").write_bytes(b"not in baseline")
        self.assertIn("raw file set", " ".join(self.inventory().errors))

    def test_reference_hash_change_rejected(self):
        ref = self.project / "reference.json"
        write(ref, {"value": "before"})
        write(self.report / "fingerprint-inputs.json", {"references": [{"path": "reference.json", "sha256": digest(ref)}]})
        self.seal()
        write(ref, {"value": "changed"})
        self.assertIn("reference hash", " ".join(self.inventory().errors))

    def test_source_config_outside_registry_source_rejected(self):
        write(self.report / "config.json", {"source_root": "docs"})
        self.seal()
        self.assertIn("source root", " ".join(self.inventory().errors))


class GroupTest(unittest.TestCase):
    """Source manifests are immutable; resolution is a new sidecar only."""
    def setUp(self):
        InventoryTest.setUp(self)
        self.decisions = self.project / "decisions.json"
        write(self.decisions, {"group_assignments": [], "near_reviews": [], "scope": "technical review only"})

    seal = InventoryTest.seal

    def set_rows(self, rows, near=()):
        self.rows = rows
        (self.processed / "manifest.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        with (self.report / "near-candidates.csv").open("w", newline="", encoding="utf-8") as s:
            writer = csv.DictWriter(s, fieldnames=["record_a", "record_b", "distance"])
            writer.writeheader()
            writer.writerows(near)
        write(self.report / "alias-candidates.json", [])
        self.inventory_report = benchmark.InventoryReport(str(self.registry), digest(self.registry),
            str(self.rights), digest(self.rights), [{"dataset": "PlantVillage", "selected_run": "run1",
            "processed": str(self.processed), "report": str(self.report), "raw_source": str(self.raw),
            "manifest_jsonl_sha256": digest(self.processed / "manifest.jsonl"),
            "group_inputs": {n: digest(self.report / n) for n in ("near-candidates.csv", "alias-candidates.json")},
            "rights": {"training_approved": False}}])

    @staticmethod
    def row(record, leaf="leaf1", label="A", sha=None, pixel=None, duplicate=""):
        return {"record_id": record, "source_file": record, "processed_file": record,
                "label_original": label, "leaf_group_id": leaf, "split_component_id": "",
                "sha256": sha or hashlib.sha256(record.encode()).hexdigest(),
                "pixel_sha256": pixel or hashlib.sha256((record + "pixels").encode()).hexdigest(),
                "group_evidence": [{"source_file": "leaf-map.json", "source_record": leaf}] if leaf else [],
                "flags": [], "record_status": "excluded_exact_duplicate" if duplicate else "ready_for_split" if leaf else "needs_review",
                "duplicate_of": duplicate, "ready_for_training": False}

    def test_same_leaf_and_exact_duplicate_share_component_one_disposition(self):
        self.set_rows([self.row("a"), self.row("b"), self.row("c", leaf="leaf2", sha=self.row("a")["sha256"], duplicate="a")])
        review = benchmark.resolve_groups(self.inventory_report, self.decisions)
        self.assertEqual(review.errors, [])
        self.assertEqual(len({r["component_id"] for r in review.records}), 1)
        self.assertEqual([r["disposition"] for r in review.records], ["technical_candidate", "technical_candidate", "excluded_exact_duplicate"])
        self.assertTrue(all(r["training_eligible"] is False for r in review.records))

    def test_missing_group_and_alias_remain_quarantined(self):
        self.set_rows([self.row("a", leaf=""), self.row("b", leaf="leaf2")])
        write(self.report / "alias-candidates.json", [{"record_id": "a", "candidate_leaf_groups": ["leaf2"], "applied": False}])
        self.inventory_report.datasets[0]["group_inputs"]["alias-candidates.json"] = digest(self.report / "alias-candidates.json")
        review = benchmark.resolve_groups(self.inventory_report, self.decisions)
        a = review.records[0]
        self.assertEqual(a["leaf_group_id"], "")
        self.assertEqual(a["disposition"], "quarantined")
        self.assertIn("alias_candidate_not_identity_evidence", a["reasons"])

    def test_cross_label_pixel_component_quarantined(self):
        self.set_rows([self.row("a"), self.row("b", leaf="other", label="B", pixel=self.row("a")["pixel_sha256"])])
        review = benchmark.resolve_groups(self.inventory_report, self.decisions)
        self.assertEqual(len({r["component_id"] for r in review.records}), 1)
        self.assertTrue(all(r["disposition"] == "quarantined" for r in review.records))
        self.assertTrue(all("component_label_conflict" in r["reasons"] for r in review.records))

    def test_pending_near_pair_quarantines_whole_leaf_component(self):
        self.set_rows([self.row("a"), self.row("a2"), self.row("b", leaf="other")],
                      [{"record_a": "a", "record_b": "b", "distance": "1"}])
        review = benchmark.resolve_groups(self.inventory_report, self.decisions)
        self.assertTrue(all(r["disposition"] == "quarantined" for r in review.records))
        self.assertTrue(all("near_duplicate_review_pending" in r["reasons"] for r in review.records))

    def test_unknown_pair_and_stale_inventory_fail_closed(self):
        self.set_rows([self.row("a")], [{"record_a": "a", "record_b": "unknown", "distance": "1"}])
        self.assertIn("unknown record", " ".join(benchmark.resolve_groups(self.inventory_report, self.decisions).errors))
        (self.processed / "manifest.jsonl").write_text("{}\n", encoding="utf-8")
        self.assertIn("hash", " ".join(benchmark.resolve_groups(self.inventory_report, self.decisions).errors))

    def test_unverified_manual_group_override_rejected(self):
        self.set_rows([self.row("a", leaf="")])
        write(self.decisions, {"group_assignments": [{"record_id": "a", "leaf_group_id": "invented"}], "near_reviews": []})
        self.assertIn("manual", " ".join(benchmark.resolve_groups(self.inventory_report, self.decisions).errors))

    def test_source_review_flags_and_unknown_status_block_whole_component(self):
        for changes in ({"record_status": "needs_review", "flags": ["mode_or_dimensions_need_review"]},
                        {"flags": ["near_scan_budget_reached"]}, {"record_status": "unknown"},
                        {"processed_file": ""}):
            with self.subTest(changes=changes):
                first = dict(self.row("a"), **changes)
                self.set_rows([first, self.row("b")])
                review = benchmark.resolve_groups(self.inventory_report, self.decisions)
                self.assertEqual(review.errors, [])
                self.assertTrue(all(r["disposition"] == "quarantined" for r in review.records))
                self.assertEqual(review.records[0]["source_record_status"], first["record_status"])
                self.assertEqual(review.records[0]["source_flags"], first["flags"])

    def test_cli_rejects_missing_dependency_without_any_output(self):
        import subprocess
        policy = self.project / "artifacts/policy.json"
        write(policy, {"sentinel": "must survive"})
        before = policy.read_bytes()
        result = subprocess.run([sys.executable, benchmark.__file__, "--registry", str(self.registry),
                                 "--output", str(policy), "--split-policy", str(policy)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(policy.read_bytes(), before)

    def test_cli_rejects_input_and_fixed_sidecar_collisions_before_writing(self):
        import subprocess
        folder = self.project / "artifacts"
        decisions, policy = folder / "decisions.json", folder / "policy.json"
        write(decisions, {"group_assignments": [], "near_reviews": []})
        write(policy, {"sentinel": "must survive"})
        for output, policy_input in ((policy, policy), (decisions, policy),
                                     (folder / "split-manifest.json", policy),
                                     (folder / "data-card.json", folder / "group-resolution.json")):
            with self.subTest(output=output, policy_input=policy_input):
                write(policy_input, {"sentinel": "must survive"})
                before = {p: p.read_bytes() for p in folder.iterdir() if p.is_file()}
                result = subprocess.run([sys.executable, benchmark.__file__, "--registry", str(self.registry),
                                         "--output", str(output), "--group-decisions", str(decisions),
                                         "--split-policy", str(policy_input)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual({p: p.read_bytes() for p in folder.iterdir() if p.is_file()}, before)

    def test_metadata_exact_lookup_does_not_promote_numeric_alias(self):
        label = "Tomato___Target_Spot"
        a = self.row("a", leaf="", label=label)
        a["source_file"] = "uuid___Com.G_TgS_FL 123.JPG"
        self.set_rows([a])
        for name in ("leaf-map.json", "leaf_grouping/leaf-map.json"):
            write(self.raw / name, {"com.g_fl 123": [label + ":::0"]})
        csv_path = self.raw / "leaf_grouping/filtered_leafmaps" / (label + ".csv")
        csv_path.parent.mkdir(parents=True)
        csv_path.write_text("File Name,Leaf #\nCom.G_FL 123.JPG,0\n", encoding="utf-8")
        audit = benchmark.investigate_metadata(self.inventory_report)
        self.assertEqual(audit["errors"], [])
        self.assertEqual(audit["exact_grouped_records"], 0)
        self.assertEqual(audit["missing_group_records"], 1)
        self.assertEqual(audit["metadata_disagreements"], [])
        self.assertFalse(audit["aliases_applied"])

    def test_split_cli_cannot_overwrite_source(self):
        import subprocess
        script = Path(benchmark.__file__)
        before = self.registry.read_bytes()
        call = subprocess.run([sys.executable, str(script), "--registry", str(self.registry), "--output", str(self.registry)],
                              capture_output=True, text=True, timeout=20)
        self.assertNotEqual(call.returncode, 0)
        self.assertEqual(self.registry.read_bytes(), before)


class SplitTest(unittest.TestCase):
    def setUp(self):
        self.review = benchmark.GroupReview("inventory-hash")
        self.review.records = [dict(GroupTest.row(f"{label}{i}", leaf=f"{label}{i}", label=label),
                                    component_id=f"component:{label}{i}", disposition="technical_candidate",
                                    reasons=[], training_eligible=False) for label in ("A", "B") for i in range(8)]
        self.review.evidence = {"rights": {"training_approved": True}, "selected_run": "fixture-only"}
        self.policy_data = {"version": "fixture-v1", "seed": 42,
                            "ratios": {"train": 0.6, "validation": 0.2, "test": 0.2},
                            "ordered_labels": ["B", "A"], "scope": "fixture-only",
                            "benchmark_approved": True, "approved_by": "fixture-reviewer", "approved_at": "2026-10-15",
                            "labels_reviewed": True, "group_review_sha256": benchmark.fingerprint(benchmark.asdict(self.review)),
                            "approved_record_ids": [r["record_id"] for r in self.review.records]}

    def policy(self, **changes):
        return benchmark.SplitPolicy(**dict(self.policy_data, **changes))

    def test_group_disjoint_deterministic_order_and_supports(self):
        first = benchmark.create_split(self.review, self.policy())
        self.assertEqual(first.status, "approved_derivative")
        self.assertEqual(first.errors, [])
        self.assertEqual(first.class_manifest["ordered_labels"], ["B", "A"])
        self.assertEqual(first.class_manifest["class_to_idx"], {"B": 0, "A": 1})
        self.assertEqual(len(first.assignments), 16)
        groups = {s: {r["component_id"] for r in first.assignments if r["split"] == s} for s in ("train", "validation", "test")}
        self.assertFalse(groups["train"] & groups["validation"] or groups["train"] & groups["test"] or groups["validation"] & groups["test"])
        self.assertTrue(all(n > 0 for values in first.supports.values() for n in values.values()))
        again = benchmark.create_split(self.review, self.policy())
        self.assertEqual(first.assignments, again.assignments)
        self.assertEqual(first.sha256, again.sha256)
        self.assertEqual(first.preprocessing["fit_statistics_on"], "train_only")
        self.assertEqual(first.preprocessing["augmentation_on"], "train_only")

    def test_absent_approval_blocks_all_assignments(self):
        result = benchmark.create_split(self.review, self.policy(benchmark_approved=False))
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.assignments, [])
        self.assertEqual(result.class_manifest, {})

    def test_null_bool_nan_and_invalid_ratios_fail_closed(self):
        for changes in ({"seed": True}, {"seed": None}, {"ratios": {"train": float("nan"), "validation": .2, "test": .2}},
                        {"ratios": {"train": .7, "validation": .2, "test": .2}}, {"labels_reviewed": False},
                        {"approved_by": ""}, {"ordered_labels": ["A", "A"]}):
            with self.subTest(changes=changes):
                self.assertEqual(benchmark.create_split(self.review, self.policy(**changes)).assignments, [])

    def test_stale_review_or_unapproved_rights_blocks(self):
        self.assertTrue(benchmark.create_split(self.review, self.policy(group_review_sha256="stale")).errors)
        self.review.evidence["rights"]["training_approved"] = False
        self.policy_data["group_review_sha256"] = benchmark.fingerprint(benchmark.asdict(self.review))
        self.assertIn("rights", " ".join(benchmark.create_split(self.review, self.policy()).errors))

    def test_ordered_codes_require_list_of_unique_nonempty_strings(self):
        for codes in ("BA", {"B": "x", "A": "y"}, None, ["B", ""], ["B", "B"], ["B", None]):
            with self.subTest(codes=codes):
                result = benchmark.create_split(self.review, self.policy(scope="approved_pilot", ordered_codes=codes))
                self.assertEqual(result.status, "blocked")
                self.assertEqual(result.assignments, [])
                self.assertEqual(result.class_manifest, {})
        result = benchmark.create_split(self.review, self.policy(scope="approved_pilot", ordered_codes=["CODE_B", "CODE_A"]))
        self.assertEqual(result.errors, [])
        self.assertEqual(result.class_manifest["ordered_codes"], ["CODE_B", "CODE_A"])

    def test_unresolved_cannot_be_approved_and_duplicate_component_never_crosses(self):
        self.review.records[0]["disposition"] = "quarantined"
        self.policy_data["group_review_sha256"] = benchmark.fingerprint(benchmark.asdict(self.review))
        self.assertIn("quarantined", " ".join(benchmark.create_split(self.review, self.policy()).errors))
        self.policy_data["approved_record_ids"].remove(self.review.records[0]["record_id"])
        self.review.records[1]["component_id"] = self.review.records[2]["component_id"]
        self.policy_data["group_review_sha256"] = benchmark.fingerprint(benchmark.asdict(self.review))
        result = benchmark.create_split(self.review, self.policy())
        self.assertEqual(result.errors, [])
        pair = [r["split"] for r in result.assignments if r["record_id"] in ("A1", "A2")]
        self.assertEqual(len(set(pair)), 1)
        self.assertEqual(sum(sum(s.values()) for s in result.supports.values()), 15)

    def test_missing_class_or_insufficient_components_blocks(self):
        self.assertTrue(benchmark.create_split(self.review, self.policy(ordered_labels=["A", "B", "C"])).errors)
        self.review.records = self.review.records[:2]
        self.policy_data.update(ordered_labels=["A"], approved_record_ids=[r["record_id"] for r in self.review.records],
                                group_review_sha256=benchmark.fingerprint(benchmark.asdict(self.review)))
        self.assertIn("support", " ".join(benchmark.create_split(self.review, self.policy()).errors))


if __name__ == "__main__":
    unittest.main()
