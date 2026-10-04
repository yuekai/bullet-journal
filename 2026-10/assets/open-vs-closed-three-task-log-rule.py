"""Three-task open-vs-closed LLM model: log per-unit value, stock learning.

Users: unit usage, task mix theta on the 2-simplex, density nu (Dirichlet).
Models: open (0) at price 0, one closed firm (1) with per-unit price p.
Per-unit utility: log(theta . a_j) - p_j. No outside option.
Closed firm prices myopically: max_p p * nu({ m >= p }), m = log(theta.a1) - log(theta.a0).
Learning (stocks): da0 = U0 ; da1 = U1 + s*U0.
Closed territory is the half-space { theta . (a1 - e^p a0) >= 0 } cut from the simplex.
"""
import numpy as np, sys
from math import gamma as G

H = 60  # grid resolution: theta_k = i_k / H
pts = [(i, j, H - i - j) for i in range(H + 1) for j in range(H + 1 - i)]
TH = np.array(pts, float) / H               # (n, 3)
N = len(TH)

def dirichlet_density(alpha):
    alpha = np.array(alpha, float)
    th = np.clip(TH, 1e-9, None)
    logw = ((alpha - 1) * np.log(th)).sum(1)
    w = np.exp(logw - logw.max())
    return w / w.sum()                        # unit total mass on the grid

NU = {
    "uniform": dirichlet_density([1, 1, 1]),
    "one popular task (Dir 2,2,6)": dirichlet_density([2, 2, 6]),
    "two popular tasks (Dir 5,5,1)": dirichlet_density([5, 5, 1]),
}

def step_info(a0, a1, mass):
    m = np.log(TH @ a1) - np.log(TH @ a0)
    order = np.argsort(-m); ms = m[order]; cum = np.cumsum(mass[order])
    prof = np.where(ms > 1e-12, ms * cum, -1.0)
    k = int(np.argmax(prof))
    if prof[k] <= 0:
        p, sel = 0.0, np.zeros(N, bool)
    else:
        p, sel = float(ms[k]), m >= ms[k]
    U1 = (mass * sel) @ TH; U0 = (mass * ~sel) @ TH
    return U0, U1, p, float((mass * sel).sum()), sel

def simulate(a0, a1, s, mass, Tend=400.0, dt=0.05):
    a0 = np.array(a0, float); a1 = np.array(a1, float)
    for _ in range(int(Tend / dt)):
        U0, U1, p, sh, sel = step_info(a0, a1, mass)
        a0 = a0 + dt * U0; a1 = a1 + dt * (U1 + s * U0)
    U0, U1, p, sh, sel = step_info(a0, a1, mass)
    ratio = a1 / a0
    open_vertices = [k for k in range(3) if ratio[k] < np.exp(p)] if 0 < sh < 1 else []
    open_mean = ((mass * ~sel) @ TH) / max((mass * ~sel).sum(), 1e-12) if sh < 1 else None
    return dict(a0=a0, a1=a1, p=p, share=sh, U0=U0, U1=U1, ratio=ratio,
                open_vertices=open_vertices, open_mean=open_mean,
                pred_ratio=(U1 + s * U0) / np.where(U0 > 0, U0, np.nan))

def classify(r):
    if r["share"] > 0.999: return "closed takes all"
    if r["share"] < 0.001: return "open takes all"
    return "interior"

def fmt(v): return "(" + ",".join(f"{x:.2f}" for x in v) + ")"

if __name__ == "__main__":
    rng = np.random.default_rng(0)
    rand_starts = [(rng.uniform(0.1, 1, 3), rng.uniform(0.1, 1, 3)) for _ in range(16)]
    struct = {
        "closed leads x1.05": ([.5, .5, .5], [.525, .525, .525]),
        "closed leads x2": ([.5, .5, .5], [1, 1, 1]),
        "closed leads, strong on task 3": ([.5, .5, .5], [.6, .6, 1.5]),
        "closed leads on tasks 2,3 only": ([.5, .5, .5], [.45, .7, .7]),
        "open leads x1.05": ([.525, .525, .525], [.5, .5, .5]),
        "open leads on task 1 only": ([.7, .5, .5], [.5, .6, .6]),
    }
    print(f"grid points: {N}")
    for nuname, mass in NU.items():
        print(f"\n=== nu = {nuname}; population mean theta = {fmt(mass @ TH)} ===")
        for s in [0.0, 0.5, 1.0]:
            out = {}
            for a0, a1 in rand_starts:
                r = simulate(a0, a1, s, mass); out.setdefault(classify(r), []).append(r)
            print(f"s={s}: random starts -> " + ", ".join(f"{k}: {len(v)}/16" for k, v in out.items()))
            if "interior" in out:
                v = out["interior"]
                print(f"    interior closed shares: {sorted(round(r['share'], 3) for r in v)}")
                print(f"    open-held vertices per run: {[r['open_vertices'] for r in v]}")
            for name, (a0, a1) in struct.items():
                r = simulate(a0, a1, s, mass)
                tail = f" open vertices={r['open_vertices']} open mean theta={fmt(r['open_mean'])}" if classify(r) == "interior" else ""
                print(f"    {name:30s} -> {classify(r):16s} share={r['share']:.3f} p={r['p']:.3f} e^p={np.exp(r['p']):.1f} ratio={fmt(r['ratio'])}{tail}")
            sys.stdout.flush()
    print("\n=== long-horizon checks (T=2000), closed leads x2 ===")
    for nuname in ["one popular task (Dir 2,2,6)", "two popular tasks (Dir 5,5,1)"]:
        for s in [0.0, 1.0]:
            r = simulate([.5, .5, .5], [1, 1, 1], s, NU[nuname], Tend=2000.0)
            print(f"{nuname}, s={s}: {classify(r)} share={r['share']:.3f} p={r['p']:.3f} ratio={fmt(r['ratio'])} pred={fmt(r['pred_ratio'])} open vertices={r['open_vertices']}")
    print("\n=== uniform, s=0.5, interior-looking starts at T=2000 ===")
    cnt = 0
    for a0, a1 in rand_starts:
        r = simulate(a0, a1, 0.5, NU["uniform"])
        if classify(r) == "interior" and cnt < 3:
            cnt += 1
            r2 = simulate(a0, a1, 0.5, NU["uniform"], Tend=2000.0)
            print(f"T=400 share={r['share']:.3f} -> T=2000 share={r2['share']:.3f} ({classify(r2)})")
