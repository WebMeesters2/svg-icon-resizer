/* Pair source and square SVG files and present their exact page boundaries. */
"use strict";

const state = {
  entries: [],
  filtered: [],
  selectedKey: null,
  objectUrls: [],
  renderToken: 0,
};

const elements = {
  body: document.body,
  folderInput: document.querySelector("#folder-input"),
  search: document.querySelector("#search"),
  iconCount: document.querySelector("#icon-count"),
  iconList: document.querySelector("#icon-list"),
  emptyState: document.querySelector("#empty-state"),
  viewer: document.querySelector("#viewer"),
  currentName: document.querySelector("#current-name"),
  position: document.querySelector("#position"),
  previous: document.querySelector("#previous"),
  next: document.querySelector("#next"),
  zoom: document.querySelector("#zoom"),
  source: previewElements("source"),
  square: previewElements("square"),
};

function previewElements(prefix) {
  return {
    page: document.querySelector(`#${prefix}-page`),
    image: document.querySelector(`#${prefix}-image`),
    metadata: document.querySelector(`#${prefix}-metadata`),
    status: document.querySelector(`#${prefix}-status`),
  };
}

function relativeParts(file) {
  return (file.webkitRelativePath || file.name).replaceAll("\\", "/").split("/");
}

function collectEntries(files) {
  const entries = new Map();
  for (const file of files) {
    if (!file.name.toLowerCase().endsWith(".svg")) continue;
    const parts = relativeParts(file);
    const isSquare = parts.length > 1 && parts.at(-2).toLowerCase() === "square";
    const key = file.name.toLocaleLowerCase();
    const entry = entries.get(key) || { key, name: file.name, source: null, square: null };
    entry[isSquare ? "square" : "source"] = file;
    if (!isSquare) entry.name = file.name;
    entries.set(key, entry);
  }
  return [...entries.values()].sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));
}

function applyFilter() {
  const query = elements.search.value.trim().toLocaleLowerCase();
  state.filtered = state.entries.filter((entry) => entry.name.toLocaleLowerCase().includes(query));
  if (!state.filtered.some((entry) => entry.key === state.selectedKey)) {
    state.selectedKey = state.filtered[0]?.key ?? null;
  }
  renderList();
  void renderSelection();
}

function renderList() {
  elements.iconList.replaceChildren();
  elements.iconCount.textContent = String(state.filtered.length);
  for (const entry of state.filtered) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.key = entry.key;
    button.classList.toggle("active", entry.key === state.selectedKey);
    button.setAttribute("aria-current", entry.key === state.selectedKey ? "true" : "false");

    const dot = document.createElement("span");
    dot.className = `pair-dot${entry.source && entry.square ? " complete" : ""}`;
    dot.title = entry.source && entry.square ? "Source and square output available" : "Incomplete pair";
    const name = document.createElement("span");
    name.className = "file-name";
    name.textContent = entry.name;
    button.append(dot, name);
    button.addEventListener("click", () => selectEntry(entry.key));
    elements.iconList.append(button);
  }
}

function selectEntry(key) {
  state.selectedKey = key;
  renderList();
  void renderSelection();
}

async function svgMetadata(file) {
  const text = await file.text();
  const documentNode = new DOMParser().parseFromString(text, "image/svg+xml");
  const parserError = documentNode.querySelector("parsererror");
  if (parserError || documentNode.documentElement.localName !== "svg") {
    return { error: "Invalid SVG document", aspect: 1 };
  }
  const root = documentNode.documentElement;
  const rawViewBox = root.getAttribute("viewBox");
  const values = rawViewBox?.trim().split(/[\s,]+/).map(Number) ?? [];
  const hasViewBox = values.length === 4 && values.every(Number.isFinite) && values[2] > 0 && values[3] > 0;
  return {
    viewBox: rawViewBox || "not set",
    width: root.getAttribute("width") || "not set",
    height: root.getAttribute("height") || "not set",
    aspect: hasViewBox ? values[2] / values[3] : 1,
    square: hasViewBox ? Math.abs(values[2] - values[3]) < 1e-9 : false,
  };
}

function clearObjectUrls() {
  for (const url of state.objectUrls) URL.revokeObjectURL(url);
  state.objectUrls = [];
}

async function renderPreview(file, preview, expectedSquare, token) {
  preview.page.classList.toggle("missing", !file);
  preview.image.removeAttribute("src");
  preview.metadata.replaceChildren();
  preview.status.className = "status";

  if (!file) {
    preview.status.textContent = "Missing";
    preview.status.classList.add("missing");
    addMetadata(preview.metadata, [["File", "No matching SVG"]]);
    preview.page.style.aspectRatio = "1";
    return;
  }

  const metadata = await svgMetadata(file);
  if (token !== state.renderToken) return;
  const url = URL.createObjectURL(file);
  state.objectUrls.push(url);
  preview.image.src = url;
  preview.page.style.aspectRatio = String(metadata.aspect);

  if (metadata.error) {
    preview.status.textContent = "Invalid";
    preview.status.classList.add("missing");
    addMetadata(preview.metadata, [["File", file.name], ["Error", metadata.error]]);
    return;
  }

  const squareState = expectedSquare ? (metadata.square ? "Square" : "Not square") : "Loaded";
  preview.status.textContent = squareState;
  if (expectedSquare && !metadata.square) preview.status.classList.add("missing");
  addMetadata(preview.metadata, [
    ["viewBox", metadata.viewBox],
    ["width", metadata.width],
    ["height", metadata.height],
    ["size", formatBytes(file.size)],
  ]);
}

function addMetadata(container, rows) {
  for (const [term, description] of rows) {
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = term;
    dd.textContent = description;
    container.append(dt, dd);
  }
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KiB`;
}

async function renderSelection() {
  const entry = state.filtered.find((candidate) => candidate.key === state.selectedKey);
  elements.emptyState.hidden = Boolean(entry);
  elements.viewer.hidden = !entry;
  if (!entry) return;

  clearObjectUrls();
  const token = ++state.renderToken;
  const index = state.filtered.indexOf(entry);
  elements.currentName.textContent = entry.name;
  elements.position.textContent = `${index + 1} / ${state.filtered.length}`;
  elements.previous.disabled = index <= 0;
  elements.next.disabled = index >= state.filtered.length - 1;
  await Promise.all([
    renderPreview(entry.source, elements.source, false, token),
    renderPreview(entry.square, elements.square, true, token),
  ]);
}

function moveSelection(offset) {
  const current = state.filtered.findIndex((entry) => entry.key === state.selectedKey);
  const target = state.filtered[current + offset];
  if (target) selectEntry(target.key);
}

elements.folderInput.addEventListener("click", () => {
  // Clearing permits choosing the same folder again after reconversion.
  elements.folderInput.value = "";
});

elements.folderInput.addEventListener("change", () => {
  clearObjectUrls();
  state.entries = collectEntries(elements.folderInput.files);
  state.selectedKey = state.entries[0]?.key ?? null;
  elements.search.disabled = state.entries.length === 0;
  elements.search.value = "";
  applyFilter();
});

elements.search.addEventListener("input", applyFilter);
elements.previous.addEventListener("click", () => moveSelection(-1));
elements.next.addEventListener("click", () => moveSelection(1));
elements.zoom.addEventListener("input", () => {
  document.documentElement.style.setProperty("--preview-size", `${elements.zoom.value}px`);
});

for (const button of document.querySelectorAll(".theme-button")) {
  button.addEventListener("click", () => {
    elements.body.dataset.theme = button.dataset.theme;
    for (const peer of document.querySelectorAll(".theme-button")) {
      peer.classList.toggle("active", peer === button);
    }
  });
}

document.addEventListener("keydown", (event) => {
  if (event.target instanceof HTMLInputElement) return;
  if (event.key === "ArrowLeft") moveSelection(-1);
  if (event.key === "ArrowRight") moveSelection(1);
});

window.addEventListener("beforeunload", clearObjectUrls);
