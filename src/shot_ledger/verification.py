from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass

from genblaze_core import Manifest

from .decision import DecisionPacket, Take
from .repository import ReviewRepository


@dataclass(frozen=True)
class TakeVerification:
    take_id: str
    asset_hash_matches: bool
    manifest_hash_matches: bool
    manifest_valid: bool
    provenance_matches: bool
    error: str | None = None

    @property
    def verified(self) -> bool:
        return (
            self.error is None
            and self.asset_hash_matches
            and self.manifest_hash_matches
            and self.manifest_valid
            and self.provenance_matches
        )

    def to_dict(self) -> dict[str, object]:
        return {**asdict(self), "verified": self.verified}


@dataclass(frozen=True)
class SceneVerification:
    takes: tuple[TakeVerification, ...]

    @property
    def verified(self) -> bool:
        return len(self.takes) == 3 and all(take.verified for take in self.takes)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "verified" if self.verified else "not verified",
            "verified": self.verified,
            "takes": [take.to_dict() for take in self.takes],
        }


def _manifest_matches_take(manifest: Manifest, take: Take) -> bool:
    for step in manifest.run.steps:
        hashes = {asset.sha256 for asset in step.assets}
        if take.asset_sha256 not in hashes:
            continue
        return (
            step.provider == take.provider
            and step.model == take.model
            and step.prompt == take.prompt
            and all(step.params.get(key) == value for key, value in take.parameters.items())
        )
    return False


def verify_take(repository: ReviewRepository, take: Take) -> TakeVerification:
    try:
        asset_hash_matches = (
            hashlib.sha256(repository.read_asset(take)).hexdigest() == take.asset_sha256
        )
        manifest = Manifest.model_validate_json(repository.read_manifest(take))
        manifest_hash_matches = manifest.canonical_hash == take.manifest_hash
        manifest_valid = manifest.verify()
        provenance_matches = _manifest_matches_take(manifest, take)
        return TakeVerification(
            take_id=take.take_id,
            asset_hash_matches=asset_hash_matches,
            manifest_hash_matches=manifest_hash_matches,
            manifest_valid=manifest_valid,
            provenance_matches=provenance_matches,
        )
    except (FileNotFoundError, OSError, TypeError, ValueError) as error:
        return TakeVerification(
            take_id=take.take_id,
            asset_hash_matches=False,
            manifest_hash_matches=False,
            manifest_valid=False,
            provenance_matches=False,
            error=str(error),
        )


def verify_scene(repository: ReviewRepository, packet: DecisionPacket) -> SceneVerification:
    return SceneVerification(tuple(verify_take(repository, take) for take in packet.takes))
