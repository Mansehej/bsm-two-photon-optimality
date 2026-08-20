#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python exact_bsm_verifier.py --case standard_50
python exact_bsm_verifier.py --case grice_75
python exact_bsm_verifier.py --case ewert_two_product_5over8
python exact_bsm_verifier.py --case ewert_four_product_75
python exact_bsm_verifier.py --corruptions-only
python global_bound_certificate.py
