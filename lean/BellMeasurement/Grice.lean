import Mathlib

/-! # Exact arithmetic for the attaining Grice construction -/

namespace BellMeasurement

/-- The conditional probabilities `(1/2,1/2,1,1)` average to `3/4`. -/
theorem grice_average :
    (((1 / 2 : ℝ) + (1 / 2 : ℝ) + 1 + 1) / 4) = (3 / 4 : ℝ) := by
  norm_num

/-- The fixed-photon scalar ratio specializes to `3/4` at two photons. -/
theorem two_photon_ratio : ((2 + 1 : ℝ) / (2 + 2)) = (3 / 4 : ℝ) := by
  norm_num

end BellMeasurement
