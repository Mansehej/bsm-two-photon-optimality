# Lean certificate project

Pinned versions:

- Lean `v4.31.0`
- mathlib `v4.31.0`

Build:

```bash
lake exe cache get
lake build
python3 scripts/check_no_placeholders.py
```

The root module is `BellMeasurement.lean`. See `FORMALIZATION_SCOPE.md` for the exact
formalization boundary and `local_build_2026-08-19.log` for the kernel-check
record.
