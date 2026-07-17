from __future__ import annotations

import hashlib
from pathlib import Path

from genblaze_core import Manifest, Modality, RunBuilder, StepBuilder, StepStatus
from PIL import Image, ImageDraw

from .decision import Take, build_decision_packet, verify_packet, write_packet

BRIEF = (
    "Clean tabletop campaign shot for an unbranded stainless-steel travel mug; "
    "keep shape, lid, background, and 4:5 frame fixed."
)

LIGHTING_TAKES = (
    ("take-a", "left window light", "#d8eef2", "#18343a"),
    ("take-b", "overhead softbox", "#f3efe4", "#2a302f"),
    ("take-c", "low side light", "#202a2b", "#e5b85c"),
)


def _create_take_image(path: Path, background: str, accent: str, label: str) -> str:
    image = Image.new("RGB", (800, 1000), background)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (270, 250, 545, 720), radius=46, fill="#b8c0c2", outline=accent, width=10
    )
    draw.rounded_rectangle((315, 210, 500, 285), radius=24, fill="#747d80")
    draw.ellipse((490, 365, 650, 590), outline=accent, width=24)
    draw.rectangle((90, 850, 710, 856), fill=accent)
    draw.text((90, 885), label.upper(), fill=accent)
    image.save(path, format="PNG")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    takes: list[Take] = []

    for take_id, lighting, background, accent in LIGHTING_TAKES:
        image_path = output_dir / f"{take_id}.png"
        asset_hash = _create_take_image(image_path, background, accent, lighting)
        prompt = f"{BRIEF} Lighting: {lighting}."
        step = (
            StepBuilder("local-proof", "deterministic-pillow-v1")
            .prompt(prompt)
            .modality(Modality.IMAGE)
            .params(width=800, height=1000, changed_variable="light_direction")
            .status(StepStatus.SUCCEEDED)
            .asset(image_path.resolve().as_uri(), "image/png", sha256=asset_hash)
            .build()
        )
        run_record = RunBuilder(f"shot-ledger-{take_id}").add_step(step).build()
        manifest = Manifest.from_run(run_record)
        manifest_path = output_dir / f"{take_id}.manifest.json"
        manifest_path.write_text(manifest.to_canonical_json() + "\n", encoding="utf-8")

        takes.append(
            Take(
                take_id=take_id,
                changed_variable="light_direction",
                changed_value=lighting,
                prompt=prompt,
                provider="local-proof",
                model="deterministic-pillow-v1",
                asset_uri=image_path.resolve().as_uri(),
                asset_sha256=asset_hash,
                manifest_hash=manifest.canonical_hash,
                manifest_uri=manifest_path.resolve().as_uri(),
            )
        )

    packet = build_decision_packet(
        scene_id="public-safe-travel-mug-001",
        brief=BRIEF,
        locked_variables={
            "subject": "unbranded stainless-steel travel mug",
            "frame": "4:5",
            "background": "clean tabletop",
            "camera": "eye-level product shot",
        },
        takes=takes,
        keeper_take_id="take-a",
        selection_reason=(
            "The left window light keeps the lid readable and separates the handle "
            "without changing the calm tabletop mood."
        ),
    )
    if not verify_packet(packet):
        raise RuntimeError("decision packet hash verification failed")

    json_path, markdown_path = write_packet(packet, output_dir)
    print(f"Decision JSON: {json_path}")
    print(f"Decision note: {markdown_path}")
    print(f"Packet hash: {packet.packet_hash}")
    print("Verified: True")


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    run(project_root / "proof" / "local")


if __name__ == "__main__":
    main()
