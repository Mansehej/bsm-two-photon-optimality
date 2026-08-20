import Mathlib

/-!
# Occupation-vector lemmas

This file formalizes the injectivity fact used when one photon is removed from a
fixed output mode.
-/

namespace BellMeasurement

/-- An `m`-mode photon-number occupation vector. -/
abbrev Occupation (m : ℕ) := Fin m → ℕ

/-- Remove one photon from mode `ell`; the definition is total on occupations. -/
def removeOne {m : ℕ} (ell : Fin m) (n : Occupation m) : Occupation m :=
  fun i => if i = ell then n i - 1 else n i

/-- The map `n ↦ n - e_ell` is injective when both counts at `ell` are positive. -/
theorem removeOne_injective_on_occupied
    {m : ℕ} {ell : Fin m} {n n' : Occupation m}
    (hn : 0 < n ell) (hn' : 0 < n' ell)
    (h : removeOne ell n = removeOne ell n') : n = n' := by
  funext i
  by_cases hi : i = ell
  · subst i
    have hcoord := congrFun h ell
    simp [removeOne] at hcoord
    omega
  · have hcoord := congrFun h i
    simpa [removeOne, hi] using hcoord

end BellMeasurement
