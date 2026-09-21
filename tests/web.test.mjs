import test from "node:test";
import assert from "node:assert/strict";
import { calculateChildPugh, calculateLegacyMeld } from "../calculator.js";

test("Child-Pugh boundary classes", () => {
  assert.deepEqual(calculateChildPugh({ bilirubin: 1, albumin: 4, inr: 1.2, ascites: "none", encephalopathy: "none" }).score, 5);
  const high = calculateChildPugh({ bilirubin: 5, albumin: 2, inr: 3, ascites: "moderate-severe", encephalopathy: "grade III-IV" });
  assert.equal(high.score, 15);
  assert.equal(high.className, "C");
});

test("legacy MELD caps creatinine at 4", () => {
  assert.equal(calculateLegacyMeld({ bilirubin: 4, inr: 2.5, creatinine: 20 }), calculateLegacyMeld({ bilirubin: 4, inr: 2.5, creatinine: 4 }));
});

test("invalid categories are rejected", () => {
  assert.throws(() => calculateChildPugh({ bilirubin: 1, albumin: 4, inr: 1.2, ascites: "other", encephalopathy: "none" }));
});
