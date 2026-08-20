# Research manuscript

This directory contains the clean scientific paper only.

- `main.tex` — complete LaTeX source.
- `bsm_two_photon_optimality.pdf` — compiled 10-page A4 preprint.
- `references.bib` — machine-readable bibliography data; `main.tex` uses an
  inline bibliography for a dependency-free build.

The main manuscript is intentionally limited to the scientific contribution:
problem context, resource model, theorem, proof, general corollary, attaining
construction, and implications. Computational verification, development audits,
and Lean implementation details are kept outside the paper.

Build with:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

or, without a TeX Live installation:

```bash
tectonic main.tex
```

For arXiv submission, build the source archive on demand:

```bash
mkdir -p anc && cp ../verification/{exact_bsm_verifier.py,global_bound_certificate.py,README.md,grice_75.json,grice_decomposition.json,verifier_summary_grice_75.json} anc/
tar czf arxiv_source.tar.gz main.tex anc
```
