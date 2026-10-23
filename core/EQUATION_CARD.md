# F2a equation card | foundation 1.0.0

**Universal conjecture U:** A common physically constrained law architecture may account for physically realizable processes, including embedded observation, representation, communication and action. This finite implementation is neither a verified TOE nor a new derivation of the imported physical laws.

**F2.1, explicit common continuous operator.** For local extended state z=(x,w), control u, and independent Wiener processes W_a:

    dz_i = P_i(z,u) dt + sum_a Q_ia(z) dW_a,
    P_i = c_i + sum_j A_ij v_j + sum_(j<=k) B_ijk v_j v_k, v=(z,u).

Q has the same degree<=2 sparse polynomial form in z. Every coefficient is stored; absent terms are zero. Local physical dimension d<=8, derived lifts w_j=x^alpha_j with 2<=|alpha_j|<=4, at most min(2d,16) lifts. Identity decoder returns x. Coefficient magnitudes<=1000 in declared units. Operators cannot use a non-neighbour variable. No independent hidden degrees of freedom or world-index encoding is admitted as a derived lift.

**F2.2, lift closure.** C_j(z)=w_j-L_j(x)=0. If dx=f dt+G dW, then

    dw_j = [DL_j f + (1/2) tr(G G^T Hess L_j)] dt + DL_j G dW.

An adapter is admissible only when both expressions have the stated quadratic representation. Lifts are derived observables, not additional physical degrees of freedom. No projection is performed during scored trajectories.

**Completely explicit scalar example.** For r in {2,4}, a,b>=0:

    dx = (-a*x-b*x*w)dt,
    dw = (-r*a*w-r*b*w*w)dt, w(0)=x(0)^r.

The decoder obeys xdot=-a*x-b*x^(r+1); e=w-x^r obeys edot=-r(a+b*w)e. With a=b=1 and r=2, x(0)=0.8, w(0)=0.64, the supplied replay integrates this exact operator. Logistic xdot=a*x-b*x² needs no lift.

**F2.3, clocked typed composition.** K_h = D_h o C o A o U o O. Classical measurement y=Hz+noise (with explicit mask); backaction z^O=Jz+Gy. Internal state updates and action/encoding are stored quadratic maps. Each of two endpoints uses its own sensor and OLD incoming buffer. Each directed FIFO has delay1..4; finite buffers are counted separately. D_h is the actual F2 flow with the resulting controls held fixed. Physical intervention is a distinct logged input, not a coordinate transformation.

**F2.4, finite quantum operator (imported).** L(rho)=-i[H,rho]+sum gamma_a(J_a rho J_a^dagger-{J_a^dagger J_a,rho}/2), Phi_h=exp(h L), hbar=1. H has one/two-site Pauli terms with degree<=2 classical coefficients; fixed nonnegative rates; jumps are Pauli strings plus local lowering/raising. At most two qubits are executed. M_s=sqrt((I+s eta P)/2), |eta|<=1; branch probability Tr(M_s rho M_s^dagger); condition only for positive probability. Only outcomes enter classical memory; no copying of an unknown quantum state.

**F2.5, discrete domain.** Elementary polynomial maps preserve {0,1}^3. CNOT=(a,a+b-2ab,c); erasure=(a,0,c); NOT=(1-a,b,c); rotation=(b,c,a). Ordered compositions act sequentially, not as one approximate transition surrogate.

**Units and solver.** All executed variables use fixed nondimensional reference scales. In dimensional form each drift term has z_i/time and diffusion term z_i/sqrt(time); a monomial lift has product units. Deterministic integration is RK4 (four substeps/tick), stochastic demonstration Ito Euler-Maruyama, linear Gaussian specialization exact matrix-exponential moments, quantum matrix exponential. No global nonexplosion assertion for arbitrary quadratic coefficients: selected scalar manifolds and confining forced Duffing have bounded finite-horizon solutions. Off-manifold states can fail outside declared neighbourhoods.

**What is shared:** polynomial/lift grammar, locality, domain, causal order, finite buffers, quantum library and solver/information contracts. World coefficients and apparatus parameters are supplied or fitted separately. No universal numerical constant, gravity law, Born rule or cross-sector coupling constant is derived.
