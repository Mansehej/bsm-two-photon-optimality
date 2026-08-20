import Mathlib

/-!
# Four-term weighted cap

The physical proof supplies nonnegative residual diagonal weights `f_j` and
Bell-basis probabilities `w_j = |z_j|^2` satisfying `w_j ≤ 1/2`.
-/

namespace BellMeasurement

/-- If every sampling weight is at most one half, the weighted sum is at most
one half of the unweighted sum. -/
theorem weighted_cap_four
    (f0 f1 f2 f3 w0 w1 w2 w3 : ℝ)
    (hf0 : 0 ≤ f0) (hf1 : 0 ≤ f1) (hf2 : 0 ≤ f2) (hf3 : 0 ≤ f3)
    (hw0 : w0 ≤ (1 / 2 : ℝ)) (hw1 : w1 ≤ (1 / 2 : ℝ))
    (hw2 : w2 ≤ (1 / 2 : ℝ)) (hw3 : w3 ≤ (1 / 2 : ℝ)) :
    f0 * w0 + f1 * w1 + f2 * w2 + f3 * w3
      ≤ (f0 + f1 + f2 + f3) / 2 := by
  have h0 : 0 ≤ f0 * ((1 / 2 : ℝ) - w0) :=
    mul_nonneg hf0 (sub_nonneg.mpr hw0)
  have h1 : 0 ≤ f1 * ((1 / 2 : ℝ) - w1) :=
    mul_nonneg hf1 (sub_nonneg.mpr hw1)
  have h2 : 0 ≤ f2 * ((1 / 2 : ℝ) - w2) :=
    mul_nonneg hf2 (sub_nonneg.mpr hw2)
  have h3 : 0 ≤ f3 * ((1 / 2 : ℝ) - w3) :=
    mul_nonneg hf3 (sub_nonneg.mpr hw3)
  nlinarith

end BellMeasurement
