from __future__ import annotations

import json
from pathlib import Path

from .decision import (
    DecisionPacket,
    build_decision_packet,
    decision_packet_from_dict,
    write_packet,
)


def load_packet(path: Path) -> DecisionPacket:
    return decision_packet_from_dict(json.loads(path.read_text(encoding="utf-8")))


def revise_decision(
    packet: DecisionPacket,
    *,
    keeper_take_id: str,
    selection_reason: str,
) -> DecisionPacket:
    return build_decision_packet(
        scene_id=packet.scene_id,
        brief=packet.brief,
        locked_variables=packet.locked_variables,
        takes=list(packet.takes),
        keeper_take_id=keeper_take_id,
        selection_reason=selection_reason,
    )


def save_packet(packet: DecisionPacket, output_dir: Path) -> Path:
    json_path, _ = write_packet(packet, output_dir)
    return json_path
