"""S11 refusal boundary on the genuine pending S10 card; no approved fixture."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from scripts.knowledge import curate, publish


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "artifacts/phase2/s11/approvals.pending.json"


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.draft = curate.curate_card(curate.CARD_ID, ROOT / "content/phase2-healthy-v1/review-inputs.json")

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "approvals.json"
        self.packet = curate.read_json(PACKET)

    def refuse(self, expected, draft=None, raw=None):
        self.path.write_text(raw if raw is not None else json.dumps(self.packet, ensure_ascii=False), encoding="utf-8")
        value = draft if draft is not None else copy.deepcopy(self.draft)
        before = copy.deepcopy(value)
        packet_bytes = self.path.read_bytes()
        result = publish.publish_knowledge(value, self.path)
        self.assertEqual(result.status, "needs_check")
        self.assertEqual((result.claims, result.sources, result.lesson_ids), ([], [], []))
        self.assertIn(expected, result.reasons)
        self.assertEqual(value, before)
        self.assertEqual(self.path.read_bytes(), packet_bytes)
        return result

    def test_genuine_pending_dossier_reports_independent_blockers(self):
        result = self.refuse("source_review_pending")
        self.assertEqual(result.reasons, ["source_review_pending", "translation_review_pending",
                                         "rights_scope_review_pending", "publication_not_authorized",
                                         "positive_publisher_unimplemented"])
        self.assertEqual(set(result.blockers), set(result.reasons))
        self.assertEqual(result.provenance["draft_sha256"], self.packet["draft_sha256"])
        self.assertEqual(result.provenance["policy"]["sha256"], self.packet["policy"]["sha256"])
        self.assertEqual(result.author["role"], curate.AI_ROLE)

    def test_missing_and_invalid_approvals_are_typed(self):
        result = publish.publish_knowledge(self.draft, self.path)
        self.assertIn("approvals_unreadable", result.reasons)
        for raw, reason in [("{", "approvals_invalid_json"), ('{"x":1,"x":2}', "approvals_invalid_json"),
                            ('{"x":NaN}', "approvals_invalid_json"), ('{"x":Infinity}', "approvals_invalid_json"),
                            (" " * (curate.MAX_JSON_BYTES + 1), "approvals_size_limit"),
                            ("[]", "approvals_schema_invalid"), ("null", "approvals_schema_invalid")]:
            with self.subTest(reason=reason, sample=raw[:30]):
                self.refuse(reason, raw=raw)

    def test_exact_schema_and_no_skip_flag(self):
        for mutation in [lambda p: p.update(schema_version=True), lambda p: p.update(schema_version=2),
                         lambda p: p.update(version="unknown"), lambda p: p.update(skip_review=True),
                         lambda p: p.update(policy=None), lambda p: p["source_review"].update(extra=True)]:
            original = copy.deepcopy(self.packet)
            mutation(self.packet)
            with self.subTest(mutation=mutation):
                self.refuse("approvals_schema_invalid")
            self.packet = original

    def test_policy_and_draft_pins_cannot_be_replaced(self):
        for field, value, reason in [("path", "../../external-policy.json", "policy_path_mismatch"),
                                      ("sha256", "0" * 64, "policy_hash_mismatch")]:
            original = copy.deepcopy(self.packet)
            self.packet["policy"][field] = value
            self.refuse(reason)
            self.packet = original
        self.packet["draft_sha256"] = "0" * 64
        self.refuse("approval_draft_hash_mismatch")

    def test_full_draft_hash_catches_nested_content_and_metadata_drift(self):
        mutations = [lambda d: d.claims[0].update(text_en="Changed EN"),
                     lambda d: d.claims[0].update(text_vi="Đã đổi nghĩa"),
                     lambda d: d.glossary["terms"][0].update(vi="đã đổi"),
                     lambda d: d.lesson["questions"][0].update(correct_option_id="a"),
                     lambda d: d.lookup_bundle["claims"][0].update(reason="changed"),
                     lambda d: d.lookup_refusals[0].update(status="allowed"),
                     lambda d: d.provenance.update(source_sha256="0" * 64),
                     lambda d: d.review.update(display_allowed=True)]
        for mutation in mutations:
            draft = copy.deepcopy(self.draft)
            mutation(draft)
            with self.subTest(mutation=mutation):
                self.refuse("draft_integrity_mismatch", draft)

    def test_specific_unsafe_content_refusals_even_with_other_blockers(self):
        for field, value, reason in [("kind", "chemical_or_mixed", "chemical_claim_forbidden"),
                                      ("required_context", {"greenhouse": True}, "contextual_claim_forbidden"),
                                      ("canonical_condition_id", "TOM_EARLY_BLIGHT", "condition_outside_scope"),
                                      ("claim_id", "unknown", "claim_outside_scope"),
                                      ("card_id", "unknown", "card_outside_scope")]:
            draft = copy.deepcopy(self.draft)
            draft.claims[0][field] = value
            with self.subTest(field=field):
                result = self.refuse(reason, draft)
                self.assertIn("draft_integrity_mismatch", result.reasons)
                self.assertIn("source_review_pending", result.reasons)
        draft = copy.deepcopy(self.draft)
        draft.card_id = "unknown"
        self.refuse("card_outside_scope", draft)

    def test_negative_approval_metadata_cannot_approve_or_self_review(self):
        # Only negative metadata is edited; the card always remains the genuine pending draft.
        for review in ("source_review", "translation_review", "rights_scope_review"):
            for actor, role, reason in [(None, None, "review_actor_missing"),
                                         (self.draft.author["actor"], "student", "review_actor_not_independent"),
                                         ("AI assistant", "AI", "review_actor_not_independent"),
                                         ("Codex", "human", "review_actor_not_independent"),
                                         ("Unverified metadata", "student", "review_approval_unverified")]:
                original = copy.deepcopy(self.packet)
                self.packet[review].update(status="approved", actor=actor, role=role,
                                           reviewed_sha256=self.packet["draft_sha256"])
                with self.subTest(review=review, actor=actor):
                    self.refuse(reason)
                self.packet = original
        self.packet["source_review"].update(status="expert_approved")
        self.refuse("approvals_schema_invalid")

    def test_pending_review_metadata_and_stale_review_hash_rejected(self):
        self.packet["source_review"]["actor"] = "Unverified metadata"
        self.refuse("pending_review_has_metadata")
        self.packet["source_review"].update(status="approved", role="student", reviewed_sha256="0" * 64)
        self.refuse("review_hash_mismatch")

    def test_invalid_draft_is_typed_and_empty(self):
        for value in (None, {}, "draft"):
            result = publish.publish_knowledge(value, PACKET)
            self.assertIn("draft_schema_invalid", result.reasons)
            self.assertEqual((result.claims, result.sources, result.lesson_ids), ([], [], []))
        draft = copy.deepcopy(self.draft)
        draft.claims = []
        self.refuse("claim_outside_scope", draft)
        draft = copy.deepcopy(self.draft)
        draft.lesson["extra"] = float("nan")
        result = publish.publish_knowledge(draft, PACKET)
        self.assertIn("draft_schema_invalid", result.reasons)
        for field, value in [("author", None), ("provenance", []), ("lesson", "invalid"),
                             ("claims", [None]), ("claims", "invalid")]:
            draft = copy.deepcopy(self.draft)
            setattr(draft, field, value)
            with self.subTest(field=field):
                self.refuse("draft_integrity_mismatch", draft)
        draft = copy.deepcopy(self.draft)
        draft.lesson["extra"] = "x" * curate.MAX_JSON_BYTES
        result = publish.publish_knowledge(draft, PACKET)
        self.assertIn("draft_schema_invalid", result.reasons)

    def test_rejected_evidence_and_nonselected_kind_stay_blocked(self):
        self.packet["rights_scope_review"]["status"] = "rejected"
        self.refuse("rights_scope_review_rejected")
        draft = copy.deepcopy(self.draft)
        draft.claims[0]["kind"] = "nonchemical_cultural"
        self.refuse("claim_kind_outside_scope", draft)

    def test_cli_stdout_refusal_and_inputs_unchanged(self):
        protected = [PACKET, ROOT / "artifacts/phase2/c3-policy-decision.json",
                     ROOT / "content/phase2-healthy-v1/review-inputs.json",
                     ROOT / "content/phase2-healthy-v1-bundle/card-draft.json"]
        before = {path: path.read_bytes() for path in protected}
        command = [sys.executable, str(ROOT / "scripts/knowledge/publish.py")]
        for args, reason in [([], "source_review_pending"),
                             (["--approvals", str(self.path)], "approvals_unreadable")]:
            completed = subprocess.run(command + args, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(completed.stderr, "")
            result = json.loads(completed.stdout)
            self.assertIn(reason, result["reasons"])
            self.assertEqual((result["claims"], result["sources"], result["lesson_ids"]), ([], [], []))
        self.assertEqual({path: path.read_bytes() for path in protected}, before)
        help_result = subprocess.run(command + ["--help"], capture_output=True, text=True)
        self.assertNotIn("--output", help_result.stdout)


if __name__ == "__main__":
    unittest.main()
