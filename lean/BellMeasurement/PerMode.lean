import BellMeasurement.WeightedCap

/-!
# Per-output-mode certificate

The analytic paper derives these hypotheses from the conditional Gram matrix and
a product state in the kernel of the pulled-back signal annihilator.
-/

namespace BellMeasurement

/-- The per-output-mode success budget `Σ_j d_j ≤ 4q+t`. -/
theorem per_mode_success_bound
    (q t d0 d1 d2 d3 f0 f1 f2 f3 w0 w1 w2 w3 : ℝ)
    (hf0 : 0 ≤ f0) (hf1 : 0 ≤ f1) (hf2 : 0 ≤ f2) (hf3 : 0 ≤ f3)
    (hw0 : w0 ≤ (1 / 2 : ℝ)) (hw1 : w1 ≤ (1 / 2 : ℝ))
    (hw2 : w2 ≤ (1 / 2 : ℝ)) (hw3 : w3 ≤ (1 / 2 : ℝ))
    (hweighted : t / 2 ≤ f0 * w0 + f1 * w1 + f2 * w2 + f3 * w3)
    (hdef0 : f0 = q + t / 2 - d0)
    (hdef1 : f1 = q + t / 2 - d1)
    (hdef2 : f2 = q + t / 2 - d2)
    (hdef3 : f3 = q + t / 2 - d3) :
    d0 + d1 + d2 + d3 ≤ 4 * q + t := by
  have hcap := weighted_cap_four f0 f1 f2 f3 w0 w1 w2 w3
    hf0 hf1 hf2 hf3 hw0 hw1 hw2 hw3
  have hfsum : t ≤ f0 + f1 + f2 + f3 := by
    nlinarith
  nlinarith [hdef0, hdef1, hdef2, hdef3]

end BellMeasurement
