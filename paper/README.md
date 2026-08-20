# Research manuscript

This directory contains the clean scientific paper only.

- `main.tex` — complete LaTeX source.
- `bsm_two_photon_optimality.pdf` — compiled 10-page A4 preprint (without AI-assistance acknowledgment).
- `references.bib` — machine-readable bibliography data; `main.tex` uses an
  inline bibliography for a dependency-free build.
- `bsm_two_photon_optimality_with_acknowledgment.pdf` — same manuscript with
  the AI-assistance acknowledgment section.
- `arxiv_source.tar.gz` — submission source archive: `main.tex` plus `anc/`
  ancillary files (exact verification code and machine-readable certificates).

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
