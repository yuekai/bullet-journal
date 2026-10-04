"""Two-task model, generic g and density, vectorized myopic pricing.

Direction t in [0,1], theta = (t, 1-t), density nu on a grid (unit total mass).
Closed firm prices per unit against free open model; sells to {m(t) >= p},
m(t) = g(theta.a1) - g(theta.a0). Learning: da0 = U0 - a0 ; da1 = U1 + s*U0 - a1.
"""
import numpy as np, itertools, sys

N = 801
T = np.linspace(0, 1, N)
TH = np.stack([T, 1 - T], axis=1)
W = np.full(N, 1.0 / (N - 1)); W[0] = W[-1] = 0.5 / (N - 1)  # trapezoid weights

G = {
    "linear": lambda z: z,
    "sqrt": lambda z: np.sqrt(np.maximum(z, 0)),
    "log1p": lambda z: np.log1p(np.maximum(z, 0)),
}

def beta_density(a, b):
    from math import gamma
    w = T**(a - 1) * (1 - T)**(b - 1) * gamma(a + b) / (gamma(a) * gamma(b))
    return w / (w * W).sum()

NU = {"uniform": np.ones(N), "beta(2,5)": beta_density(2, 5)}

def step_info(a0, a1, s, g, nu):
    m = g(TH @ a1) - g(TH @ a0)
    mass = nu * W
    order = np.argsort(-m)                      # descending margin
    ms = m[order]; cum = np.cumsum(mass[order])  # mass with margin >= ms[k]
    prof = np.where(ms > 1e-12, ms * cum, -1.0)
    k = int(np.argmax(prof))
    if prof[k] <= 0:
        p = 0.0; sel = np.zeros(N, bool)
    else:
        p = float(ms[k]); sel = m >= p
    U1 = (mass * sel) @ TH
    U0 = (mass * ~sel) @ TH
    return U0, U1, p, float((mass * sel).sum())

def simulate(a0, a1, s, g, nu, Tend=100.0, dt=0.05):
    a0 = np.array(a0, float); a1 = np.array(a1, float)
    for _ in range(int(Tend / dt)):
        U0, U1, p, sh = step_info(a0, a1, s, g, nu)
        a0 = np.maximum(a0 + dt * (U0 - a0), 0)
        a1 = np.maximum(a1 + dt * (U1 + s * U0 - a1), 0)
    U0, U1, p, sh = step_info(a0, a1, s, g, nu)
    return a0, a1, p, sh

def classify(sh):
    if sh > 0.99: return "closed takes all"
    if sh < 0.01: return "open takes all"
    return "interior"

if __name__ == "__main__":
    rng = np.random.default_rng(0)
    starts = [(rng.uniform(0, 1, 2), rng.uniform(0, 1, 2)) for _ in range(16)]
    for gname, nuname in itertools.product(["linear", "sqrt", "log1p"], ["uniform", "beta(2,5)"]):
        g = G[gname]; nu = NU[nuname]
        print(f"\n=== g={gname}, nu={nuname} ===")
        for s in [0.0, 0.5, 0.9, 1.0]:
            outcomes = {}
            for a0, a1 in starts:
                a0f, a1f, p, sh = simulate(a0, a1, s, g, nu)
                outcomes.setdefault(classify(sh), []).append((a0f.round(3), a1f.round(3), round(p, 3), round(sh, 3)))
            print(f"s={s}: " + ", ".join(f"{k}: {len(v)}/16" for k, v in outcomes.items()))
            for k, v in outcomes.items():
                if k == "interior":
                    for a0f, a1f, p, sh in v[:3]:
                        print(f"    interior: a0={a0f} a1={a1f} p={p} closed share={sh}")
            sys.stdout.flush()

    print("\n=== perturbation test, linear/uniform, s=0.5 interior fp (t*=0.288) ===")
    t = 0.288
    U1 = np.array([(1 - t**2) / 2, (1 - t)**2 / 2]); U0 = np.array([t**2 / 2, t - t**2 / 2])
    a0s = U0; a1s = U1 + 0.5 * U0
    for eps in [-0.01, 0.01]:
        _, _, _, sh = simulate(a0s, a1s + np.array([eps, 0]), 0.5, G["linear"], NU["uniform"])
        print(f"a1 task-1 {eps:+.2f}: {classify(sh)}")
        _, _, _, sh = simulate(a0s + np.array([0, eps]), a1s, 0.5, G["linear"], NU["uniform"])
        print(f"a0 task-2 {eps:+.2f}: {classify(sh)}")
