export function scoreBilirubin(value) { return value < 2 ? 1 : value <= 3 ? 2 : 3; }
export function scoreAlbumin(value) { return value > 3.5 ? 1 : value >= 2.8 ? 2 : 3; }
export function scoreInr(value) { return value < 1.7 ? 1 : value <= 2.3 ? 2 : 3; }
export function scoreAscites(value) {
  if (value === "none") return 1;
  if (value === "mild/controlled") return 2;
  if (value === "moderate-severe") return 3;
  throw new Error("Invalid ascites category.");
}
export function scoreEncephalopathy(value) {
  if (value === "none") return 1;
  if (value === "grade I-II") return 2;
  if (value === "grade III-IV") return 3;
  throw new Error("Invalid encephalopathy category.");
}

function positiveFinite(name, value, allowZero = false) {
  const number = Number(value);
  if (!Number.isFinite(number) || number < 0 || (!allowZero && number === 0)) {
    throw new Error(name + " has an invalid value.");
  }
  return number;
}

export function calculateLegacyMeld({ bilirubin, inr, creatinine, dialysis = false }) {
  bilirubin = positiveFinite("Bilirubin", bilirubin);
  inr = positiveFinite("INR", inr);
  creatinine = positiveFinite("Creatinine", creatinine);
  const bili = Math.max(bilirubin, 1);
  const inrUsed = Math.max(inr, 1);
  const creat = dialysis ? 4 : Math.min(Math.max(creatinine, 1), 4);
  const raw = 3.78 * Math.log(bili) + 11.2 * Math.log(inrUsed) + 9.57 * Math.log(creat) + 6.43;
  return Math.max(6, Math.min(Math.round(raw), 40));
}

export function calculateChildPugh({ bilirubin, albumin, inr, ascites, encephalopathy }) {
  bilirubin = positiveFinite("Bilirubin", bilirubin, true);
  albumin = positiveFinite("Albumin", albumin);
  inr = positiveFinite("INR", inr);
  const scores = {
    bilirubin: scoreBilirubin(bilirubin),
    albumin: scoreAlbumin(albumin),
    inr: scoreInr(inr),
    ascites: scoreAscites(ascites),
    encephalopathy: scoreEncephalopathy(encephalopathy),
  };
  const total = Object.values(scores).reduce((sum, value) => sum + value, 0);
  return {
    score: total,
    className: total <= 6 ? "A" : total <= 9 ? "B" : "C",
    scores,
  };
}
