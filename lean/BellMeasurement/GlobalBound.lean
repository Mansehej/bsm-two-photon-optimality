import BellMeasurement.PerMode

/-!
# Global arithmetic certificates
-/

namespace BellMeasurement

/-- Four-photon counting and the summed local budget imply average success at
most `3/4`. -/
theorem two_photon_global_average_bound
    (p0 p1 p2 p3 dSum qSum tSum : ℝ)
    (hcount : dSum = 4 * (p0 + p1 + p2 + p3))
    (hbudget : dSum ≤ 4 * qSum + tSum)
    (hq : qSum = 2) (ht : tSum = 4) :
    (p0 + p1 + p2 + p3) / 4 ≤ (3 / 4 : ℝ) := by
  have hbudget' : dSum ≤ 12 := by
    rw [hq, ht] at hbudget
    norm_num at hbudget ⊢
    exact hbudget
  have hpsum : p0 + p1 + p2 + p3 ≤ 3 := by
    nlinarith [hcount, hbudget']
  nlinarith

/-- The final scalar division step for the fixed-`k` optical budget. -/
theorem fixed_k_average_bound
    (k P : ℝ) (hk : 0 ≤ k)
    (hbudget : (k + 2) * (4 * P) ≤ 4 * (k + 1)) :
    P ≤ (k + 1) / (k + 2) := by
  have hk2 : 0 < k + 2 := by linarith
  apply (le_div_iff₀ hk2).2
  nlinarith

end BellMeasurement
