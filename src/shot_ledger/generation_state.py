from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from .decision import Take, take_from_dict

SLOT_STATUSES = {"pending", "succeeded", "failed"}


@dataclass(frozen=True)
class GenerationSlot:
    take_id: str
    changed_value: str
    status: str
    attempts: int
    take: Take | None = None
    error_code: str | None = None
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        if self.status not in SLOT_STATUSES:
            raise ValueError(f"invalid generation slot status: {self.status}")
        if self.attempts < 0:
            raise ValueError("generation attempts cannot be negative")
        if self.status == "succeeded" and self.take is None:
            raise ValueError("succeeded generation slot requires a durable take")
        if self.status != "succeeded" and self.take is not None:
            raise ValueError("only succeeded generation slots may carry a take")
        if self.status == "failed" and not self.failure_reason:
            raise ValueError("failed generation slot requires a recovery reason")


@dataclass(frozen=True)
class GenerationState:
    scene_id: str
    brief: str
    locked_variables: dict[str, str]
    changed_variable: str
    slots: tuple[GenerationSlot, GenerationSlot, GenerationSlot]
    updated_at: str
    state_hash: str

    @property
    def complete(self) -> bool:
        return all(slot.status == "succeeded" for slot in self.slots)

    @property
    def pending_take_ids(self) -> tuple[str, ...]:
        return tuple(slot.take_id for slot in self.slots if slot.status != "succeeded")

    @property
    def successful_takes(self) -> list[Take]:
        return [slot.take for slot in self.slots if slot.take is not None]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def build_generation_state(
    *,
    scene_id: str,
    brief: str,
    locked_variables: dict[str, str],
    changed_variable: str,
    slots: list[GenerationSlot],
    updated_at: str | None = None,
) -> GenerationState:
    if len(slots) != 3 or len({slot.take_id for slot in slots}) != 3:
        raise ValueError("generation state requires exactly three unique slots")
    for slot in slots:
        if slot.take and slot.take.changed_variable != changed_variable:
            raise ValueError("succeeded take does not match the controlled variable")
        if slot.take and slot.take.changed_value != slot.changed_value:
            raise ValueError("succeeded take does not match its generation slot")
    timestamp = updated_at or datetime.now(UTC).isoformat()
    payload = {
        "scene_id": scene_id,
        "brief": brief,
        "locked_variables": locked_variables,
        "changed_variable": changed_variable,
        "slots": [asdict(slot) for slot in slots],
        "updated_at": timestamp,
    }
    state_hash = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    return GenerationState(
        scene_id=scene_id,
        brief=brief,
        locked_variables=locked_variables,
        changed_variable=changed_variable,
        slots=(slots[0], slots[1], slots[2]),
        updated_at=timestamp,
        state_hash=state_hash,
    )


def verify_generation_state(state: GenerationState) -> bool:
    payload = asdict(state)
    expected_hash = payload.pop("state_hash")
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest() == expected_hash


def generation_state_from_dict(payload: dict[str, Any]) -> GenerationState:
    slots = [
        GenerationSlot(
            take_id=slot["take_id"],
            changed_value=slot["changed_value"],
            status=slot["status"],
            attempts=int(slot["attempts"]),
            take=take_from_dict(slot["take"]) if slot.get("take") else None,
            error_code=slot.get("error_code"),
            failure_reason=slot.get("failure_reason"),
        )
        for slot in payload["slots"]
    ]
    state = build_generation_state(
        scene_id=payload["scene_id"],
        brief=payload["brief"],
        locked_variables=dict(payload["locked_variables"]),
        changed_variable=payload["changed_variable"],
        slots=slots,
        updated_at=payload["updated_at"],
    )
    if state.state_hash != payload["state_hash"] or not verify_generation_state(state):
        raise ValueError("stored generation state failed hash verification")
    return state


def humanize_generation_failure(error_code: str | None, error: object) -> str:
    combined = f"{error_code or ''} {error or ''}".lower()
    if any(word in combined for word in ("moderation", "nsfw", "safety", "policy")):
        return "The provider filter stopped this take. Rephrase the object and setting, then retry."
    if any(word in combined for word in ("timeout", "rate", "429", "unavailable")):
        return "The take did not finish. Retry it without regenerating the completed siblings."
    return (
        "No durable asset was saved for this take. "
        "Retry it without regenerating the completed siblings."
    )
