const state = {
  scene: null,
  keeperTakeId: null,
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
    input.addEventListener("change", () => {
      state.keeperTakeId = take.take_id;
      renderTakes(state.scene.takes);
      renderPacket(state.scene);
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

function render(scene) {
  state.scene = scene;
  state.keeperTakeId = scene.keeper_take_id;
  byId("brief").textContent = scene.brief;
  byId("integrity-value").textContent = titleCase(scene.integrity);
  byId("storage-mode").textContent = `${titleCase(scene.storage_mode)} / ${scene.scene_id}`;
  byId("selection-reason").value = scene.selection_reason;
  renderLockedVariables(scene.locked_variables);
  renderTakes(scene.takes);
  renderPacket(scene);
}

async function loadScene() {
  const response = await fetch("/api/scene", { cache: "no-store" });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "Could not load the scene");
  render(payload);
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
    status.textContent = `Decision sealed. Packet ${shortHash(payload.packet_hash)} verified.`;
  } catch (error) {
    status.textContent = error.message;
  }
});

loadScene().catch((error) => {
  byId("form-status").textContent = error.message;
  byId("storage-mode").textContent = "Scene unavailable";
});
