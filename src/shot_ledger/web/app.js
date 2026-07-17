const state = {
  scene: null,
  keeperTakeId: null,
  sealedKeeperTakeId: null,
  sealedReason: null,
};

const byId = (id) => document.getElementById(id);

function shortHash(value) {
  return `${value.slice(0, 10)}...${value.slice(-8)}`;
}

function titleCase(value) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function renderLockedVariables(variables) {
  const root = byId("locked-variables");
  root.replaceChildren();
  for (const [key, value] of Object.entries(variables)) {
    const wrapper = document.createElement("div");
    const term = document.createElement("dt");
    const detail = document.createElement("dd");
    term.textContent = titleCase(key);
    detail.textContent = value;
    wrapper.append(term, detail);
    root.append(wrapper);
  }
}

function renderTakes(takes) {
  const root = byId("take-grid");
  const template = byId("take-template");
  root.replaceChildren();
  takes.forEach((take, index) => {
    const fragment = template.content.cloneNode(true);
    const input = fragment.querySelector("input");
    const image = fragment.querySelector("img");
    input.value = take.take_id;
    input.checked = take.take_id === state.keeperTakeId;
    input.disabled = state.scene.write_enabled === false;
    input.addEventListener("change", () => {
      state.keeperTakeId = take.take_id;
      renderTakes(state.scene.takes);
      renderPacket(state.scene);
      renderSelectedReceipt();
      byId("form-status").textContent = `${titleCase(take.take_id)} selected. Add the reason it wins.`;
    });
    image.src = take.preview_url;
    image.alt = `${take.changed_value} take of the locked travel mug scene`;
    fragment.querySelector(".take-number").textContent = `0${index + 1}`;
    fragment.querySelector(".take-state").textContent = input.checked ? "Keeper" : "Candidate";
    fragment.querySelector(".take-name").textContent = titleCase(take.take_id);
    fragment.querySelector(".take-change").textContent = take.changed_value;
    fragment.querySelector(".take-meta").textContent = `${take.provider} / ${take.model}\n${shortHash(take.manifest_hash)}`;
    root.append(fragment);
  });
}

function renderPacket(scene) {
  const rejected = scene.takes
    .filter((take) => take.take_id !== state.keeperTakeId)
    .map((take) => take.take_id)
    .join(", ");
  byId("packet-keeper").textContent = state.keeperTakeId || "Not selected";
  byId("packet-rejected").textContent = rejected || "-";
  byId("packet-hash").textContent = scene.packet_hash;
}

function renderSelectedReceipt() {
  const take = state.scene.takes.find((candidate) => candidate.take_id === state.keeperTakeId);
  if (!take) return;
  const reason = byId("selection-reason").value.trim();
  const sealed = state.keeperTakeId === state.sealedKeeperTakeId && reason === state.sealedReason;
  byId("receipt-state").textContent = sealed ? "Sealed" : "Draft change";
  byId("receipt-take").textContent = `${titleCase(take.take_id)} / ${take.changed_value}`;
  byId("receipt-provider").textContent = `${take.provider} / ${take.model}`;
  byId("receipt-storage").textContent = titleCase(state.scene.storage_mode);
  byId("receipt-prompt").textContent = take.prompt;
  byId("receipt-parameters").textContent = Object.entries(take.parameters)
    .map(([key, value]) => `${key}=${value}`)
    .join(" / ");
  byId("receipt-reason").textContent = reason || "Reason not recorded";
}

function render(scene) {
  state.scene = scene;
  state.keeperTakeId = scene.keeper_take_id;
  state.sealedKeeperTakeId = scene.keeper_take_id;
  state.sealedReason = scene.selection_reason;
  byId("brief").textContent = scene.brief;
  byId("integrity-value").textContent = titleCase(scene.integrity);
  byId("media-integrity-value").textContent = titleCase(scene.media_integrity.status);
  byId("storage-mode").textContent = titleCase(scene.storage_mode);
  byId("storage-mode").title = scene.scene_id;
  byId("selection-reason").value = scene.selection_reason;
  byId("proof-scope").textContent = scene.proof_scope;
  byId("selection-reason").disabled = !scene.write_enabled;
  byId("seal-decision").disabled = !scene.write_enabled;
  byId("form-status").textContent = scene.write_enabled
    ? "Select a take and leave a concrete reason."
    : "Public B2 proof is read-only. The sealed decision remains unchanged.";
  renderLockedVariables(scene.locked_variables);
  renderTakes(scene.takes);
  renderPacket(scene);
  renderSelectedReceipt();
}

function renderRecovery(runState) {
  document.body.classList.add("recovery-mode");
  byId("brief").textContent = runState.brief;
  byId("integrity-value").textContent = "State Saved";
  byId("media-integrity-value").textContent = "Partial";
  byId("storage-mode").textContent = titleCase(runState.storage_mode);
  byId("storage-mode").title = runState.scene_id;
  byId("recovery-summary").textContent = `${runState.succeeded_count} of 3 takes have durable media and provenance. Completed siblings will not run again.`;
  byId("recovery-command").textContent = runState.retry_command;
  const slots = byId("recovery-slots");
  slots.replaceChildren();
  for (const slot of runState.slots) {
    const item = document.createElement("li");
    const heading = document.createElement("strong");
    const status = document.createElement("span");
    const reason = document.createElement("p");
    heading.textContent = `${titleCase(slot.take_id)} / ${slot.changed_value}`;
    status.textContent = `${titleCase(slot.status)} / ${slot.attempts} attempt${slot.attempts === 1 ? "" : "s"}`;
    reason.textContent = slot.failure_reason || (slot.status === "succeeded" ? "Durable asset and manifest preserved." : "Waiting to run.");
    item.dataset.status = slot.status;
    item.append(heading, status, reason);
    slots.append(item);
  }
  byId("recovery-panel").hidden = false;
}

async function loadScene() {
  const [sceneResponse, runResponse] = await Promise.all([
    fetch("/api/scene", { cache: "no-store" }),
    fetch("/api/run-state", { cache: "no-store" }),
  ]);
  const runState = await runResponse.json();
  if (runResponse.ok && !runState.complete) {
    renderRecovery(runState);
    return;
  }
  const scene = await sceneResponse.json();
  if (!sceneResponse.ok) throw new Error(scene.error || "Could not load the scene");
  render(scene);
}

byId("decision-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const status = byId("form-status");
  const reason = byId("selection-reason").value.trim();
  if (!state.keeperTakeId || !reason) {
    status.textContent = "Choose a keeper and write the visible reason it wins.";
    return;
  }
  status.textContent = "Sealing decision...";
  try {
    const response = await fetch("/api/decision", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        keeper_take_id: state.keeperTakeId,
        selection_reason: reason,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Decision was not saved");
    render(payload);
    status.textContent = `Decision sealed. Hash ${shortHash(payload.packet_hash)} recorded.`;
  } catch (error) {
    status.textContent = error.message;
  }
});

byId("selection-reason").addEventListener("input", () => {
  if (state.scene) renderSelectedReceipt();
});

loadScene().catch((error) => {
  byId("form-status").textContent = error.message;
  byId("storage-mode").textContent = "Scene unavailable";
});
