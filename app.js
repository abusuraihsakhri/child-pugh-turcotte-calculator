import { calculateChildPugh, calculateLegacyMeld } from "./calculator.js";

const $ = (id) => document.getElementById(id);
const descriptions = {
  A: "Lower Child-Pugh severity class",
  B: "Intermediate Child-Pugh severity class",
  C: "Higher Child-Pugh severity class",
};

function inputValue(id, { optional = false } = {}) {
  const raw = $(id).value.trim();
  if (optional && raw === "") return null;
  return raw;
}

function renderPoints(scores) {
  const names = [
    ["Bilirubin", scores.bilirubin],
    ["Albumin", scores.albumin],
    ["INR", scores.inr],
    ["Ascites", scores.ascites],
    ["Enceph.", scores.encephalopathy],
  ];
  const items = names.map(([name, value]) => {
    const item = document.createElement("div");
    item.className = "point";
    const strong = document.createElement("b");
    strong.textContent = String(value);
    const small = document.createElement("small");
    small.textContent = name;
    item.append(strong, small);
    return item;
  });
  $("componentPoints").replaceChildren(...items);
}

function calculate() {
  const bilirubin = inputValue("bilirubin");
  const albumin = inputValue("albumin");
  const inr = inputValue("inr");
  const creatinine = inputValue("creatinine", { optional: true });
  const dialysis = $("dialysis").checked;
  if (dialysis && creatinine === null) throw new Error("Creatinine is required when dialysis is selected.");

  const result = calculateChildPugh({
    bilirubin,
    albumin,
    inr,
    ascites: $("ascites").value,
    encephalopathy: $("encephalopathy").value,
  });

  $("scoreValue").textContent = String(result.score);
  $("classValue").textContent = result.className;
  $("classText").textContent = descriptions[result.className];
  renderPoints(result.scores);

  if (creatinine !== null) {
    $("meldValue").textContent = String(calculateLegacyMeld({ bilirubin, inr, creatinine, dialysis }));
    $("meldBlock").classList.remove("hidden");
  } else {
    $("meldBlock").classList.add("hidden");
  }
}

$("scoreForm").addEventListener("submit", (event) => {
  event.preventDefault();
  $("errorMessage").textContent = "";
  try { calculate(); } catch (error) { $("errorMessage").textContent = error.message; }
});

const savedTheme = localStorage.getItem("cpt-theme");
if (savedTheme === "dark" || savedTheme === "light") document.documentElement.dataset.theme = savedTheme;
$("themeToggle").addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  localStorage.setItem("cpt-theme", next);
});

calculate();
