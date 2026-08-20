# Paper-to-Lean proof map

| Paper ingredient | Lean declaration | Notes |
|---|---|---|
| Injectivity in the exclusive-component deletion lemma | `removeOne_injective_on_occupied` | Formalizes the occupation combinatorics. |
| `w_j <= 1/2`, `f_j >= 0` weighted cap | `weighted_cap_four` | The Bell/product geometry supplies the hypotheses analytically. |
| Equations leading from the weighted lower bound to `sum d <= 4q+t` | `per_mode_success_bound` | Exact real-arithmetic certificate. |
| Four-photon count, summed local budget, `sum q=2`, `sum t=4` | `two_photon_global_average_bound` | Produces the exact `3/4` upper bound. |
| Fixed-`k` final division | `fixed_k_average_bound` | Assumes the generalized optical budget already derived. |
| Grice conditional probabilities | `grice_average` | Exact attainment arithmetic. |

The model-to-certificate statements that are not yet Lean theorems are listed in
`FORMALIZATION_SCOPE.md`.
