"""Offline data-contract tests. Approved records below are SYNTHETIC ONLY.

They prove lookup gating, never approval of real advice or model performance.
"""
import copy
import unittest
from pathlib import Path

from review_integration import fingerprint, load, lookup, validate_bundle


OUTPUT = Path(__file__).resolve().parents[2] / "data/TomatoAI/data/reports/integration/ir-20261014-v1"


class IntegrationContractTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load(OUTPUT / "lookup-bundle.json")

    def prediction(self, label="Tomato___healthy"):
        manifest = self.bundle["class_manifest"]
        return {"class_index": manifest["ordered_labels"].index(label), "label_original": label,
                "manifest_version": manifest["version"], "manifest_sha256": manifest["sha256"],
                "mapping_version": self.bundle["version"], "confidence": 0.9,
                "scope": "in_scope", "quality": "accepted"}

    def result(self, prediction=None):
        return lookup(self.bundle, prediction or self.prediction(), confidence_threshold=0.7)

    def approve_synthetic(self, label="Tomato___healthy"):
        """In-memory SYNTHETIC approval; source files are never written."""
        mapping = next(m for m in self.bundle["mapping"] if m["label_original"] == label)
        card = next(c for c in self.bundle["cards"] if c["record_id"] == mapping["card_id"])
        card["review"].update(domain="expert_approved", safe_for_advice=True)
        mapping["card_sha256"] = fingerprint(card)
        for claim in self.bundle["claims"]:
            if claim["card_id"] == card["record_id"]:
                claim["card_sha256"] = mapping["card_sha256"]
        claim = next(c for c in self.bundle["claims"] if c["card_id"] == card["record_id"]
                     and c["source_check"] == "source_checked_candidate")
        claim.update(domain_review="expert_approved", domain_reviewer="SYNTHETIC reviewer for tests, not a real expert",
                     translation_review="approved", translation_reviewer="SYNTHETIC translation reviewer",
                     text_vi="VĂN BẢN TỔNG HỢP ĐỂ TEST; không phải bản dịch hoặc lời khuyên đã duyệt.",
                     translation_source_sha256=claim["source_sha256"],
                     translation_claim_sha256=fingerprint(claim["text_en"]), display_allowed=True,
                     required_context={})
        claim["translation_sha256"] = fingerprint(claim["text_vi"])
        self.bundle["fixture"] = "SYNTHETIC ONLY, not approval evidence"
        return claim

    def assertBlocked(self, result, reason=None):
        self.assertEqual(result["status"], "needs_check")
        self.assertEqual(result["guidance"], [])
        if reason:
            self.assertEqual(result["reason"], reason)

    def test_all_ten_real_classes_reference_present_and_blocked(self):
        validate_bundle(self.bundle)
        self.assertEqual(len(self.bundle["mapping"]), 10)
        self.assertEqual(len(self.bundle["cards"]), 17)
        for mapping in self.bundle["mapping"]:
            with self.subTest(label=mapping["label_original"]):
                expected = "mapping_not_verified" if mapping["relation"] == "candidate_pending" else "card_not_approved"
                self.assertBlocked(self.result(self.prediction(mapping["label_original"])), expected)

    def test_synthetic_approved_nonchemical_guidance_has_provenance(self):
        claim = self.approve_synthetic("Tomato___Early_blight")
        result = self.result(self.prediction("Tomato___Early_blight"))
        self.assertEqual(result["status"], "guidance_allowed")
        self.assertEqual(len(result["guidance"]), 1)
        self.assertEqual(result["guidance"][0]["claim_id"], claim["claim_id"])
        self.assertEqual(result["guidance"][0]["source_sha256"], claim["source_sha256"])
        self.assertEqual(result["guidance"][0]["version"], "ir-20261014-v1")

    def test_invalid_class_indices(self):
        for index in [-1, 10, True, 0.0, "0", None]:
            with self.subTest(index=index):
                p = self.prediction(); p["class_index"] = index
                self.assertBlocked(self.result(p), "invalid_class_index")

    def test_changed_order_and_recomputed_manifest_reject_old_prediction(self):
        p = self.prediction()
        self.bundle["class_manifest"]["ordered_labels"].reverse()
        manifest = self.bundle["class_manifest"]
        manifest["sha256"] = fingerprint({k: v for k, v in manifest.items() if k != "sha256"})
        self.assertBlocked(self.result(p), "manifest_mismatch")

    def test_modified_manifest_without_hash(self):
        self.bundle["class_manifest"]["ordered_labels"].reverse()
        self.assertBlocked(self.result(), "invalid_bundle")

    def test_versions_and_hash_mismatch(self):
        for field in ["manifest_version", "manifest_sha256", "mapping_version"]:
            with self.subTest(field=field):
                p = self.prediction(); p[field] = "incorrect"
                self.assertBlocked(self.result(p), "mapping_version_mismatch" if field == "mapping_version" else "manifest_mismatch")

    def test_missing_or_duplicate_card(self):
        original = copy.deepcopy(self.bundle)
        self.bundle["cards"].pop()
        self.assertBlocked(self.result(), "invalid_bundle")
        self.bundle = original
        self.bundle["cards"].append(copy.deepcopy(self.bundle["cards"][0]))
        self.assertBlocked(self.result(), "invalid_bundle")

    def test_duplicate_mapping_and_claim(self):
        original = copy.deepcopy(self.bundle)
        self.bundle["mapping"].append(copy.deepcopy(self.bundle["mapping"][0]))
        self.assertBlocked(self.result(), "invalid_bundle")
        self.bundle = original
        self.bundle["claims"].append(copy.deepcopy(self.bundle["claims"][0]))
        self.assertBlocked(self.result(), "invalid_bundle")

    def test_unknown_label(self):
        p = self.prediction(); p["label_original"] = "unseen"
        self.assertBlocked(self.result(p), "unknown_or_inconsistent_label")

    def test_ambiguous_mapping(self):
        self.approve_synthetic()
        next(m for m in self.bundle["mapping"] if m["canonical_condition_id"] == "TOM_HEALTHY")["relation"] = "ambiguous"
        self.assertBlocked(self.result(), "mapping_not_verified")

    def test_missing_claim_source_evidence(self):
        claim = self.approve_synthetic(); claim["evidence"] = []
        self.assertBlocked(self.result(), "no_approved_vi_claims")

    def test_unapproved_domain_even_with_approved_translation(self):
        claim = self.approve_synthetic(); claim["domain_review"] = "pending"
        self.assertBlocked(self.result(), "no_approved_vi_claims")

    def test_unapproved_translation_even_with_approved_domain(self):
        claim = self.approve_synthetic(); claim["translation_review"] = "draft"
        self.assertBlocked(self.result(), "no_approved_vi_claims")

    def test_healthy_never_treatment(self):
        claim = self.approve_synthetic(); claim["kind"] = "nonchemical_cultural"
        self.assertBlocked(self.result(), "no_approved_vi_claims")

    def test_healthy_wrong_card_even_if_hash_updated(self):
        healthy = next(m for m in self.bundle["mapping"] if m["canonical_condition_id"] == "TOM_HEALTHY")
        other = next(m for m in self.bundle["mapping"] if m["canonical_condition_id"] == "TOM_EARLY_BLIGHT")
        for key in ["card_id", "card_sha256", "source_sha256", "disease_id_original"]:
            healthy[key] = other[key]
        self.assertBlocked(self.result(), "invalid_bundle")

    def test_low_confidence_external_scope_quality_and_invalid_score(self):
        self.approve_synthetic()
        for field, value in [("confidence", 0.2), ("scope", "out_of_scope"), ("scope", "unverified"), ("quality", "blurred")]:
            with self.subTest(field=field, value=value):
                p = self.prediction(); p[field] = value
                self.assertBlocked(self.result(p), "quality_scope_or_confidence")
        for score in [float("nan"), float("inf"), -0.1, 1.1, True, "0.9", 10 ** 1000]:
            p = self.prediction(); p["confidence"] = score
            self.assertBlocked(self.result(p), "invalid_confidence")

    def test_topk_does_not_mix_conditions(self):
        self.approve_synthetic()
        self.approve_synthetic("Tomato___Early_blight")
        p = self.prediction(); p["top_k"] = [{"label": "Tomato___Early_blight", "confidence": 0.88}]
        result = self.result(p)
        self.assertEqual(result["canonical_condition_id"], "TOM_HEALTHY")
        self.assertEqual(len(result["guidance"]), 1)
        self.assertTrue(result["guidance"][0]["claim_id"].startswith("ir-claim:healthy:"))

    def test_chemical_and_contextual_claims_stay_hidden(self):
        claim = self.approve_synthetic("Tomato___Early_blight")
        claim["kind"] = "chemical_or_mixed"
        self.assertBlocked(self.result(self.prediction("Tomato___Early_blight")), "no_approved_vi_claims")
        claim["kind"] = "nonchemical_cultural"; claim["required_context"] = {"greenhouse": True}
        self.assertBlocked(self.result(self.prediction("Tomato___Early_blight")), "no_approved_vi_claims")

    def test_stale_source_card_translation_and_claim_hashes(self):
        for field in ["source_sha256", "card_sha256", "translation_source_sha256", "translation_claim_sha256", "translation_sha256"]:
            with self.subTest(field=field):
                self.setUp(); claim = self.approve_synthetic(); claim[field] = "stale"
                self.assertBlocked(self.result(), "no_approved_vi_claims")
        self.setUp(); claim = self.approve_synthetic(); claim["text_en"] += " invented advice"
        claim["translation_claim_sha256"] = fingerprint(claim["text_en"])
        self.assertBlocked(self.result(), "invalid_bundle")

    def test_missing_review_actor_or_bad_evidence_metadata(self):
        for field in ["domain_reviewer", "translation_reviewer"]:
            self.setUp(); claim = self.approve_synthetic(); claim[field] = None
            self.assertBlocked(self.result(), "no_approved_vi_claims")
        self.setUp(); claim = self.approve_synthetic(); claim["evidence"] = [{"url": "http://example.com"}]
        self.assertBlocked(self.result(), "no_approved_vi_claims")
        self.setUp(); claim = self.approve_synthetic(); claim["evidence"] = ["malformed"]
        self.assertBlocked(self.result(), "invalid_bundle")

    def test_input_object_not_mutated_and_real_flags_unchanged(self):
        before = copy.deepcopy(self.bundle)
        self.result()
        self.assertEqual(self.bundle, before)
        self.assertTrue(all(c["review"]["safe_for_advice"] is False for c in self.bundle["cards"]))

    def test_registry_points_to_reviewed_run_and_originals_match(self):
        project = OUTPUT.parents[5]
        root = project / "data/TomatoAI/data"
        registry = load(root / "dataset-registry.json")
        self.assertEqual(self.bundle["class_manifest"]["dataset_run"], registry["datasets"]["PlantVillage"]["current_run"])
        cards_path = root / registry["datasets"]["PlantExpertVQA-tomato"]["processed"] / "cards"
        actual = {c["record_id"]: c for c in self.bundle["cards"]}
        for path in cards_path.glob("*.json"):
            card = load(path)
            self.assertEqual(card, actual[card["record_id"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
