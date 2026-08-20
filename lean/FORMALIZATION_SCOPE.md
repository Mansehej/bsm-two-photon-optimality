# Lean formalization scope

## Kernel-targeted certificate layer

The Lean source contains no `sorry`, `admit`, declaration-level `axiom`, or
unsafe theorem declaration. It encodes:

1. injectivity of `n ↦ n - e_ell` on occupations with `n_ell > 0`;
2. the four-term weighted cap from `f_j >= 0` and `w_j <= 1/2`;
3. the per-mode implication `sum_j d_j <= 4 q + t`;
4. the global two-photon arithmetic yielding average success `<= 3/4`;
5. the exact Grice average `(1/2+1/2+1+1)/4 = 3/4`;
6. the final scalar division step for the fixed-`k` corollary.

## Analytic bridge not yet in Lean

This is not presented as an end-to-end formalization of bosonic optics. The
paper, supported by independent exact Python verification, still supplies:

- finite bosonic Fock space and creation/annihilation operators;
- passive second quantization;
- the conditional Gram decomposition;
- exclusive Fock-coordinate deletion and the residual PSD inequality;
- Bell one-particle density matrices and the product-overlap cap;
- exact permanent/polynomial evaluation of the attaining circuit.

A full kernel development would need to encode those model-to-certificate
lemmas and then invoke the certificate theorems already present here.
