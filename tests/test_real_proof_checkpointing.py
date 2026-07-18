from types import SimpleNamespace

from genblaze_core import StepStatus

from shot_ledger import real_proof
from shot_ledger.generation_state import generation_state_from_dict


class FakePipeline:
    results = []

    def __init__(self, name):
        assert name == "shot-ledger-controlled-lighting"

    def step(self, provider, **kwargs):
        self.provider = provider
        self.kwargs = kwargs
        return self

    def run(self, **kwargs):
        assert kwargs["raise_on_failure"] is False
        return self.results.pop(0)


class FakeStateStore:
    def __init__(self):
        self.saved = []

    def save(self, state):
        self.saved.append(state.to_dict())


def _result(take_number):
    asset = SimpleNamespace(
        url=f"https://example.invalid/take-{take_number}.png",
        sha256=f"{take_number}" * 64,
    )
    step = SimpleNamespace(
        status=StepStatus.SUCCEEDED,
        assets=[asset],
        error=None,
        error_code=None,
        provider="test-provider",
        model="test-model",
    )
    manifest = SimpleNamespace(
        manifest_uri=f"https://example.invalid/take-{take_number}.manifest.json",
        canonical_hash=f"{take_number + 3}" * 64,
    )
    return SimpleNamespace(run=SimpleNamespace(steps=[step]), manifest=manifest)


def test_real_generation_checkpoints_each_paid_take(monkeypatch):
    FakePipeline.results = [_result(1), _result(2), _result(3)]
    store = FakeStateStore()
    monkeypatch.setattr(real_proof, "Pipeline", FakePipeline)
    monkeypatch.setattr(real_proof, "ObjectStorageSink", lambda *args, **kwargs: object())
    monkeypatch.setattr(real_proof, "_provider", lambda: object())
    monkeypatch.setattr(
        real_proof,
        "_provider_settings",
        lambda: ("test-model", {"size": "1024x1280"}),
    )

    state = real_proof._generate_pending(real_proof._initial_state(), object(), store)

    assert state.complete is True
    assert len(store.saved) == 3
    assert [
        sum(slot["status"] == "succeeded" for slot in checkpoint["slots"])
        for checkpoint in store.saved
    ] == [1, 2, 3]

    resumed = generation_state_from_dict(store.saved[0])
    retry_store = FakeStateStore()
    FakePipeline.results = [_result(2), _result(3)]

    retried = real_proof._generate_pending(resumed, object(), retry_store)

    assert retried.complete is True
    assert len(retry_store.saved) == 2
    assert retried.slots[0].attempts == 1
