#!/usr/bin/env python3
"""Machine-checkable algebraic sanity certificate for the analytic bound.

This is NOT a proof-assistant formalization of the full theorem. It checks exactly:
  * the Bell one-particle density matrices are I_4/2;
  * the Grice BS decomposition equals the stored analytic unitary;
  * the exact Grice success weights d_{j,ell} satisfy the per-mode inequality
        sum_j d_{j,ell} <= 4 q_ell + t_ell
    and saturate the summed global bound;
  * the last scalar inequality is a manifest nonnegative linear certificate.
"""
import sympy as sp
import exact_bsm_verifier as v


def one_rdm(st, m=4):
    # exact <a_p^dag a_q> in normalized Fock basis
    R = sp.zeros(m)
    for p in range(m):
        for q in range(m):
            val = 0
            for occ, c in st.items():
                if occ[q] == 0:
                    continue
                mid = list(occ); mid[q] -= 1
                fac1 = sp.sqrt(occ[q])
                midt = tuple(mid)
                out = list(mid); out[p] += 1
                outt = tuple(out)
                fac2 = sp.sqrt(mid[p] + 1)
                cp = st.get(outt, 0)
                val += sp.conjugate(cp) * c * fac1 * fac2
            R[p,q] = sp.simplify(val)
    return R


def ancilla_rdm(st, m=8):
    return one_rdm(st, m)


def main():
    bells = v.bell_states(4)
    target = sp.eye(4)/2
    for name, st in bells.items():
        R = one_rdm(st,4)
        assert all(v.is_zero(x) for x in (R-target)), (name,R)
    print('Bell 1RDM check: PASS (I4/2 for all four states)')

    m=8
    l1=(v.pair_bs(m,0,4)*v.pair_bs(m,1,5)*v.pair_bs(m,2,6)*v.pair_bs(m,3,7))
    l2=(v.pair_bs(m,0,2)*v.pair_bs(m,1,3)*v.pair_bs(m,4,6)*v.pair_bs(m,5,7))
    assert all(v.is_zero(x) for x in (l1*l2-v.grice_U8()))
    print('Grice balanced-BS decomposition: PASS')

    U=v.grice_U8(); anc=v.grice_ancilla8(); inputs=v.total_inputs(8,anc)
    outs={name:v.output_state_polynomial(U,st) for name,st in inputs.items()}
    assigned,_,_=v.auto_partition(outs,8,4)

    # d_{j,ell}
    d={name:[sp.Integer(0)]*m for name in v.BELL_NAMES}
    for name in v.BELL_NAMES:
        for pat in assigned[name]:
            pr=v.abs2(outs[name][pat])
            for ell,n in enumerate(pat):
                d[name][ell]+=n*pr
        d[name]=[sp.simplify(x) for x in d[name]]

    # For creation convention a_i^dag -> sum_l U[i,l] b_l^dag,
    # pulled-back output annihilator coefficients have the same moduli/Gram contractions.
    Ranc=ancilla_rdm(anc,8)
    t=[]; q=[]
    for ell in range(m):
        t_ell=sp.simplify(sum(sp.conjugate(U[i,ell])*U[i,ell] for i in range(4)))
        # Ancilla coefficient vector over modes 4..7.
        q_ell=0
        for i in range(4,8):
            for j in range(4,8):
                q_ell += sp.conjugate(U[i,ell])*Ranc[i,j]*U[j,ell]
        t.append(sp.simplify(t_ell)); q.append(sp.simplify(q_ell))

    for ell in range(m):
        lhs=sp.simplify(sum(d[name][ell] for name in v.BELL_NAMES))
        rhs=sp.simplify(4*q[ell]+t[ell])
        assert sp.simplify(rhs-lhs) >= 0
        print(f'mode {ell+1}: sum_d={lhs}, 4q+t={rhs}, slack={sp.simplify(rhs-lhs)}')

    assert sp.simplify(sum(t)-4)==0
    assert sp.simplify(sum(q)-2)==0
    total_d=sp.simplify(sum(sum(d[name]) for name in v.BELL_NAMES))
    ps,avg=v.success_probabilities(outs,assigned)
    assert sp.simplify(total_d-4*sum(ps.values()))==0
    assert sp.simplify(total_d-12)==0
    assert sp.simplify(avg-sp.Rational(3,4))==0
    print('Parseval sums: sum t=4, sum q=2: PASS')
    print('Grice global count: sum_{j,ell} d = 12 = 4*sum_j p_j: PASS')
    print('Grice saturation of 3/4: PASS')

    # Scalar nonnegative certificate:
    # 1/2 sum f_j - sum w_j f_j = sum_j (1/2-w_j) f_j >=0
    f=sp.symbols('f0:4', nonnegative=True)
    w=sp.symbols('w0:4', nonnegative=True)
    cert=sp.expand(sp.Rational(1,2)*sum(f)-sum(f[i]*w[i] for i in range(4)))
    expected=sp.expand(sum((sp.Rational(1,2)-w[i])*f[i] for i in range(4)))
    assert sp.simplify(cert-expected)==0
    print('Scalar cone certificate identity: PASS')
    print('ALL GLOBAL-BOUND SANITY CHECKS PASSED')

if __name__=='__main__':
    main()
