# Optimal two-ancillary-photon Bell-state measurement

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22027744.svg)](https://doi.org/10.5281/zenodo.22027744)

Supplementary material for the manuscript

> Mansehej Singh, *Optimal Unambiguous Dual-Rail Bell-State Measurement with
> Linear Optics and Two Ancillary Photons* (2026).

The main result is

\[
P_2^\star = \frac34,
\]

together with the fixed-photon-number bound
\(P_{\mathrm{succ}} \le (k+1)/(k+2)\) and exact optimality of the Grice
hierarchy at \(k = 2^N - 2\).

Archived on Zenodo under concept DOI
[10.5281/zenodo.22027744](https://doi.org/10.5281/zenodo.22027744), which
always resolves to the latest released version.

## Contents

- `paper/` — the manuscript: LaTeX source, compiled PDFs, bibliography, and
  the arXiv source archive (CC-BY 4.0).
- `verification/` — exact symbolic verification (MIT): two independent
  amplitude engines (matrix permanents and creation-operator polynomial
  expansion), the complete PNR outcome partition for the attaining circuit,
  benchmark cases (1/2, 5/8, 3/4), deliberate corruption tests, and the
  global-bound arithmetic certificate, with machine-readable outputs.
- `lean/` — Lean 4 certificate-layer formalization (MIT) with pinned
  toolchain and dependency manifest, kernel-checked locally and in CI. The
  formalization boundary is documented in `lean/FORMALIZATION_SCOPE.md`.
- `MANIFEST.sha256` — integrity hashes for the distributed files.

## Scope of the theorem

The analytic proof covers arbitrary finite ancillary and vacuum mode counts, an
arbitrary normalized pure exactly-two-photon ancilla, unrestricted static
passive `U(m)`, ideal photon-number-resolving detection, exact unambiguous
pattern assignments, and equal Bell-state priors.

It excludes active Gaussian operations, nonlinearities, feed-forward,
intermediate destructive measurements, extra populated photons, additional
encoding degrees of freedom, and threshold-only detection.

## Exact replay

```bash
cd verification
python3 exact_bsm_verifier.py --case grice_75
python3 exact_bsm_verifier.py --corruptions-only
python3 global_bound_certificate.py
```

Requires Python 3 with SymPy. `run_replay.sh` runs every benchmark.

## License

The code and formalization (`verification/`, `lean/`) are released under the
MIT License (see `LICENSE`). The manuscript and its LaTeX source (`paper/`)
are released under CC-BY 4.0 (see `paper/LICENSE`).
