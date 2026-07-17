from __future__ import annotations

import json
import shutil
from pathlib import Path

from .repository import LocalReviewRepository
from .server import scene_payload

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = Path(__file__).resolve().parent / "web"
LOCAL_PROOF_ROOT = PROJECT_ROOT / "proof" / "local"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "worker" / "public"


def export_demo(output_root: Path = DEFAULT_OUTPUT_ROOT) -> None:
    if output_root.exists():
        shutil.rmtree(output_root)
    shutil.copytree(WEB_ROOT, output_root)

    proof_root = output_root / "proof"
    proof_root.mkdir()
    repository = LocalReviewRepository(LOCAL_PROOF_ROOT / "decision.json", LOCAL_PROOF_ROOT)
    packet = repository.load()
    payload = scene_payload(packet, repository, write_enabled=False)
    (proof_root / "scene.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    shutil.copy2(LOCAL_PROOF_ROOT / "decision.json", proof_root / "decision.json")
    for take in packet.takes:
        shutil.copy2(LOCAL_PROOF_ROOT / f"{take.take_id}.png", proof_root / f"{take.take_id}.png")


if __name__ == "__main__":
    export_demo()
