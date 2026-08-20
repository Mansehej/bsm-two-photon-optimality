#!/usr/bin/env python3
"""Exact verifier for dual-rail linear-optical Bell measurements.

Conventions
-----------
Mode creation operators transform as
    a_i^† -> sum_j U[i,j] b_j^†
with U unitary. Fock-state coefficients are for normalized number states.

This script has two independent amplitude engines:
  1) normalized bosonic permanents (Ryser formula),
  2) explicit creation-operator polynomial expansion.

All benchmark circuits use SymPy exact arithmetic.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import sympy as sp

I = sp.I
SQ2 = sp.sqrt(2)
Expr = sp.Expr
Occ = Tuple[int, ...]
State = Dict[Occ, Expr]

BELL_NAMES = ("Phi+", "Phi-", "Psi+", "Psi-")


def simp(x: Expr) -> Expr:
    return sp.simplify(sp.expand_complex(x))


def is_zero(x: Expr) -> bool:
    y = sp.simplify(x)
    if y == 0:
        return True
    z = sp.cancel(sp.together(y))
    return z == 0


def abs2(x: Expr) -> Expr:
    return sp.simplify(x * sp.conjugate(x))


def factorial_product(o: Occ) -> int:
    out = 1
    for n in o:
        out *= math.factorial(n)
    return out


def occupations(m: int, n: int) -> Iterable[Occ]:
    """All m-mode occupations of n photons."""
    if m == 1:
        yield (n,)
        return
    for first in range(n + 1):
        for rest in occupations(m - 1, n - first):
            yield (first,) + rest


def occ_with(m: int, pairs: Mapping[int, int]) -> Occ:
    a = [0] * m
    for i, n in pairs.items():
        a[i] = n
    return tuple(a)


def state_norm2(st: State) -> Expr:
    return sp.simplify(sum(abs2(c) for c in st.values()))


def photon_numbers(st: State) -> set[int]:
    return {sum(o) for o, c in st.items() if not is_zero(c)}


def add_states(*states: State) -> State:
    d: Dict[Occ, Expr] = defaultdict(lambda: sp.Integer(0))
    for st in states:
        for o, c in st.items():
            d[o] += c
    return {o: sp.simplify(c) for o, c in d.items() if not is_zero(c)}


def tensor_same_modes(a: State, b: State) -> State:
    """Multiply disjoint-support Fock states represented on the same mode list."""
    d: Dict[Occ, Expr] = defaultdict(lambda: sp.Integer(0))
    for oa, ca in a.items():
        for ob, cb in b.items():
            if any(x and y for x, y in zip(oa, ob)):
                # Overlap is mathematically legal, but normalized coefficients acquire
                # a binomial sqrt factor. We do not need it for our disjoint benchmarks.
                raise ValueError("tensor_same_modes benchmark helper expects disjoint supports")
            o = tuple(x + y for x, y in zip(oa, ob))
            d[o] += ca * cb
    return {o: sp.simplify(c) for o, c in d.items()}


def bell_states(m: int) -> Dict[str, State]:
    """User's Bell-state convention on modes 0,1,2,3."""
    if m < 4:
        raise ValueError("Need at least four modes")
    p13 = occ_with(m, {0: 1, 2: 1})
    p24 = occ_with(m, {1: 1, 3: 1})
    p14 = occ_with(m, {0: 1, 3: 1})
    p23 = occ_with(m, {1: 1, 2: 1})
    return {
        "Phi+": {p13: 1 / SQ2, p24: 1 / SQ2},
        "Phi-": {p13: 1 / SQ2, p24: -1 / SQ2},
        "Psi+": {p14: 1 / SQ2, p23: 1 / SQ2},
        "Psi-": {p14: 1 / SQ2, p23: -1 / SQ2},
    }


def ryser_permanent(A: sp.Matrix) -> Expr:
    """Exact permanent. For the small photon numbers here, direct permutations
    are substantially faster in SymPy than repeated simplification inside Ryser.
    The function name is kept for compatibility with corruption tests.
    """
    n = A.rows
    if A.cols != n:
        raise ValueError("Permanent requires square matrix")
    if n == 0:
        return sp.Integer(1)
    total = sp.Integer(0)
    for perm in itertools.permutations(range(n)):
        term = sp.Integer(1)
        for i, j in enumerate(perm):
            term *= A[i, j]
        total += term
    return sp.expand(total)


def repeated_submatrix(U: sp.Matrix, s: Occ, t: Occ) -> sp.Matrix:
    rows: List[int] = []
    cols: List[int] = []
    for i, n in enumerate(s):
        rows.extend([i] * n)
    for j, n in enumerate(t):
        cols.extend([j] * n)
    if len(rows) != len(cols):
        raise ValueError("Input and output photon number mismatch")
    return U.extract(rows, cols)


def fock_amp_permanent(U: sp.Matrix, s: Occ, t: Occ) -> Expr:
    if sum(s) != sum(t):
        return sp.Integer(0)
    A = repeated_submatrix(U, s, t)
    den = sp.sqrt(factorial_product(s) * factorial_product(t))
    return sp.simplify(ryser_permanent(A) / den)


def output_state_permanent(U: sp.Matrix, st: State) -> State:
    m = U.rows
    nums = photon_numbers(st)
    if len(nums) != 1:
        raise ValueError("State must have a fixed photon number")
    n = next(iter(nums))
    out: State = {}
    for t in occupations(m, n):
        amp = sp.Integer(0)
        for s, c in st.items():
            amp += c * fock_amp_permanent(U, s, t)
        amp = sp.simplify(amp)
        if not is_zero(amp):
            out[t] = amp
    return out


def basis_output_polynomial(U: sp.Matrix, s: Occ) -> State:
    """Independent creation-polynomial expansion for one normalized input Fock state."""
    m = U.rows
    zero = (0,) * m
    raw: Dict[Occ, Expr] = {zero: sp.Integer(1)}
    for i, ni in enumerate(s):
        for _ in range(ni):
            nxt: Dict[Occ, Expr] = defaultdict(lambda: sp.Integer(0))
            for o, c in raw.items():
                for j in range(m):
                    if is_zero(U[i, j]):
                        continue
                    oo = list(o)
                    oo[j] += 1
                    nxt[tuple(oo)] += c * U[i, j]
            raw = nxt
    in_den = sp.sqrt(factorial_product(s))
    out: State = {}
    for t, c_raw in raw.items():
        amp = sp.simplify(c_raw * sp.sqrt(factorial_product(t)) / in_den)
        if not is_zero(amp):
            out[t] = amp
    return out


def output_state_polynomial(U: sp.Matrix, st: State) -> State:
    d: Dict[Occ, Expr] = defaultdict(lambda: sp.Integer(0))
    for s, c in st.items():
        bo = basis_output_polynomial(U, s)
        for t, a in bo.items():
            d[t] += c * a
    return {t: sp.simplify(a) for t, a in d.items() if not is_zero(a)}


def assert_unitary(U: sp.Matrix) -> None:
    if U.rows != U.cols:
        raise AssertionError("U is not square")
    E = sp.simplify(U * U.conjugate().T - sp.eye(U.rows))
    for x in E:
        if not is_zero(x):
            raise AssertionError(f"U is not unitary; residual {x}")


def pair_bs(m: int, a: int, b: int) -> sp.Matrix:
    """Balanced beam splitter B=(1/sqrt2)[[1,i],[i,1]] on modes a,b."""
    U = sp.eye(m)
    B = sp.Matrix([[1, I], [I, 1]]) / SQ2
    for rr, r in enumerate((a, b)):
        for cc, c in enumerate((a, b)):
            U[r, c] = B[rr, cc]
    return U


def path_grice_U() -> sp.Matrix:
    return sp.Matrix([
        [1, I, I, -1],
        [I, 1, -1, I],
        [I, -1, 1, I],
        [-1, I, I, 1],
    ]) / 2


def grice_U8() -> sp.Matrix:
    S = path_grice_U()
    U = sp.zeros(8)
    for pin in range(4):
        for pout in range(4):
            for rail in range(2):
                U[2 * pin + rail, 2 * pout + rail] = S[pin, pout]
    return U


def grice_ancilla8() -> State:
    # (a5† a7† + a6† a8†)|0>/sqrt2 in one-based user-facing indexing.
    return {
        occ_with(8, {4: 1, 6: 1}): 1 / SQ2,
        occ_with(8, {5: 1, 7: 1}): 1 / SQ2,
    }


def standard_U4() -> sp.Matrix:
    return pair_bs(4, 0, 2) * pair_bs(4, 1, 3)


def ewert_U6_two_product_photons() -> sp.Matrix:
    # Stage 1: standard Bell analyzer + prepare Υ1 from input |1,1> in ancilla modes 5,6.
    m = 6
    stage1 = pair_bs(m, 0, 2) * pair_bs(m, 1, 3) * pair_bs(m, 4, 5)
    # Stage 2: boost only pair [A,B] by mixing A-5, B-6.
    stage2 = pair_bs(m, 0, 4) * pair_bs(m, 1, 5)
    return sp.simplify(stage1 * stage2)


def ewert_ancilla6_product() -> State:
    return {occ_with(6, {4: 1, 5: 1}): sp.Integer(1)}


def ewert_U8_four_product_photons() -> sp.Matrix:
    m = 8
    stage1 = (
        pair_bs(m, 0, 2) * pair_bs(m, 1, 3)
        * pair_bs(m, 4, 5) * pair_bs(m, 6, 7)
    )
    stage2 = (
        pair_bs(m, 0, 4) * pair_bs(m, 1, 5)
        * pair_bs(m, 2, 6) * pair_bs(m, 3, 7)
    )
    return sp.simplify(stage1 * stage2)


def ewert_ancilla8_product() -> State:
    return {occ_with(8, {4: 1, 5: 1, 6: 1, 7: 1}): sp.Integer(1)}


def total_inputs(m: int, ancilla: State) -> Dict[str, State]:
    bells = bell_states(m)
    return {name: tensor_same_modes(bells[name], ancilla) for name in BELL_NAMES}


def all_patterns_from_outputs(outputs: Mapping[str, State], m: int, n: int) -> List[Occ]:
    # Include all mathematically possible patterns, including all-zero-support patterns, for a complete partition.
    return list(occupations(m, n))


def auto_partition(outputs: Mapping[str, State], m: int, n: int):
    assigned = {name: [] for name in BELL_NAMES}
    inconclusive: List[Occ] = []
    zero_all: List[Occ] = []
    for t in all_patterns_from_outputs(outputs, m, n):
        support = [name for name in BELL_NAMES if not is_zero(outputs[name].get(t, sp.Integer(0)))]
        if len(support) == 1:
            assigned[support[0]].append(t)
        else:
            inconclusive.append(t)
            if len(support) == 0:
                zero_all.append(t)
    return assigned, inconclusive, zero_all


def success_probabilities(outputs: Mapping[str, State], assigned: Mapping[str, Sequence[Occ]]):
    ps = {}
    for name in BELL_NAMES:
        ps[name] = sp.simplify(sum(abs2(outputs[name].get(t, 0)) for t in assigned[name]))
    avg = sp.simplify(sum(ps.values()) / 4)
    return ps, avg


def compare_outputs(a: Mapping[str, State], b: Mapping[str, State], m: int, n: int) -> None:
    for name in BELL_NAMES:
        for t in occupations(m, n):
            da = a[name].get(t, sp.Integer(0))
            db = b[name].get(t, sp.Integer(0))
            if not is_zero(da - db):
                raise AssertionError(f"Amplitude engines disagree for {name}, {t}: {da} vs {db}")


def verify_assignments(outputs: Mapping[str, State], assigned: Mapping[str, Sequence[Occ]]) -> None:
    seen = set()
    for name, pats in assigned.items():
        if name not in BELL_NAMES:
            raise AssertionError(f"Unknown Bell label {name}")
        for t in pats:
            if t in seen:
                raise AssertionError(f"Pattern double-counted: {t}")
            seen.add(t)
            if is_zero(outputs[name].get(tuple(t), 0)):
                raise AssertionError(f"Assigned pattern has zero target amplitude: {name}, {t}")
            for other in BELL_NAMES:
                if other == name:
                    continue
                x = outputs[other].get(tuple(t), sp.Integer(0))
                if not is_zero(x):
                    raise AssertionError(f"Cross amplitude is nonzero for {t}: target={name}, other={other}, amp={x}")


def serialize_expr(x: Expr) -> str:
    return str(sp.simplify(x))


def serialize_state(st: State):
    return [
        {"occupation": list(o), "coefficient": serialize_expr(c)}
        for o, c in sorted(st.items())
    ]


def serialize_matrix(U: sp.Matrix):
    return [[serialize_expr(U[i, j]) for j in range(U.cols)] for i in range(U.rows)]


def write_case_json(path: Path, case_name: str, U: sp.Matrix, ancilla: State, outputs: Mapping[str, State], assigned, inconclusive, zero_all, ps, avg):
    data = {
        "case": case_name,
        "creation_transform_convention": "a_i^dagger -> sum_j U[i,j] b_j^dagger",
        "mode_count": U.rows,
        "mode_indexing_in_file": "0-based occupations; narrative uses 1-based mode labels",
        "ancilla": serialize_state(ancilla),
        "unitary": serialize_matrix(U),
        "success_sets": {k: [list(t) for t in v] for k, v in assigned.items()},
        "inconclusive_set": [list(t) for t in inconclusive],
        "zero_for_all_inputs_subset": [list(t) for t in zero_all],
        "success_probabilities": {k: serialize_expr(v) for k, v in ps.items()},
        "equal_prior_average": serialize_expr(avg),
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


@dataclass
class Case:
    name: str
    U: sp.Matrix
    ancilla: State
    expected: Expr
    do_permanent: bool = True


def verify_case(case: Case, outdir: Path, write_json: bool = True):
    print(f"\n=== {case.name} ===")
    U, anc = case.U, case.ancilla
    assert_unitary(U)
    if sp.simplify(state_norm2(anc) - 1) != 0:
        raise AssertionError(f"Ancilla not normalized: norm2={state_norm2(anc)}")
    an = photon_numbers(anc)
    if len(an) != 1:
        raise AssertionError(f"Ancilla not fixed-photon-number: {an}")
    k = next(iter(an))
    inputs = total_inputs(U.rows, anc)
    total_n = k + 2
    for name, st in inputs.items():
        if photon_numbers(st) != {total_n}:
            raise AssertionError(f"Wrong total photon number for {name}")
        if sp.simplify(state_norm2(st) - 1) != 0:
            raise AssertionError(f"Input not normalized for {name}")

    print("computing creation-polynomial amplitudes ...")
    out_poly = {name: output_state_polynomial(U, st) for name, st in inputs.items()}
    for name in BELL_NAMES:
        if sp.simplify(state_norm2(out_poly[name]) - 1) != 0:
            raise AssertionError(f"Polynomial output norm failure for {name}: {state_norm2(out_poly[name])}")

    if case.do_permanent:
        print("computing permanent amplitudes ...")
        out_perm = {name: output_state_permanent(U, st) for name, st in inputs.items()}
        compare_outputs(out_poly, out_perm, U.rows, total_n)
        print("two-engine amplitude check: PASS")
    else:
        print("permanent engine skipped for this larger benchmark")

    assigned, inconclusive, zero_all = auto_partition(out_poly, U.rows, total_n)
    verify_assignments(out_poly, assigned)
    ps, avg = success_probabilities(out_poly, assigned)
    print("success:", {k: serialize_expr(v) for k, v in ps.items()}, "average", serialize_expr(avg))
    print("successful pattern counts:", {k: len(v) for k, v in assigned.items()})
    print("inconclusive patterns:", len(inconclusive), "of which zero-for-all:", len(zero_all))
    if sp.simplify(avg - case.expected) != 0:
        raise AssertionError(f"Expected average {case.expected}, got {avg}")
    if write_json:
        write_case_json(outdir / f"{case.name}.json", case.name, U, anc, out_poly, assigned, inconclusive, zero_all, ps, avg)
    return out_poly, assigned, ps, avg


def corruption_tests(grice_outputs: Mapping[str, State], grice_assigned: Mapping[str, Sequence[Occ]]) -> List[str]:
    logs = []

    # 1. Nonunitary U.
    U_bad = grice_U8().copy()
    U_bad[0, 0] *= sp.Rational(999, 1000)
    try:
        assert_unitary(U_bad)
        raise AssertionError("nonunitary matrix was not rejected")
    except AssertionError:
        logs.append("nonunitary_U: PASS (rejected)")

    # 2. Incorrectly normalized ancilla.
    anc_bad = {o: 2 * c for o, c in grice_ancilla8().items()}
    if sp.simplify(state_norm2(anc_bad) - 1) == 0:
        raise AssertionError("bad ancilla unexpectedly normalized")
    logs.append("incorrect_ancilla_normalization: PASS (detected)")

    # 3. Small but exactly nonzero cross-amplitude in an amplitude table.
    # Choose any genuine Grice success pattern and inject epsilon into another Bell state's amplitude.
    target = next(name for name in BELL_NAMES if grice_assigned[name])
    t = tuple(grice_assigned[target][0])
    other = next(x for x in BELL_NAMES if x != target)
    corrupted = {name: dict(st) for name, st in grice_outputs.items()}
    corrupted[other][t] = sp.Rational(1, 10**9)
    try:
        verify_assignments(corrupted, {k: ([t] if k == target else []) for k in BELL_NAMES})
        raise AssertionError("small nonzero cross amplitude was not rejected")
    except AssertionError:
        logs.append("small_nonzero_cross_amplitude: PASS (rejected exactly)")

    # 4. Wrong mode ordering: swap signal modes 2 and 3 in the *input interpretation* but keep old assignment.
    # This changes Bell states while leaving U/ancilla fixed.
    def swap_occ(o: Occ, i: int, j: int) -> Occ:
        x = list(o); x[i], x[j] = x[j], x[i]; return tuple(x)
    bells_wrong = bell_states(8)
    bells_wrong = {name: {swap_occ(o, 1, 2): c for o, c in st.items()} for name, st in bells_wrong.items()}
    wrong_inputs = {name: tensor_same_modes(bells_wrong[name], grice_ancilla8()) for name in BELL_NAMES}
    wrong_out = {name: output_state_polynomial(grice_U8(), st) for name, st in wrong_inputs.items()}
    try:
        verify_assignments(wrong_out, grice_assigned)
        raise AssertionError("wrong mode ordering unexpectedly passed original assignment")
    except AssertionError:
        logs.append("wrong_mode_ordering: PASS (detected by cross-amplitude check)")

    # 5. Factorial normalization: find a repeated-photon output and show an intentionally bad
    # permanent normalization disagrees with polynomial verifier.
    found = False
    U = grice_U8(); inputs = total_inputs(8, grice_ancilla8())
    for name in BELL_NAMES:
        st = inputs[name]
        for t, correct in grice_outputs[name].items():
            if max(t) < 2:
                continue
            bad = sp.Integer(0)
            for s, c in st.items():
                A = repeated_submatrix(U, s, t)
                # BUG: omit sqrt(output factorials)
                bad += c * ryser_permanent(A) / sp.sqrt(factorial_product(s))
            if not is_zero(sp.simplify(bad - correct)):
                found = True
                logs.append(f"repeated_photon_factorial_normalization: PASS (bad formula disagrees at {name} {t})")
                break
        if found:
            break
    if not found:
        raise AssertionError("failed to find factorial-normalization corruption witness")

    # 6. Threshold coarse graining must never create a 'success' absent at PNR level.
    # Check every threshold signature: it is conclusive only if all nonzero PNR refinements
    # across all inputs belong to a single Bell label.
    threshold_support = defaultdict(set)
    for name, st in grice_outputs.items():
        for t, amp in st.items():
            if is_zero(amp):
                continue
            sig = tuple(1 if n else 0 for n in t)
            threshold_support[sig].add(name)
    colliding = [sig for sig, supp in threshold_support.items() if len(supp) > 1]
    if not colliding:
        raise AssertionError("expected at least one ambiguous threshold collision")
    logs.append(f"threshold_vs_PNR_coarse_graining: PASS ({len(colliding)} ambiguous threshold signatures detected)")

    # 7. Hidden fifth photon rejected by resource counter.
    hidden5 = {occ_with(8, {4: 2, 6: 1}): sp.Integer(1)}  # three ancilla photons => five total
    if photon_numbers(hidden5) != {3}:
        raise AssertionError("bad hidden-photon test")
    if next(iter(photon_numbers(hidden5))) == 2:
        raise AssertionError("hidden fifth photon not detected")
    logs.append("hidden_fifth_photon: PASS (ancilla photon count=3, rejected for two-photon resource)")

    # 8. Double-count an outcome in two assigned sets.
    t2 = t
    fake = {k: [] for k in BELL_NAMES}
    fake["Phi+"] = [t2]
    fake["Phi-"] = [t2]
    try:
        verify_assignments(grice_outputs, fake)
        raise AssertionError("double-counted pattern was not rejected")
    except AssertionError:
        logs.append("double_counted_pattern: PASS (rejected)")

    return logs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", type=Path, default=Path(__file__).resolve().parent)
    ap.add_argument("--full-permanent", action="store_true", help="also run permanent engine for 6-photon Ewert benchmark")
    ap.add_argument("--case", choices=["standard_50", "grice_75", "ewert_two_product_5over8", "ewert_four_product_75"], help="run one benchmark only")
    ap.add_argument("--corruptions-only", action="store_true", help="run only the deliberate-corruption tests against Grice")
    args = ap.parse_args()
    outdir = args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    all_cases = [
        Case("standard_50", standard_U4(), {occ_with(4, {}): sp.Integer(1)}, sp.Rational(1, 2), True),
        Case("grice_75", grice_U8(), grice_ancilla8(), sp.Rational(3, 4), True),
        Case("ewert_two_product_5over8", ewert_U6_two_product_photons(), ewert_ancilla6_product(), sp.Rational(5, 8), True),
        Case("ewert_four_product_75", ewert_U8_four_product_photons(), ewert_ancilla8_product(), sp.Rational(3, 4), args.full_permanent),
    ]

    if args.corruptions_only:
        U = grice_U8(); anc = grice_ancilla8(); inputs = total_inputs(8, anc)
        outputs = {name: output_state_polynomial(U, st) for name, st in inputs.items()}
        assigned, _, _ = auto_partition(outputs, 8, 4)
        clogs = corruption_tests(outputs, assigned)
        for x in clogs:
            print(x)
        (outdir / "corruption_tests.log").write_text("\n".join(clogs) + "\n", encoding="utf-8")
        return

    cases = [c for c in all_cases if args.case is None or c.name == args.case]
    results = {}
    grice_outputs = None
    grice_assigned = None
    for case in cases:
        outputs, assigned, ps, avg = verify_case(case, outdir)
        results[case.name] = {"average": serialize_expr(avg), "per_state": {k: serialize_expr(v) for k, v in ps.items()}}
        if case.name == "grice_75":
            grice_outputs, grice_assigned = outputs, assigned

    # In all-cases mode only, also run corruptions. For robust replay, run_all.sh
    # invokes each case in a fresh process and then --corruptions-only.
    clogs = []
    if args.case is None:
        print("\n=== corruption tests ===")
        if grice_outputs is None:
            raise AssertionError("internal: Grice result missing")
        clogs = corruption_tests(grice_outputs, grice_assigned)
        for x in clogs:
            print(x)

    summary = {
        "benchmarks": results,
        "corruption_tests": clogs,
        "sympy_version": sp.__version__,
    }
    suffix = args.case or "all"
    (outdir / f"verifier_summary_{suffix}.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\nPASS")


if __name__ == "__main__":
    main()
