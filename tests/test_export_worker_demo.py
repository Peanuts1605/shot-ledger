from __future__ import annotations

import json

from shot_ledger.export_worker_demo import export_demo
from shot_ledger.proof_local import run as generate_local_proof


def test_worker_demo_export_is_read_only_and_visibly_synthetic(tmp_path):
    output = tmp_path / "public"
    local_proof = tmp_path / "local-proof"

    generate_local_proof(local_proof)
    export_demo(output, local_proof)

    scene = json.loads((output / "proof" / "scene.json").read_text(encoding="utf-8"))
    assert scene["write_enabled"] is False
    assert "Synthetic local demonstration" in scene["proof_scope"]
    assert scene["media_integrity"]["verified"] is True
    assert all(not take["asset_uri"].startswith("file:") for take in scene["takes"])
    assert all(not take["manifest_uri"].startswith("file:") for take in scene["takes"])
    assert scene["takes"][0]["asset_uri"].startswith("synthetic://")
    assert scene["takes"][0]["manifest_uri"].startswith("synthetic://")
    assert (output / "index.html").is_file()
    assert (output / "proof" / "take-a.png").is_file()
    assert (output / "proof" / "take-a.manifest.json").is_file()

    decision = json.loads((output / "proof" / "decision.json").read_text(encoding="utf-8"))
    assert decision["packet_hash"] == scene["packet_hash"]
    assert all(not take["asset_uri"].startswith("file:") for take in decision["takes"])
