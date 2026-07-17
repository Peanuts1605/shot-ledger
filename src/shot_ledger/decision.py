from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Take:
    take_id: str
    changed_variable: str
    changed_value: str
    prompt: str
    provider: str
    model: str
    asset_uri: str
    asset_sha256: str
    manifest_hash: str
    manifest_uri: str


@dataclass(frozen=True)
class DecisionPacket:
    scene_id: str
    brief: str
    locked_variables: dict[str, str]
    takes: tuple[Take, Take, Take]
    keeper_take_id: str
    selection_reason: str
    created_at: str
    packet_hash: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["takes"] = [
            {
                **take,
                "status": ("keeper" if take["take_id"] == self.keeper_take_id else "rejected"),
            }
            for take in payload["takes"]
        ]
        return payload


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _validate_sha256(value: str, label: str) -> None:
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{label} must be a lowercase SHA-256 hex digest")


def build_decision_packet(
    *,
    scene_id: str,
    brief: str,
    locked_variables: dict[str, str],
    takes: list[Take],
    keeper_take_id: str,
    selection_reason: str,
    created_at: str | None = None,
) -> DecisionPacket:
    if len(takes) != 3:
        raise ValueError("Shot Ledger requires exactly three controlled takes")

    take_ids = {take.take_id for take in takes}
    if len(take_ids) != 3:
        raise ValueError("take IDs must be unique")
    if keeper_take_id not in take_ids:
        raise ValueError("keeper_take_id must identify one of the three takes")
    if not selection_reason.strip():
        raise ValueError("selection_reason is required")

    changed_variables = {take.changed_variable for take in takes}
    if len(changed_variables) != 1:
        raise ValueError("all takes must test the same changed variable")

    for take in takes:
        _validate_sha256(take.asset_sha256, f"{take.take_id} asset_sha256")
        _validate_sha256(take.manifest_hash, f"{take.take_id} manifest_hash")

    timestamp = created_at or datetime.now(UTC).isoformat()
    packet_without_hash = {
        "scene_id": scene_id,
        "brief": brief,
        "locked_variables": locked_variables,
        "takes": [asdict(take) for take in takes],
        "keeper_take_id": keeper_take_id,
        "selection_reason": selection_reason.strip(),
        "created_at": timestamp,
    }
    packet_hash = hashlib.sha256(_canonical_bytes(packet_without_hash)).hexdigest()

    return DecisionPacket(
        scene_id=scene_id,
        brief=brief,
        locked_variables=locked_variables,
        takes=(takes[0], takes[1], takes[2]),
        keeper_take_id=keeper_take_id,
        selection_reason=selection_reason.strip(),
        created_at=timestamp,
        packet_hash=packet_hash,
    )


def verify_packet(packet: DecisionPacket) -> bool:
    payload = asdict(packet)
    expected_hash = payload.pop("packet_hash")
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest() == expected_hash


def decision_packet_from_dict(payload: dict[str, Any]) -> DecisionPacket:
    takes = tuple(
        Take(
            take_id=take["take_id"],
            changed_variable=take["changed_variable"],
            changed_value=take["changed_value"],
            prompt=take["prompt"],
            provider=take["provider"],
            model=take["model"],
            asset_uri=take["asset_uri"],
            asset_sha256=take["asset_sha256"],
            manifest_hash=take["manifest_hash"],
            manifest_uri=take["manifest_uri"],
        )
        for take in payload["takes"]
    )
    if len(takes) != 3:
        raise ValueError("stored packet must contain exactly three takes")

    packet = DecisionPacket(
        scene_id=payload["scene_id"],
        brief=payload["brief"],
        locked_variables=dict(payload["locked_variables"]),
        takes=(takes[0], takes[1], takes[2]),
        keeper_take_id=payload["keeper_take_id"],
        selection_reason=payload["selection_reason"],
        created_at=payload["created_at"],
        packet_hash=payload["packet_hash"],
    )
    if not verify_packet(packet):
        raise ValueError("stored decision packet failed hash verification")
    return packet


def write_packet(packet: DecisionPacket, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "decision.json"
    markdown_path = output_dir / "decision.md"

    json_path.write_text(
        json.dumps(packet.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        f"# Decision Packet: {packet.scene_id}",
        "",
        f"**Brief:** {packet.brief}",
        "",
        f"**Keeper:** {packet.keeper_take_id}",
        "",
        f"**Why it won:** {packet.selection_reason}",
        "",
        "## Controlled Takes",
        "",
    ]
    for take in packet.takes:
        status = "KEEPER" if take.take_id == packet.keeper_take_id else "REJECTED"
        lines.extend(
            [
                f"### {take.take_id}: {status}",
                "",
                f"- {take.changed_variable}: {take.changed_value}",
                f"- provider/model: {take.provider} / {take.model}",
                f"- asset SHA-256: `{take.asset_sha256}`",
                f"- manifest hash: `{take.manifest_hash}`",
                "",
            ]
        )
    lines.extend(["## Packet Integrity", "", f"`{packet.packet_hash}`", ""])
    markdown_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, markdown_path
