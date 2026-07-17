from __future__ import annotations

from .decision import DecisionPacket, build_decision_packet
from .generation_state import GenerationState


def build_reviewed_decision(
    state: GenerationState,
    *,
    keeper_take_id: str,
    selection_reason: str,
) -> DecisionPacket:
    if not state.complete:
        raise ValueError("all three takes must finish before a keeper can be sealed")

    return build_decision_packet(
        scene_id=state.scene_id,
        brief=state.brief,
        locked_variables=state.locked_variables,
        takes=state.successful_takes,
        keeper_take_id=keeper_take_id,
        selection_reason=selection_reason,
    )
