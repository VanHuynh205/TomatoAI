"""S10 preparation only: one hash-bound AI draft; no approval or runtime API."""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Preparation may reuse this sealed validator. Runtime extraction belongs to S06.
sys.path.insert(0, str(ROOT / "scripts/data"))
from review_integration import fingerprint, load, lookup, validate_bundle  # noqa: E402

CARD_ID = "pex:disease_kb/tomato/healthy.json"
CLAIM_ID = "ir-claim:healthy:cultural:2"
POINTER = "/content_en/management/cultural/2"
AI_ROLE = "AI drafting and source-checking assistant; not independent reviewer"
MAX_JSON_BYTES = 2 * 1024 * 1024
INPUT_PATHS = {
    "raw": "data/TomatoAI/data/raw/plantexpert/disease_kb/tomato/healthy.json",
    "card": "data/TomatoAI/data/processed/plantexpert-tomato/pex-b3da04d66a031756/cards/healthy.json",
    "integration": "data/TomatoAI/data/reports/integration/ir-20261014-v1/lookup-bundle.json",
    "seal": "data/TomatoAI/data/reports/integration/ir-20261014-v1/artifact-seal.json",
    "registry": "data/TomatoAI/data/dataset-registry.json",
    "rights": "docs/development/assets-rights.json",
    "validator": "scripts/data/review_integration.py",
    "localization": "planning/tomato-desktop/knowledge-localization-edtech.md",
}
PENDING = {"status": "draft", "domain_review": "pending", "translation_review": "pending",
           "domain_reviewer": None, "translation_reviewer": None, "display_allowed": False,
           "c3": "pending", "redistribution": "pending"}


@dataclass
class CardDraft:
    schema_version: int
    version: str
    card_id: str
    provenance: dict
    author: dict
    claims: list
    glossary: dict
    lesson: dict
    lesson_sha256: str
    review: dict
    lookup_bundle: dict
    lookup_refusals: list


def digest(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    if path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError("json_size_limit")
    value = load(path)  # Existing loader rejects duplicate keys.
    fingerprint(value)  # Reject NaN/Infinity, including nested values.
    return value


def keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected.split()):
        raise ValueError("invalid_fields: " + expected)


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 4000:
        raise ValueError("empty_or_invalid_text")


def refs(value, allowed, required=True):
    if not isinstance(value, list) or (required and not value) or any(not isinstance(x, str) for x in value):
        raise ValueError("invalid_references")
    if len(set(value)) != len(value) or not set(value) <= set(allowed):
        raise ValueError("unknown_or_duplicate_reference")


def lesson_refs(item, evidence):
    refs(item["source_ids"], [*evidence, "card:healthy", "project:localization"])
    refs(item["claim_ids"], [CLAIM_ID], required=False)
    refs(item["card_pointers"], [POINTER, "/content_en/symptoms/leaves/0", "/content_en/symptoms/leaves/2"], required=False)
    refs(item["project_sections"], ["Hướng dẫn có ngữ cảnh và giới hạn"], required=False)
    if not (item["claim_ids"] or item["card_pointers"] or item["project_sections"]):
        raise ValueError("lesson_missing_source_locator")
    if ((item["card_pointers"] and "card:healthy" not in item["source_ids"])
            or (item["project_sections"] and "project:localization" not in item["source_ids"])
            or (item["claim_ids"] and "healthy" not in item["source_ids"])):
        raise ValueError("lesson_source_locator_mismatch")


def curate_card(card_id: str, review_inputs: Path) -> CardDraft:
    """Read bounded, exact inputs and return a draft without writing anything."""
    try:
        return _curate(card_id, Path(review_inputs))
    except (KeyError, TypeError, IndexError, AttributeError, StopIteration, OSError) as error:
        raise ValueError(f"invalid_curation_input: {error}") from error


def _curate(card_id, review_inputs):
    if card_id != CARD_ID:
        raise ValueError("unsupported_card_id")
    v = read_json(review_inputs)
    keys(v, "schema_version version card_id author review inputs claim_sha256 claims glossary glossary_sha256 source_checks lesson lesson_sha256")
    if type(v["schema_version"]) is not int or v["schema_version"] != 1 or v["card_id"] != card_id:
        raise ValueError("schema_or_card_id")
    if not isinstance(v["version"], str) or not re.fullmatch(r"phase2-healthy-v[1-9][0-9]*", v["version"]):
        raise ValueError("invalid_version")
    if v["review"] != PENDING:
        raise ValueError("approval_not_permitted")
    keys(v["author"], "actor role date")
    text(v["author"]["actor"])
    if v["author"]["role"] != AI_ROLE:
        raise ValueError("author_role_must_be_ai_draft")
    if date.fromisoformat(v["author"]["date"]).isoformat() != v["author"]["date"]:
        raise ValueError("invalid_author_date")
    keys(v["inputs"], " ".join(INPUT_PATHS))
    for name, path in INPUT_PATHS.items():
        pin = v["inputs"][name]
        keys(pin, "path sha256")
        if pin["path"] != path or digest(ROOT / path) != pin["sha256"]:
            raise ValueError(f"input_hash_or_path: {name}")
    bundle = read_json(ROOT / INPUT_PATHS["integration"])
    validate_bundle(bundle)
    seal = read_json(ROOT / INPUT_PATHS["seal"])
    for entry in seal["files"]:
        path = (ROOT / entry["path"]).resolve()
        if not path.is_relative_to(ROOT / "data/TomatoAI/data/reports/integration/ir-20261014-v1"):
            raise ValueError("seal_path_outside_integration")
        if digest(path) != entry["sha256"] or path.stat().st_size != entry["bytes"]:
            raise ValueError("integration_seal_hash: " + entry["path"])
    card = read_json(ROOT / INPUT_PATHS["card"])
    raw = read_json(ROOT / INPUT_PATHS["raw"])
    if (card["record_id"] != card_id or card["content_en"] != raw
            or card["source"]["sha256"] != v["inputs"]["raw"]["sha256"]
            or card != next(c for c in bundle["cards"] if c["record_id"] == card_id)):
        raise ValueError("raw_card_integration_hash_alignment")
    registry = read_json(ROOT / INPUT_PATHS["registry"])
    if registry["datasets"]["PlantExpertVQA-tomato"]["current_run"] != "pex-b3da04d66a031756":
        raise ValueError("registry_run_mismatch")
    rights = read_json(ROOT / INPUT_PATHS["rights"])
    asset = next(a for a in rights["assets"] if a["id"] == card_id)
    if asset["source_sha256"] != card["source"]["sha256"]:
        raise ValueError("rights_source_hash")
    if not isinstance(v["claims"], list) or len(v["claims"]) != 1:
        raise ValueError("exactly_one_selected_claim")
    chosen = v["claims"][0]
    keys(chosen, "claim_id canonical_condition_id pointer text_vi required_context term_ids source_ids")
    if (chosen["claim_id"] != CLAIM_ID or chosen["pointer"] != POINTER
            or chosen["canonical_condition_id"] != "TOM_HEALTHY" or chosen["required_context"] != {}):
        raise ValueError("exact_claim_selection_or_context")
    text(chosen["text_vi"])
    claim = next(c for c in bundle["claims"] if c["claim_id"] == CLAIM_ID)
    if (claim["source_check"] != "source_checked_candidate" or claim["kind"] != "basic_care"
            or claim["card_id"] != card_id or claim["canonical_condition_id"] != "TOM_HEALTHY"
            or claim["card_sha256"] != fingerprint(card) or claim["source_sha256"] != card["source"]["sha256"]
            or claim["pointer"] != POINTER or v["claim_sha256"] != fingerprint(claim)):
        raise ValueError("claim_hash_or_candidate")
    evidence = {e["source_id"]: e for e in claim["evidence"]}
    refs(chosen["source_ids"], evidence)
    if not isinstance(v["source_checks"], list) or len(v["source_checks"]) != 1:
        raise ValueError("one_source_check_required")
    check = v["source_checks"][0]
    keys(check, "source_id url sections accessed actor role note limits")
    if (check["source_id"] not in evidence or check["url"] != evidence[check["source_id"]]["url"]
            or check["role"] != AI_ROLE or check["actor"] != v["author"]["actor"]
            or check["accessed"] != v["author"]["date"]):
        raise ValueError("source_check_identity")
    text(check["note"]); text(check["limits"])
    refs(check["sections"], ["Watering", "Diseases"])
    g = v["glossary"]
    keys(g, "version status terms")
    text(g["version"])
    if g["status"] != "draft" or fingerprint(g) != v["glossary_sha256"]:
        raise ValueError("glossary_hash_or_status")
    if not isinstance(g["terms"], list) or not g["terms"]:
        raise ValueError("glossary_terms_required")
    term_ids = []
    for term in g["terms"]:
        keys(term, "id en vi scientific_name source_ids")
        for name in ("id", "en", "vi"):
            text(term[name])
        if term["scientific_name"] is not None:
            text(term["scientific_name"])
        refs(term["source_ids"], [*evidence, "card:healthy", "project:localization"])
        term_ids.append(term["id"])
    if len(set(term_ids)) != len(term_ids):
        raise ValueError("duplicate_term_id")
    refs(chosen["term_ids"], term_ids)
    lesson = v["lesson"]
    keys(lesson, "lesson_id status display_allowed title_vi objectives sections questions")
    text(lesson["lesson_id"]); text(lesson["title_vi"])
    if lesson["status"] != "draft" or lesson["display_allowed"] is not False or fingerprint(lesson) != v["lesson_sha256"]:
        raise ValueError("lesson_hash_or_approval")
    if not isinstance(lesson["objectives"], list) or not lesson["objectives"]:
        raise ValueError("lesson_objectives")
    for objective in lesson["objectives"]:
        text(objective)
    if not isinstance(lesson["sections"], list) or len(lesson["sections"]) != 3:
        raise ValueError("lesson_sections")
    for section in lesson["sections"]:
        keys(section, "id text_vi source_ids card_pointers project_sections claim_ids")
        text(section["id"]); text(section["text_vi"])
        lesson_refs(section, evidence)
    if len({s["id"] for s in lesson["sections"]}) != 3:
        raise ValueError("duplicate_section_id")
    questions = lesson["questions"]
    if not isinstance(questions, list) or len(questions) != 2:
        raise ValueError("exactly_two_questions")
    for question in questions:
        keys(question, "question_id prompt_vi choices correct_option_id explanation_vi source_ids card_pointers project_sections claim_ids")
        for name in ("question_id", "prompt_vi", "explanation_vi"):
            text(question[name])
        lesson_refs(question, evidence)
        choices = question["choices"]
        if not isinstance(choices, list) or not 2 <= len(choices) <= 6:
            raise ValueError("question_choices")
        for choice in choices:
            keys(choice, "id text_vi")
            text(choice["id"]); text(choice["text_vi"])
        ids = [c["id"] for c in choices]
        if (len(set(ids)) != len(ids) or len({c["text_vi"] for c in choices}) != len(choices)
                or question["correct_option_id"] not in ids):
            raise ValueError("invalid_question_key_or_duplicate_choice")
    if questions[0]["question_id"] == questions[1]["question_id"]:
        raise ValueError("duplicate_question_id")
    claim = copy.deepcopy(claim)
    claim.update(text_vi=chosen["text_vi"], translation_review="pending", display_allowed=False,
                 translation_source_sha256=card["source"]["sha256"], translation_claim_sha256=fingerprint(claim["text_en"]),
                 translation_sha256=fingerprint(chosen["text_vi"]), glossary_sha256=fingerprint(g),
                 source_check_sha256=fingerprint(v["source_checks"]), lesson_sha256=fingerprint(lesson),
                 term_ids=chosen["term_ids"], author=v["author"])
    bundle["version"] = v["version"]
    bundle["claims"] = [claim if c["claim_id"] == CLAIM_ID else c for c in bundle["claims"]]
    validate_bundle(bundle)
    refusals = []
    manifest = bundle["class_manifest"]
    for index, label in enumerate(manifest["ordered_labels"]):
        prediction = {"class_index": index, "label_original": label, "manifest_version": manifest["version"],
                      "manifest_sha256": manifest["sha256"], "mapping_version": bundle["version"],
                      "confidence": 0.9, "scope": "in_scope", "quality": "accepted"}
        result = lookup(bundle, prediction, confidence_threshold=0.7)  # Historical fixture value; not production policy.
        if result["guidance"] != [] or result["status"] != "needs_check":
            raise ValueError("unexpected_guidance_approval")
        refusals.append(dict(result, label_original=label))
    provenance = {"inputs": v["inputs"], "review_inputs_sha256": digest(review_inputs),
                  "source_sha256": card["source"]["sha256"], "card_sha256": fingerprint(card),
                  "claim_sha256": v["claim_sha256"], "glossary_sha256": fingerprint(g),
                  "source_checks": v["source_checks"], "source_checks_sha256": fingerprint(v["source_checks"]),
                  "sources": {**evidence, "card:healthy": {"path": INPUT_PATHS["card"], "sha256": fingerprint(card)},
                              "project:localization": v["inputs"]["localization"]},
                  "rights": asset, "limit": "AI draft; healthy is a leaf class only; C3 pending; no learning-effectiveness evidence"}
    return CardDraft(1, v["version"], card_id, provenance, v["author"], [claim], g, lesson,
                     fingerprint(lesson), dict(PENDING), bundle, refusals)


def write_draft(draft: CardDraft, output: Path):
    """Create content/<version>-bundle beside editorial <version>; never overwrite."""
    output = Path(output).resolve()
    if (output.parent != (ROOT / "content").resolve() or output.name != draft.version + "-bundle"
            or output.exists()):
        raise ValueError("output_requires_new_content_version_directory")
    payload = json.dumps(asdict(draft), ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    # Atomic directory creation refuses collisions; all validation precedes writing.
    output.mkdir()
    try:
        with (output / "card-draft.json").open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
    except OSError:
        (output / "card-draft.json").unlink(missing_ok=True)
        output.rmdir()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--card-id", default=CARD_ID)
    parser.add_argument("--review-inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="New content/<version>-bundle directory; absent means read-only validation")
    args = parser.parse_args()
    try:
        draft = curate_card(args.card_id, args.review_inputs)
        if args.output:
            write_draft(draft, args.output)
        print(json.dumps({"version": draft.version, "card_id": draft.card_id, "claims": len(draft.claims),
                          "questions": len(draft.lesson["questions"]), "refused_classes": len(draft.lookup_refusals),
                          "display_allowed": False, "c3": "pending", "output": str(args.output) if args.output else None}))
    except (ValueError, OSError) as error:
        parser.exit(2, f"curation refused: {error}\n")


if __name__ == "__main__":
    main()
