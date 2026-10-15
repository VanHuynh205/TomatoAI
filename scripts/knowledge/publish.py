"""S11 preparation-only refusal boundary. No positive publisher or runtime gate."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.knowledge.curate import (AI_ROLE, CARD_ID, CLAIM_ID, MAX_JSON_BYTES, POINTER,
                                    ROOT, CardDraft, curate_card, digest, fingerprint, keys, read_json)

EDITORIAL = ROOT / "content/phase2-healthy-v1/review-inputs.json"
SAVED_DRAFT = ROOT / "content/phase2-healthy-v1-bundle/card-draft.json"
POLICY_PATH = "artifacts/phase2/c3-policy-decision.json"
POLICY_SHA256 = "d45220c90aebf58d7d0ecf35915c063887f6fd97e3130e73410e97f40774f9fc"
EDITORIAL_SHA256 = "71081c5a62f531114ae82a935db255b8001732448003fb3dac67706bb4c507e4"
DRAFT_SHA256 = "9c7aca79597fa3bc44353fc4ec472fcee43d3b24927dd3f0d51f04fd2a623d45"
PACKET = ROOT / "artifacts/phase2/s11/approvals.pending.json"
PREPARER = {"actor": "Codex (GPT-6), AI assistant", "role": "AI preparation validator; not independent reviewer"}
REVIEWS = ("source_review", "translation_review", "rights_scope_review")
BLOCKERS = {
    "source_review_pending": "An identified human must review the exact source and context.",
    "translation_review_pending": "A separate human review must cover EN–VI, glossary, lesson and both quiz keys.",
    "rights_scope_review_pending": "Permitted use and packaging scope require documented rights evidence.",
    "publication_not_authorized": "Pinned C3 selects direction only; publication and display remain false.",
    "positive_publisher_unimplemented": "A genuine approved card and verified positive publisher/lookup remain future work.",
}


@dataclass
class KnowledgeBundle:
    """Preparation response only; never an allowed bundle consumable by S06."""
    schema_version: int = 1
    version: str = "s11-refusal-v1"
    status: str = "needs_check"
    condition_id: str | None = None
    reasons: list[str] = field(default_factory=list)
    blockers: dict[str, str] = field(default_factory=dict)
    claims: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    lesson_ids: list[str] = field(default_factory=list)
    provenance: dict = field(default_factory=dict)
    author: dict = field(default_factory=dict)


def add_reason(result, reason):
    if reason not in result.reasons:
        result.reasons.append(reason)
        result.blockers[reason] = BLOCKERS.get(reason, "Input evidence refused; resolve this reason before further review.")


def packet_schema(packet):
    keys(packet, "schema_version version draft_sha256 policy prepared_by source_review translation_review rights_scope_review")
    if (type(packet["schema_version"]) is not int or packet["schema_version"] != 1
            or packet["version"] != "s11-approvals-pending-v1" or packet["prepared_by"] != PREPARER):
        raise ValueError("schema_version_or_preparer")
    keys(packet["policy"], "path sha256")
    for value in (packet["draft_sha256"], packet["policy"]["sha256"]):
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("invalid_hash")
    if not isinstance(packet["policy"]["path"], str):
        raise ValueError("invalid_policy_path")
    for name in REVIEWS:
        review = packet[name]
        keys(review, "status actor role reviewed_sha256")
        if review["status"] not in ("pending", "approved", "rejected"):
            raise ValueError("invalid_review_status")
        for field_name in ("actor", "role", "reviewed_sha256"):
            value = review[field_name]
            if value is not None and (not isinstance(value, str) or not value.strip() or len(value) > 4000):
                raise ValueError("invalid_review_metadata")


def publish_knowledge(draft: CardDraft, approvals: Path) -> KnowledgeBundle:
    """Read bounded evidence, replay S10 and explain refusal without mutating any input.

    No metadata, status string or flag can enable publication in this delivery.
    Hashes bind local trusted baselines; they do not authenticate a human reviewer.
    """
    result = KnowledgeBundle()
    try:
        if type(draft) is not CardDraft:
            raise ValueError("not_card_draft")
        value = asdict(draft)
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
        if len(encoded.encode("utf-8")) > MAX_JSON_BYTES:
            raise ValueError("draft_size_limit")
        draft_hash = fingerprint(value)
        result.provenance["draft_sha256"] = draft_hash
    except (TypeError, ValueError, RecursionError, OverflowError):
        add_reason(result, "draft_schema_invalid")
        return result

    if draft.card_id != CARD_ID:
        add_reason(result, "card_outside_scope")
    if not isinstance(draft.claims, list) or len(draft.claims) != 1 or not isinstance(draft.claims[0], dict):
        add_reason(result, "claim_outside_scope")
    else:
        claim = draft.claims[0]
        if claim.get("card_id") != CARD_ID:
            add_reason(result, "card_outside_scope")
        if claim.get("claim_id") != CLAIM_ID or claim.get("pointer") != POINTER:
            add_reason(result, "claim_outside_scope")
        if claim.get("canonical_condition_id") != "TOM_HEALTHY":
            add_reason(result, "condition_outside_scope")
        if claim.get("kind") != "basic_care":
            add_reason(result, "chemical_claim_forbidden" if str(claim.get("kind")).startswith("chemical") else "claim_kind_outside_scope")
        if claim.get("required_context") != {}:
            add_reason(result, "contextual_claim_forbidden")
    if draft_hash != DRAFT_SHA256:
        add_reason(result, "draft_integrity_mismatch")
    trusted = None
    try:
        if digest(EDITORIAL) != EDITORIAL_SHA256:
            add_reason(result, "editorial_integrity_mismatch")
        trusted = curate_card(CARD_ID, EDITORIAL)  # Revalidates all pinned files and the sealed gate.
        if fingerprint(asdict(trusted)) != DRAFT_SHA256 or fingerprint(read_json(SAVED_DRAFT)) != DRAFT_SHA256:
            add_reason(result, "trusted_draft_integrity_mismatch")
        result.author = dict(trusted.author)
        result.provenance["publisher"] = dict(PREPARER)
        result.provenance["editorial_sha256"] = EDITORIAL_SHA256
        result.condition_id = "TOM_HEALTHY" if draft_hash == DRAFT_SHA256 else None
    except (OSError, ValueError, TypeError, RecursionError, OverflowError):
        add_reason(result, "curation_replay_failed")

    try:
        packet = read_json(Path(approvals))
    except OSError:
        add_reason(result, "approvals_unreadable")
        return result
    except (ValueError, TypeError, RecursionError, OverflowError) as error:
        add_reason(result, "approvals_size_limit" if str(error) == "json_size_limit" else "approvals_invalid_json")
        return result
    try:
        packet_schema(packet)
    except (ValueError, TypeError, KeyError):
        add_reason(result, "approvals_schema_invalid")
        return result

    if packet["draft_sha256"] != DRAFT_SHA256 or packet["draft_sha256"] != draft_hash:
        add_reason(result, "approval_draft_hash_mismatch")
    if packet["policy"]["path"] != POLICY_PATH:
        add_reason(result, "policy_path_mismatch")
    if packet["policy"]["sha256"] != POLICY_SHA256:
        add_reason(result, "policy_hash_mismatch")
    try:
        # Always use the fixed local path, never a path supplied by a packet.
        if digest(ROOT / POLICY_PATH) != POLICY_SHA256:
            add_reason(result, "policy_integrity_mismatch")
        policy = read_json(ROOT / POLICY_PATH)
        scope = policy["scope"]
        if trusted is None:
            raise ValueError("trusted_draft_unavailable")
        expected = {"draft_version": "phase2-healthy-v1", "card_id": CARD_ID, "condition_id": "TOM_HEALTHY",
                    "claim_ids": [CLAIM_ID], "lesson_id": "lesson:healthy-leaf-watering:vi:v1",
                    "draft_sha256": DRAFT_SHA256, "claim_sha256": fingerprint(trusted.claims[0]),
                    "translation_sha256": fingerprint(trusted.claims[0]["text_vi"]),
                    "glossary_sha256": fingerprint(trusted.glossary), "lesson_sha256": fingerprint(trusted.lesson)}
        if scope != expected:
            add_reason(result, "policy_scope_mismatch")
        result.provenance["policy"] = {"path": POLICY_PATH, "sha256": digest(ROOT / POLICY_PATH)}
    except (OSError, ValueError, TypeError, KeyError, RecursionError, OverflowError):
        add_reason(result, "policy_invalid")

    for name in REVIEWS:
        review = packet[name]
        if review["status"] == "pending":
            add_reason(result, name + "_pending")
            if any(review[key] is not None for key in ("actor", "role", "reviewed_sha256")):
                add_reason(result, "pending_review_has_metadata")
        elif review["status"] == "rejected":
            add_reason(result, name + "_rejected")
        else:
            actor, role = review["actor"], review["role"]
            if actor is None or role is None:
                add_reason(result, "review_actor_missing")
            elif (actor.casefold() == PREPARER["actor"].casefold()
                  or re.search(r"\b(ai|codex|gpt|assistant|llm)\b", actor + " " + role, re.I)):
                add_reason(result, "review_actor_not_independent")
            add_reason(result, "review_approval_unverified")
            if review["reviewed_sha256"] != DRAFT_SHA256:
                add_reason(result, "review_hash_mismatch")
    add_reason(result, "publication_not_authorized")
    add_reason(result, "positive_publisher_unimplemented")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approvals", type=Path, default=PACKET)
    args = parser.parse_args()
    try:
        draft = curate_card(CARD_ID, EDITORIAL)
        result = publish_knowledge(draft, args.approvals)
    except (ValueError, OSError, TypeError, RecursionError, OverflowError):
        result = KnowledgeBundle()
        add_reason(result, "curation_replay_failed")
    print(json.dumps(asdict(result), ensure_ascii=False, allow_nan=False))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
