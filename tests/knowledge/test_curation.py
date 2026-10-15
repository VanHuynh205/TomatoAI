"""Real S10 draft provenance and refusal regressions; no approval fixtures."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from scripts.knowledge import curate


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "content/phase2-healthy-v1/review-inputs.json"


class CurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "input.json"
        self.value = json.loads(INPUT.read_text(encoding="utf-8"))

    def run_draft(self):
        self.path.write_text(json.dumps(self.value, ensure_ascii=False), encoding="utf-8")
        return curate.curate_card(curate.CARD_ID, self.path)

    def test_real_tracer_exact_en_provenance_and_all_ten_refused(self):
        draft = asdict(self.run_draft())
        self.assertEqual(draft["card_id"], "pex:disease_kb/tomato/healthy.json")
        claim = draft["claims"][0]
        self.assertEqual(claim["claim_id"], "ir-claim:healthy:cultural:2")
        self.assertEqual(claim["pointer"], "/content_en/management/cultural/2")
        self.assertEqual(claim["text_en"], "Water at the base of the plant to keep foliage dry.")
        self.assertEqual(claim["text_vi"], "Tưới vào gốc cây để giữ lá khô.")
        self.assertEqual(claim["translation_sha256"], curate.fingerprint(claim["text_vi"]))
        self.assertEqual(claim["glossary_sha256"], curate.fingerprint(draft["glossary"]))
        self.assertEqual(draft["lesson_sha256"], curate.fingerprint(draft["lesson"]))
        self.assertFalse(draft["review"]["display_allowed"])
        self.assertEqual(len(draft["lookup_refusals"]), 10)
        self.assertTrue(all(r["guidance"] == [] for r in draft["lookup_refusals"]))
        self.assertEqual(draft["review"]["domain_review"], "pending")
        self.assertEqual(draft["review"]["translation_review"], "pending")

    def test_stale_file_and_editorial_hashes(self):
        for field in self.value["inputs"]:
            original = copy.deepcopy(self.value)
            self.value["inputs"][field]["sha256"] = "0" * 64
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "hash"):
                self.run_draft()
            self.value = original
        for field in ("claim_sha256", "glossary_sha256", "lesson_sha256"):
            original = copy.deepcopy(self.value)
            self.value[field] = "0" * 64
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "hash"):
                self.run_draft()
            self.value = original

    def test_exact_selection_rejects_unknown_duplicate_wrong_condition_pointer(self):
        for key, value in [("claim_id", "unknown"), ("claim_id", "ir-claim:healthy:cultural:0"),
                           ("canonical_condition_id", "TOM_EARLY_BLIGHT"), ("pointer", "/content_en/management/cultural/0")]:
            original = copy.deepcopy(self.value)
            self.value["claims"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.run_draft()
            self.value = original
        self.value["claims"].append(copy.deepcopy(self.value["claims"][0]))
        with self.assertRaises(ValueError):
            self.run_draft()
        with self.assertRaises(ValueError):
            curate.curate_card("unknown", INPUT)

    def test_editorial_references_keys_actor_and_blank_vi_rejected(self):
        mutations = [lambda v: v["claims"][0].update(text_vi=" "),
                     lambda v: v["author"].update(actor=" "),
                     lambda v: v["author"].update(role=" "),
                     lambda v: v["author"].update(date="yesterday"),
                     lambda v: v["lesson"]["questions"][0].update(correct_option_id="missing"),
                     lambda v: v["lesson"]["questions"][0].update(source_ids=["unknown"]),
                     lambda v: v["lesson"]["questions"][0].update(claim_ids=["unknown"]),
                     lambda v: v["lesson"]["questions"][0].update(explanation_vi=""),
                     lambda v: v["lesson"]["questions"].pop(),
                     lambda v: v["lesson"]["questions"][0]["choices"].append(v["lesson"]["questions"][0]["choices"][0]),
                     lambda v: v["glossary"]["terms"][0].update(source_ids=["unknown"])]
        for mutation in mutations:
            original = copy.deepcopy(self.value)
            mutation(self.value)
            self.value["glossary_sha256"] = curate.fingerprint(self.value["glossary"])
            self.value["lesson_sha256"] = curate.fingerprint(self.value["lesson"])
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.run_draft()
            self.value = original

    def test_approval_and_unsafe_context_injection(self):
        for target, key, value in [("review", "display_allowed", True), ("review", "domain_review", "expert_approved"),
                                   ("review", "translation_review", "approved"), ("claims", "required_context", {"greenhouse": True}),
                                   ("author", "role", "expert_approved"), ("lesson", "display_allowed", True)]:
            original = copy.deepcopy(self.value)
            node = self.value[target][0] if target == "claims" else self.value[target]
            node[key] = value
            with self.subTest(target=target, key=key), self.assertRaises(ValueError):
                self.run_draft()
            self.value = original

    def test_duplicate_json_keys_nan_and_oversize_rejected(self):
        for text in ('{"schema_version":1,"schema_version":1}', '{"x":NaN}', ' ' * (curate.MAX_JSON_BYTES + 1)):
            self.path.write_text(text, encoding="utf-8")
            with self.assertRaises(ValueError):
                curate.curate_card(curate.CARD_ID, self.path)

    def test_lesson_keys_and_source_hashes(self):
        draft = self.run_draft()
        self.assertEqual(len(draft.lesson["questions"]), 2)
        for q in draft.lesson["questions"]:
            self.assertIn(q["correct_option_id"], [o["id"] for o in q["choices"]])
            self.assertTrue(q["source_ids"])
        self.assertEqual([q["correct_option_id"] for q in draft.lesson["questions"]], ["b", "a"])
        observation, watering = draft.lesson["questions"]
        self.assertEqual(observation["claim_ids"], [])
        self.assertEqual(observation["card_pointers"], ["/content_en/symptoms/leaves/0", "/content_en/symptoms/leaves/2"])
        self.assertEqual(observation["project_sections"], ["Hướng dẫn có ngữ cảnh và giới hạn"])
        self.assertIn("project:localization", observation["source_ids"])
        self.assertEqual(watering["claim_ids"], [curate.CLAIM_ID])
        self.assertEqual(watering["card_pointers"], [curate.POINTER])
        self.assertTrue(draft.claims[0]["source_check_sha256"])

    def test_cli_creates_once_and_preserves_existing_paths(self):
        import time
        self.value["version"] = "phase2-healthy-v" + str(time.time_ns())
        self.path.write_text(json.dumps(self.value, ensure_ascii=False), encoding="utf-8")
        output = ROOT / "content" / (self.value["version"] + "-bundle")
        self.addCleanup(lambda: output.exists() and __import__("shutil").rmtree(output))
        command = [sys.executable, str(ROOT / "scripts/knowledge/curate.py"), "--review-inputs", str(self.path), "--output", str(output)]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        original = (output / "card-draft.json").read_bytes()
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual((output / "card-draft.json").read_bytes(), original)
        for path in [ROOT, ROOT / "data", ROOT / "content", INPUT, ROOT / "content/../data/forbidden"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                curate.write_draft(self.run_draft(), path)


if __name__ == "__main__":
    unittest.main()
