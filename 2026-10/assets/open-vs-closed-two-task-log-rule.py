"""Two-task open-vs-closed LLM model: alternative 1 with log per-unit value.

Users: unit usage, task mix theta = (t, 1-t), t in [0,1], density nu (unit mass).
Models: open (0) at price 0, one closed firm (1) with per-unit price p.
Per-unit utility: u_j = log(theta . a_j) - p_j. No outside option.
Closed firm prices myopically: max_p p * nu({ m >= p }), m = log(theta.a1) - log(theta.a0).
Learning (stocks, no depreciation): da0 = g*U0 ; da1 = g*(U1 + s*U0), g = 1.
"""
import numpy as np, itertools, sys

N = 801
T = np.linspace(0, 1, N)
TH = np.stack([T, 1 - T], axis=1)
W = np.full(N, 1.0 / (N - 1)); W[0] = W[-1] = 0.5 / (N - 1)

def beta_density(a, b):
    from math import gamma
    w = T**(a - 1) * (1 - T)**(b - 1) * gamma(a + b) / (gamma(a) * gamma(b))
    return w / (w * W).sum()

NU = {"uniform": np.ones(N), "beta(2,5)": beta_density(2, 5)}

def step_info(a0, a1, nu):
    m = np.log(TH @ a1) - np.log(TH @ a0)
    mass = nu * W
    order = np.argsort(-m); ms = m[order]; cum = np.cumsum(mass[order])
    prof = np.where(ms > 1e-12, ms * cum, -1.0)
    k = int(np.argmax(prof))
    if prof[k] <= 0:
        p, sel = 0.0, np.zeros(N, bool)
    else:
        p, sel = float(ms[k]), m >= ms[k]
    U1 = (mass * sel) @ TH; U0 = (mass * ~sel) @ TH
    return U0, U1, p, float((mass * sel).sum())

def simulate(a0, a1, s, nu, Tend=400.0, dt=0.05, trace=False):
    a0 = np.array(a0, float); a1 = np.array(a1, float)
    path = []
    n = int(Tend / dt)
    for i in range(n):
        U0, U1, p, sh = step_info(a0, a1, nu)
        if trace and i % int(20 / dt) == 0:
            path.append((round(i * dt, 1), round(sh, 3), round(p, 3)))
        a0 = a0 + dt * U0; a1 = a1 + dt * (U1 + s * U0)
    U0, U1, p, sh = step_info(a0, a1, nu)
    return dict(a0=a0, a1=a1, p=p, closed_share=sh, U0=U0, U1=U1, ratio=a1 / a0, path=path)

def classify(r):
    sh = r["closed_share"]
    if sh > 0.999: return "closed takes all (open frozen)"
    if sh < 0.001: return "open takes all"
    return "interior"

if __name__ == "__main__":
    rng = np.random.default_rng(0)
    rand_starts = [(rng.uniform(0.1, 1, 2), rng.uniform(0.1, 1, 2)) for _ in range(16)]
    struct = {
        "closed leads x1.05": ([0.5, 0.5], [0.525, 0.525]),
        "closed leads x2": ([0.5, 0.5], [1.0, 1.0]),
        "closed leads, lopsided": ([0.5, 0.5], [1.5, 0.6]),
        "open leads x1.05": ([0.525, 0.525], [0.5, 0.5]),
        "open leads on task 2 only": ([0.5, 0.7], [0.6, 0.5]),
    }
    for nuname in ["uniform", "beta(2,5)"]:
        nu = NU[nuname]
        print(f"\n=== nu={nuname} ===")
        for s in [0.0, 0.5, 0.9, 1.0]:
            out = {}
            for a0, a1 in rand_starts:
                r = simulate(a0, a1, s, nu); out.setdefault(classify(r), []).append(r)
            print(f"s={s}: random starts -> " + ", ".join(f"{k}: {len(v)}/16" for k, v in out.items()))
            for k, v in out.items():
                if k == "interior":
                    shares = sorted(round(r['closed_share'], 3) for r in v)
                    r = v[0]
                    print(f"    interior closed shares: {shares}")
                    print(f"    example: p={r['p']:.3f} ratio a1/a0=({r['ratio'][0]:.2f},{r['ratio'][1]:.2f}) U1={r['U1'].round(3)} U0={r['U0'].round(3)}")
            for name, (a0, a1) in struct.items():
                r = simulate(a0, a1, s, nu)
                print(f"    {name:26s} -> {classify(r):30s} share={r['closed_share']:.3f} p={r['p']:.3f} ratio=({r['ratio'][0]:.2f},{r['ratio'][1]:.2f})")
            sys.stdout.flush()
    print("\n=== convergence check: beta(2,5), s=0.5, closed leads x2, closed share and price over time ===")
    r = simulate([0.5, 0.5], [1.0, 1.0], 0.5, NU["beta(2,5)"], Tend=800.0, trace=True)
    print(r["path"][::4])
