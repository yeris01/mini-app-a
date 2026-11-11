const categoryList = document.querySelector("#category-list");
const categoryTitle = document.querySelector("#category-title");
const sourceValue = document.querySelector("#source-value");
const sourceUnit = document.querySelector("#source-unit");
const targetUnit = document.querySelector("#target-unit");
const resultValue = document.querySelector("#result-value");
const sourceUnitName = document.querySelector("#source-unit-name");
const targetUnitName = document.querySelector("#target-unit-name");
const summary = document.querySelector("#conversion-summary");
const status = document.querySelector("#conversion-status");
const swapButton = document.querySelector("#swap-button");
const copyButton = document.querySelector("#copy-button");

let groups = {};
let activeCategory = "longitud";
let latestResult = "";
let requestNumber = 0;

const formatNumber = (number) => new Intl.NumberFormat("es-ES", {
  maximumSignificantDigits: 10,
}).format(number);

function updateUnitNames() {
  const units = groups[activeCategory].units;
  sourceUnitName.textContent = units.find((unit) => unit.code === sourceUnit.value)?.label ?? "";
  targetUnitName.textContent = units.find((unit) => unit.code === targetUnit.value)?.label ?? "";
}

function renderCategories() {
  categoryList.replaceChildren();
  Object.entries(groups).forEach(([key, group], index) => {
    const button = document.createElement("button");
    button.className = "category-button";
    button.type = "button";
    button.setAttribute("aria-current", String(key === activeCategory));
    button.innerHTML = `<span class="category-icon" aria-hidden="true">${group.symbol}</span><span>${group.label}</span><span class="category-count">${String(index + 1).padStart(2, "0")}</span>`;
    button.addEventListener("click", () => selectCategory(key));
    categoryList.append(button);
  });
}

function renderUnits() {
  const units = groups[activeCategory].units;
  const previousSource = sourceUnit.value;
  const previousTarget = targetUnit.value;
  for (const select of [sourceUnit, targetUnit]) {
    select.replaceChildren();
    units.forEach(({ code }) => {
      const option = document.createElement("option");
      option.value = code;
      option.textContent = code;
      select.append(option);
    });
  }
  sourceUnit.value = units.some((unit) => unit.code === previousSource) ? previousSource : units[0].code;
  targetUnit.value = units.some((unit) => unit.code === previousTarget) ? previousTarget : units[1]?.code ?? units[0].code;
  categoryTitle.textContent = groups[activeCategory].label;
  updateUnitNames();
  convert();
}

function selectCategory(category) {
  activeCategory = category;
  renderCategories();
  renderUnits();
}

async function convert() {
  const currentRequest = ++requestNumber;
  status.textContent = "";
  if (sourceValue.value.trim() === "" || !Number.isFinite(Number(sourceValue.value))) {
    resultValue.textContent = "—";
    summary.textContent = "Escribe un valor para convertir";
    latestResult = "";
    return;
  }

  try {
    const response = await fetch("/api/convert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category: activeCategory,
        value: Number(sourceValue.value),
        from_unit: sourceUnit.value,
        to_unit: targetUnit.value,
      }),
    });
    const payload = await response.json();
    if (currentRequest !== requestNumber) return;
    if (!response.ok) throw new Error(payload.detail ?? "No se pudo realizar la conversión.");
    resultValue.textContent = formatNumber(payload.result);
    latestResult = String(payload.result);
    summary.textContent = `${formatNumber(payload.value)} ${payload.from_unit} = ${formatNumber(payload.result)} ${payload.to_unit}`;
  } catch (error) {
    if (currentRequest !== requestNumber) return;
    resultValue.textContent = "—";
    summary.textContent = "";
    latestResult = "";
    status.textContent = error.message || "No se pudo conectar con el servidor.";
  }
}

sourceValue.addEventListener("input", convert);
sourceUnit.addEventListener("change", () => { updateUnitNames(); convert(); });
targetUnit.addEventListener("change", () => { updateUnitNames(); convert(); });
swapButton.addEventListener("click", () => {
  [sourceUnit.value, targetUnit.value] = [targetUnit.value, sourceUnit.value];
  updateUnitNames();
  convert();
});
copyButton.addEventListener("click", async () => {
  if (!latestResult) return;
  try {
    await navigator.clipboard.writeText(latestResult);
    status.textContent = "Copiado";
    window.setTimeout(() => { status.textContent = ""; }, 1600);
  } catch {
    status.textContent = "No se pudo copiar el resultado.";
  }
});

async function initialize() {
  try {
    const response = await fetch("/api/units");
    if (!response.ok) throw new Error("No se pudieron cargar las unidades.");
    groups = await response.json();
    renderCategories();
    renderUnits();
  } catch (error) {
    status.textContent = error.message || "No se pudo conectar con el servidor.";
  }
}

initialize();
