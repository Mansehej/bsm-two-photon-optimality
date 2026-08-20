# Exact two-ancillary-photon Bell-measurement package

## Result

The analytic certificate in `global_bound_proof.md` proves, for the frozen resource model in the task statement,

`P*_2 = 3/4`.

The upper bound is dimension-free over arbitrary finite ancillary/vacuum mode counts and unrestricted static passive interferometers. `grice_75.json` is an exact attaining witness.

## Files

- `global_bound_proof.md` — complete analytic upper-bound proof.
- `global_bound_certificate.py` / `.log` — exact algebraic sanity checks for the proof ingredients and Grice saturation.
- `status_audit.md` — 17 August 2026 primary-literature resource audit and post-discovery search summary.
- `exact_bsm_verifier.py` — two independent exact amplitude engines: bosonic permanents and creation-polynomial expansion.
- `grice_75.json` — exact 8-mode Grice ancilla, unitary, complete success partition, complete inconclusive partition, and exact per-input success probabilities.
- `grice_decomposition.json` — exact balanced-beamsplitter decomposition of the Grice unitary.
- `standard_50.json` — exact standard vacuum-ancilla benchmark.
- `ewert_two_product_5over8.json` — exact benchmark with two externally unentangled ancillary single photons.
- `ewert_four_product_75.json` — exact benchmark with four externally unentangled ancillary single photons.
- `*.log` and `corruption_tests.log` — replay output / deliberate-corruption results.
- `approach_registry.md` — route registry and adversarial audit.

All occupation vectors in JSON are 0-based arrays of photon counts. Narrative mode names are 1-based.

## Exact Grice witness

Mode order:

`[H1,V1,H2,V2,H3,V3,H4,V4]`.

Signal modes are the first four. Ancilla:

`(a5^dagger a7^dagger + a6^dagger a8^dagger)|0>/sqrt(2)`.

On spatial paths `1,2,3,4`, use

`S = (1/2)*[[1,i,i,-1],[i,1,-1,i],[i,-1,1,i],[-1,i,i,1]]`,

identically on both rails. The file `grice_75.json` stores the resulting full 8x8 matrix. The exact decomposition is `S=B tensor B` with

`B=(1/sqrt(2))*[[1,i],[i,1]]`.

Exact conditional success probabilities in task Bell ordering:

`Phi+ = 1/2, Phi- = 1/2, Psi+ = 1, Psi- = 1`, average `3/4`.

## Replay

Requires Python 3 and SymPy 1.14 or compatible.

```bash
cd bsm_two_photon_optimum
python exact_bsm_verifier.py --case standard_50
python exact_bsm_verifier.py --case grice_75
python exact_bsm_verifier.py --case ewert_two_product_5over8
python exact_bsm_verifier.py --case ewert_four_product_75
python exact_bsm_verifier.py --corruptions-only
```

The Grice witness and the two-product-photon Ewert benchmark are checked by **both** exact amplitude engines over their complete Fock output spaces. The larger six-photon/four-ancilla Ewert benchmark uses the creation-polynomial engine by default; pass `--full-permanent` to request the slower second engine there too.

## Expected benchmark output

- Standard vacuum ancilla: `1/2`.
- Two unentangled ancillary single photons, applied to one Ewert arm: `5/8`.
- Grice two-photon entangled ancilla: `3/4`.
- Four unentangled ancillary single photons, full Ewert circuit: `3/4`.

The corruption suite rejects: nonunitarity, ancilla misnormalization, an exact nonzero cross amplitude, wrong signal-mode ordering, repeated-photon factorial errors, threshold/PNR coarse-graining mistakes, a hidden fifth photon, and double-counted outcome assignment.
