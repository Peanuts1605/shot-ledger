from __future__ import annotations

import json
import os
from typing import Any

from .real_proof import _provider, _provider_name, _provider_settings, _required_env


def verify_provider() -> dict[str, str]:
    provider_name = _provider_name()
    model, _ = _provider_settings()
    if provider_name == "openai":
        from openai import OpenAI

        returned = OpenAI().models.retrieve(model)
        returned_id = getattr(returned, "id", None)
        if returned_id != model:
            raise RuntimeError(f"OpenAI returned unexpected model id: {returned_id!r}")
    else:
        _provider().preflight_auth()
    return {"provider": provider_name, "model": model, "status": "verified"}


def verify_b2() -> dict[str, str]:
    from genblaze_s3 import S3StorageBackend

    backend: Any = S3StorageBackend.for_backblaze(preflight=True)
    try:
        return {
            "bucket": os.environ["B2_BUCKET"],
            "region": os.environ.get("B2_REGION", "us-west-004"),
            "status": "verified",
        }
    finally:
        backend.close()


def run() -> dict[str, object]:
    _required_env()
    receipt: dict[str, object] = {
        "provider": verify_provider(),
        "storage": verify_b2(),
        "paid_generation_started": False,
        "planned_takes": 3,
        "status": "ready_for_spend_approval",
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return receipt


if __name__ == "__main__":
    run()
