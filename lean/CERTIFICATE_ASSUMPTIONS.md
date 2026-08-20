# Meaning of the scalar certificate variables

For one output mode `ell`:

- `q` is the ancillary expectation `q_ell = <chi|r_ell^† r_ell|chi>`;
- `t` is the squared signal coefficient norm `t_ell = ||s_ell||^2`;
- `d0,...,d3` are successful detected-photon weights `d_{j,ell}`;
- `f_j = q+t/2-d_j` are residual Gram diagonal entries and are nonnegative;
- `w_j=|z_j|^2` are Bell-basis weights of a product state in the signal
  annihilator kernel, with `w_j <= 1/2`;
- positive semidefiniteness supplies `t/2 <= sum_j f_j w_j`.

`per_mode_success_bound` proves exactly that these hypotheses imply
`d0+d1+d2+d3 <= 4q+t`.
