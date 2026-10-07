"""Open-vs-closed LLM model with diminishing returns in overall quality.

Learning: da0 = U0 / ||a0||^eta ;  da1 = (U1 + s*U0) / ||a1||^eta   (gamma = 1, L2 norm).
Users: unit usage, task mix theta on the simplex, density nu. Per-unit utility log(theta.a_j) - p_j,
no outside option. One closed firm prices myopically per unit against a free open model.
Compares eta in {0, 0.5, 1, 2} on two- and three-task densities. Self-contained.
"""
import numpy as np, sys
from math import gamma as Gf

# ---- two-task grid: theta = (t, 1-t) ----
N2 = 801
T2 = np.linspace(0, 1, N2)
TH2 = np.stack([T2, 1 - T2], axis=1)
W2 = np.full(N2, 1.0 / (N2 - 1)); W2[0] = W2[-1] = 0.5 / (N2 - 1)

def beta_mass(a, b):
    w = T2**(a - 1) * (1 - T2)**(b - 1)
    w = w / (w * W2).sum()
    return w * W2

MASS2 = {"uniform": np.ones(N2) * W2, "beta(2,5)": beta_mass(2, 5)}

# ---- three-task grid: theta_k = i_k / H ----
H = 60
pts = [(i, j, H - i - j) for i in range(H + 1) for j in range(H + 1 - i)]
TH3 = np.array(pts, float) / H

def dirichlet_mass(alpha):
    alpha = np.array(alpha, float); th = np.clip(TH3, 1e-9, None)
    logw = ((alpha - 1) * np.log(th)).sum(1); w = np.exp(logw - logw.max())
    return w / w.sum()

MASS3 = {"uniform": dirichlet_mass([1, 1, 1]),
         "one popular task (Dir 2,2,6)": dirichlet_mass([2, 2, 6]),
         "two popular tasks (Dir 5,5,1)": dirichlet_mass([5, 5, 1])}

def step(a0, a1, TH, mass):
    m = np.log(TH @ a1) - np.log(TH @ a0)
    order = np.argsort(-m); ms = m[order]; cum = np.cumsum(mass[order])
    prof = np.where(ms > 1e-12, ms * cum, -1.0); k = int(np.argmax(prof))
    if prof[k] <= 0: p, sel = 0.0, np.zeros(len(m), bool)
    else: p, sel = float(ms[k]), m >= ms[k]
    return (mass * ~sel) @ TH, (mass * sel) @ TH, p, float((mass * sel).sum())

def simulate(a0, a1, s, eta, TH, mass, Tend=2000.0, dt=0.05):
    a0 = np.array(a0, float); a1 = np.array(a1, float)
    for _ in range(int(Tend / dt)):
        U0, U1, p, sh = step(a0, a1, TH, mass)
        a0 = a0 + dt * U0 / np.linalg.norm(a0) ** eta
        a1 = a1 + dt * (U1 + s * U0) / np.linalg.norm(a1) ** eta
    U0, U1, p, sh = step(a0, a1, TH, mass)
    V1 = U1 + s * U0; V0 = U0
    with np.errstate(divide="ignore", invalid="ignore"):
        pred = (V1 / V0) * (np.linalg.norm(V0) / np.linalg.norm(V1)) ** (eta / (1 + eta))
    return dict(share=sh, p=p, ratio=a1 / a0, pred=pred, U0=U0, U1=U1)

def fmt(v): return "(" + ",".join(f"{x:.2f}" for x in v) + ")"
def cls(r):
    if r["share"] > 0.999: return "closed all"
    if r["share"] < 0.001: return "open all"
    return "interior"

if __name__ == "__main__":
    print("=== two tasks, beta(2,5), closed leads x2 ===")
    for s in [0.0, 1.0]:
        for eta in [0.0, 0.5, 1.0, 2.0]:
            r = simulate([.5, .5], [1, 1], s, eta, TH2, MASS2["beta(2,5)"])
            print(f"s={s} eta={eta}: {cls(r):9s} share={r['share']:.3f} e^p={np.exp(r['p']):.1f} ratio={fmt(r['ratio'])} pred={fmt(r['pred'])}")
    print("\n=== two tasks, uniform, s=0.5 ===")
    for eta in [0.0, 1.0, 2.0]:
        for name, a1 in [("leads x2", [1, 1]), ("lopsided", [1.5, .6])]:
            r = simulate([.5, .5], a1, 0.5, eta, TH2, MASS2["uniform"])
            print(f"eta={eta} {name:8s}: {cls(r):9s} share={r['share']:.3f} ratio={fmt(r['ratio'])}")
    rng = np.random.default_rng(0)
    rand = [(rng.uniform(.1, 1, 3), rng.uniform(.1, 1, 3)) for _ in range(4)]
    for nuname, mass in MASS3.items():
        print(f"\n=== three tasks, {nuname} ===")
        for s in [0.0, 1.0]:
            for eta in [0.0, 1.0]:
                r = simulate([.5, .5, .5], [1, 1, 1], s, eta, TH3, mass, Tend=1200.0)
                rr = [simulate(a0, a1, s, eta, TH3, mass, Tend=1200.0) for a0, a1 in rand]
                print(f"s={s} eta={eta}: leads x2 -> {cls(r):9s} share={r['share']:.3f} e^p={np.exp(r['p']):.1f} ratio={fmt(r['ratio'])} | random: "
                      + ", ".join(f"{cls(x)} {x['share']:.2f}" for x in rr))
                sys.stdout.flush()
