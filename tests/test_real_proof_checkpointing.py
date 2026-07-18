from types import SimpleNamespace

import pytest
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
    sinks = []

    def fake_sink():
        sink = object()
        sinks.append(sink)
        return sink

    monkeypatch.setattr(real_proof, "Pipeline", FakePipeline)
    monkeypatch.setattr(real_proof, "_generation_storage_sink", fake_sink)
    monkeypatch.setattr(real_proof, "_provider", lambda: object())
    monkeypatch.setattr(
        real_proof,
        "_provider_settings",
        lambda: ("test-model", {"size": "1024x1280"}),
    )

    state = real_proof._generate_pending(real_proof._initial_state(), store)

    assert state.complete is True
    assert len(sinks) == 3
    assert len({id(sink) for sink in sinks}) == 3
    assert len(store.saved) == 3
    assert [
        sum(slot["status"] == "succeeded" for slot in checkpoint["slots"])
        for checkpoint in store.saved
    ] == [1, 2, 3]

    resumed = generation_state_from_dict(store.saved[0])
    retry_store = FakeStateStore()
    FakePipeline.results = [_result(2), _result(3)]

    retried = real_proof._generate_pending(resumed, retry_store)

    assert retried.complete is True
    assert len(retry_store.saved) == 2
    assert retried.slots[0].attempts == 1


def test_infrastructure_failure_is_checkpointed_before_later_spend(monkeypatch):
    class FailingSecondPipeline(FakePipeline):
        calls = 0

        def run(self, **kwargs):
            self.__class__.calls += 1
            if self.__class__.calls == 2:
                raise RuntimeError("B2 manifest upload failed")
            return _result(1)

    FailingSecondPipeline.calls = 0
    store = FakeStateStore()
    monkeypatch.setattr(real_proof, "Pipeline", FailingSecondPipeline)
    monkeypatch.setattr(real_proof, "_generation_storage_sink", lambda: object())
    monkeypatch.setattr(real_proof, "_provider", lambda: object())
    monkeypatch.setattr(
        real_proof,
        "_provider_settings",
        lambda: ("test-model", {"size": "1024x1280"}),
    )

    with pytest.raises(RuntimeError, match="later takes were not started"):
        real_proof._generate_pending(real_proof._initial_state(), store)

    checkpoint = store.saved[-1]
    assert FailingSecondPipeline.calls == 2
    assert checkpoint["slots"][0]["status"] == "succeeded"
    assert checkpoint["slots"][1]["status"] == "failed"
    assert checkpoint["slots"][1]["error_code"] == "pipeline_infrastructure_failure"
    assert checkpoint["slots"][2]["status"] == "pending"
