---
title: Open vs closed LLM ecosystem model
description: Model of competition between closed LLMs and one free open-data LLM; users are task-mix profiles on the simplex, models are training stocks mapped to abilities by a per-task power law, per-unit prices, log per-unit value; the open developer publishes its data with a one-period delay, every developer chooses what to train on against a compute cost; settled setup, long-run structure, results under the superseded learning rule, alternatives explored, related work, and open issues
date: 2026-10-02
---

A model of the open-weight LLM ecosystem in which the agents are organizations rather than individual programmers. Users and models both live in a task space. The Oct 3 version had models learn mechanically from usage, with a spillover parameter carrying open-model usage to closed firms; that version is recorded in §4 and its results in §3. The Oct 7 revision replaces the learning rule with a firm side: a model is its training stock, ability is a power law of the stock, the open developer publishes its data with a one-period delay, and every developer chooses what to train on against a compute cost. This note records the setup as it now stands, the questions a solved model should answer, what the old instances showed, the alternatives that were explored and dropped, how the model compares to existing work, and what is still open.

## 1. Setup

### 1.1 Primitives

- **Tasks.** There are d task types, such as coding, writing and math.
- **Users.** A continuum of users, each with a task mix θ in the unit simplex Δ^{d−1} and unit usage. Users are distributed by a density ν on the simplex with unit mass. Heavy users are represented by more density at their task mix, not by a longer vector. This is valid because demand, revenue and training data are all linear in usage, and it commits the model to per-unit pricing: a fixed fee would break the linearity. Ū = ∫ θ dν is the population's usage by task, a fixed vector.
- **Models.** One open model, indexed 0, and n closed models, indexed 1..n. A model is its training stock Sⱼ ∈ ℝᵈ₊, the unique tokens of each task it has been trained on so far. Its ability profile aⱼ ∈ ℝᵈ₊ is computed from the stock by the map in §1.3. Closed model j charges a per-unit price pⱼ ≥ 0; the open model is free, p₀ = 0.
- **Choice.** A user with task mix θ gets per-unit utility uⱼ(θ) = log(θ·aⱼ) − pⱼ from model j and picks the argmax. There is no outside option: every user uses some model. Utility differences are log ratios, so the model is scale-free: scaling every ability by one factor changes nothing. Price is in log units, so eᵖ is the quality ratio at which a user is indifferent between paying p and using the free model.

### 1.2 Territories and usage

Let Tⱼ ⊂ Δ^{d−1} be the set of task mixes choosing model j. Competition is purely horizontal: each model owns a region of the simplex. The usage of model j is the vector Uⱼ = ∫_{Tⱼ} θ dν(θ) ∈ ℝᵈ₊, whose component Uⱼₖ is how much task-k work flows through model j, and its mass is Nⱼ = ν(Tⱼ). Write mⱼₗ(θ) = log(θ·aⱼ) − log(θ·aₗ) for model j's quality edge over model l in direction θ. A user buys from closed firm j when j's price is below j's edge over the free model and below j's edge over every rival plus that rival's price:

```
θ ∈ Tⱼ   iff   pⱼ ≤ min( mⱼ₀(θ),  min_{k≠j, k≥1} [ mⱼₖ(θ) + pₖ ] )
```

Given rivals' prices, j's demand is the mass of users whose threshold exceeds pⱼ, a one-dimensional problem solved by sorting directions by threshold and scanning.

### 1.3 Data and abilities

**Ability map.** With γ = 1 and T a d×d matrix with ones on the diagonal, default T = I,

```
aⱼₖ = γ · ( (T·Sⱼ)ₖ )^κ ,        0 < κ < 1
```

- The form is the quanta picture of scaling (Michaud et al., §5.4). A task consists of discrete skills used with Zipf frequencies pₙ ∝ n^{−(α+1)}; a skill is learned once the training set holds about τ examples that use it; so with Sₖ task-k tokens the model learns the skills with pₙ·Sₖ ≥ τ, whose count grows like Sₖ^{1/(α+1)}. Ability is the count of learned task-k skills, so κ = 1/(1 + α). The same model gives the loss exponent in data as α_D = α/(α+1), so κ = 1 − α_D, which is how κ is to be read off a fitted scaling law.
- Reading ability as a skill count makes a user's per-unit value linear in the number of relevant skills, so rare skills are worth more per use in proportion to their rarity. This is an assumption, not a derivation, and it is what keeps utility scale-free: aⱼ(λS) = λ^κ·aⱼ(S), so scaling every stock leaves every territory unchanged. The bounded reading, fraction of skill mass learned, is the success-rate ceiling in §4.
- Tₖₘ is the fraction of task-m tokens that exercise task-k skills. Transfer across distributions is documented (Hernandez et al., Ye et al., §5.4); T = I is the default because nothing computed yet needs it.
- Per task, ability is concave in the stock, so a token raises a smaller stock by a larger proportion. This is the model's catch-up force and it is per task.

**Data pools.** With periods t = 0, 1, 2, … (§1.5),

```
Pᵗ  = P⁰ + Σ_{τ<t} U₀^τ          open pool at the start of period t
Bᵗ  = Pᵗ⁻¹ ,   B⁰ = P⁰            public book at the start of period t
Qⱼᵗ = Eⱼ⁰ + Σ_{τ<t} Uⱼ^τ         private pool of closed firm j
```

- The open developer publishes its data: its initial corpus P⁰ and every log it collects. The open pool is all of it. The public book is what closed firms may train on, the open pool as it stood one period earlier. The initial corpus is public from the start. There is no other public data: the open developer's corpus is the public corpus.
- A closed firm's private pool is its private endowment Eⱼ⁰ plus its own logs. Nobody else sees it, including other closed firms.
- Access bounds: S₀ᵗ ≤ Pᵗ and Sⱼᵗ ≤ Bᵗ + Qⱼᵗ. A developer's stock is anything between what it has already trained on and what it has access to, since training costs compute (§1.4).
- Tokens are unique tokens. Re-training on data already in the stock adds nothing, which Muennighoff et al. (§5.4) support for more than a few epochs.
- A model with no users collects no logs. The open model with no users stops growing. A closed firm with no users still has access to the book one period late, so if it trains on it its stock is Pᵗ⁻¹ + Qⱼ against the open model's Pᵗ: it leads on task k exactly when its private pool there exceeds one period of open logs, Qⱼₖ > U₀ₖ, and its margin there shrinks like κ·(Qⱼₖ − U₀ₖ)/Pₖ as the pool grows. Access is not training: under costly compute a firm with no revenue to defend may leave the book unused.

### 1.4 Training cost

Adding mⱼ = Sⱼᵗ⁺¹ − Sⱼᵗ tokens in period t costs

```
Cᵗ(mⱼ ; Sⱼ) = cₜ · |aⱼ(Sⱼ)|₁ · |mⱼ|₁ ,        cₜ = c₀ · e^{−g·t}
```

- Compute per token is proportional to the size of the model being trained (Hoffmann et al., §5.4), and model size is proportional to total ability because each learned skill occupies a fixed number of parameters (Michaud et al.). So each developer faces one compute price per token, the same on every task, which rises as its model improves overall. This is where the overall-quality effect of the Oct 6 rule now lives, with the ℓ¹ norm and exponent one; the per-task diminishing returns live in κ.
- Public tokens cost the same compute as private ones. A closed firm pays to train on the book exactly as on its own logs and may ration it.
- Units: a period's total usage is one and γ = 1, so a stock of one period's usage on a task gives ability one on it. c₀ is then the cost of training a unit-ability model on one period's worth of tokens, in revenue units; revenue per period is of order one to three. g ≥ 0 is the rate at which compute gets cheaper; g = 0 is constant compute.
- Variant, not baseline: a full retrain per generation costs cₜ·|aⱼ(Sⱼ + mⱼ)|₁·|Sⱼ + mⱼ|₁, a fixed cost per release that grows with the stock, so releases are lumpy.

### 1.5 Timing, objectives and equilibrium

A period is a model generation. Within period t:

1. Every stock, and so every ability, is public. Closed firms set prices simultaneously; the open model is free.
2. Users sort. Masses Nⱼᵗ and usage vectors Uⱼᵗ are realized.
3. Pools update: Pᵗ⁺¹ = Pᵗ + U₀ᵗ, Qⱼᵗ⁺¹ = Qⱼᵗ + Uⱼᵗ, Bᵗ⁺¹ = Pᵗ. The open developer's new logs enter its pool now and reach the book one period later.
4. Developers choose next stocks simultaneously, with usage known: S₀ᵗ ≤ S₀ᵗ⁺¹ ≤ Pᵗ⁺¹ and Sⱼᵗ ≤ Sⱼᵗ⁺¹ ≤ Pᵗ + Qⱼᵗ⁺¹. The open developer may use its logs through period t; a closed firm may use its own logs through t and open logs through t − 1.
5. Closed firm j receives pⱼᵗ·Nⱼᵗ − Cᵗ(mⱼᵗ; Sⱼᵗ). The open developer is credited with N₀ᵗ.

**Closed firm j** maximizes Σₜ βᵗ·[pⱼᵗ·Nⱼᵗ − Cᵗ(mⱼᵗ; Sⱼᵗ)] over its prices and training, given the others' strategies. Lowering the price keeps users whose logs would otherwise feed the open model now and, through the book, every closed rival one period later; it also gets their logs into the firm's own stock a period sooner. Training on a task pays when the future revenue from the added ability exceeds the compute price of the tokens, so for every task the firm trains on all its tokens, some, or none.

**The open developer** maximizes Σₜ β₀ᵗ·N₀ᵗ subject to Cᵗ(m₀ᵗ; S₀ᵗ) ≤ B each period: it spends a fixed per-period budget from its sponsor on the tokens that add most to its future share. It sets no price and never withholds data.

**Nobody trains without looking ahead.** Training costs now and pays next period, so a developer maximizing one period's payoff never trains; there is no myopic baseline. The computational device is a lookahead of H periods: each developer chooses this period's price and training to maximize the discounted sum of this period's and the next H periods' payoffs, with later periods' choices taken from the same rule. H = 1 sees one channel of the price: a ceded user feeds the open model, which trains on her logs and is stronger next period. H = 2 also sees the two delayed channels, her logs reaching the book and the rivals, and the firm's own one-period loss on them. H = 2 is the smallest horizon containing every channel and is the baseline; longer horizons are a robustness check, and since stocks grow while a period's usage is bounded, ratios move more slowly each period and the horizon should matter less over time.

**Equilibrium.** A strategy maps the state (S₀, S₁..Sₙ, P, L = U₀ lagged, Q₁..Qₙ) to a price and a training choice, and each developer's strategy is a best response to the others'. Within a period there are two stages: the price game, then the training game with usage known. Each is solved by iterating best responses, each best response being a sort-and-scan over directions for the price and a per-task comparison of token value with the compute price for training. Demand in own price is step-like and non-concave, so a pure fixed point is not guaranteed; a cycle is reported, not hidden.

### 1.6 Questions the solved model should answer

- **Do closed firms cede the thin tail?** Which directions, and how the ceded share depends on the openness regime and the shape of ν.
- **Does the open model survive?** Survival is U₀ > 0 in the long run. It now has three inputs: density geometry, the sponsor's budget B, and whether any closed firm wants it alive.
- **Which closed firms want open data?** The public book erodes every closed firm's lead over the open model, but it also compresses gaps among closed firms, so a lagging closed firm gains on the leader as the pool grows. Who prices to starve the pool and who tolerates it.
- **Where do stocks and abilities diverge?** Which tasks each developer exhausts, rations and discards; how much of the book each closed firm uses; whether the open developer is weaker than its own pool.
- **Prices across regimes.** Open data versus open weights with private logs versus no open model (§3.6).
- **Welfare.** Per-unit consumer surplus ∫ maxⱼ uⱼ(θ) dν, producer surplus net of compute, and the public data flow, which a closed monopoly that freezes the open model also stops.
- **Dynamic pricing.** How much a forward-looking firm cedes relative to the one-period-profit price, and which of the three channels drives it.

## 2. Long-run structure

Derived, not yet checked numerically.

**Growth.** Usage per period is bounded by the population mass, so every stock grows at most linearly in t and every ability at most like t^κ. Stocks of a developer that keeps its users grow linearly; the ratio of any two stocks on a task converges, and a period's logs become negligible against the stocks.

**Stationary ratios when data saturates.** If every developer trains on everything it can access, then S₀ᵗ = Pᵗ, Sⱼᵗ = Pᵗ⁻¹ + Qⱼᵗ, the delay washes out, and with T = I, componentwise,

```
aⱼ / a₀  →  ( 1 + Vⱼ / V₀ )^κ ,       Vⱼ = long-run usage of model j
```

The closed firm's data is its own usage plus the open model's, which together is everything, so its lead is set by how much of the population it serves relative to the open model on each task, compressed by κ. There is no overall-norm term. The Oct 6 rule's ratio formula is in §4.

**Whether data saturates depends on compute, and differently for the two kinds of developer.** A closed firm's compute price per token is cₜ·|aⱼ|₁, which grows with its own ability, while the value of a token falls like the marginal ability S^{κ−1} times a bounded revenue effect. At g = 0 a closed firm therefore stops training on a task once the value falls below the price; its ability and its compute price are then frozen, and whether it resumes depends on how the open model's growth moves its revenue effect. The open developer never stops under a budget: it buys B/(cₜ·|a₀|₁) tokens per period, positive at any finite ability, so at g = 0 its stock keeps growing while closed stocks stall. Whether the industry freezes, or the open model slowly overtakes stalled closed firms, is a parameter question for §3.6. Closed development continues forever only if cₜ falls at least like 1/t, and the saturated regime above is the limit of the g > 0 case.

**Asymptotic myopia.** Because ratios move like 1/t, a developer discounting in calendar time cares less each period about the effect of its choices on ratios, and forward-looking pricing converges to one-period pricing. Forward-looking effects are transients of the initial condition, which is why the lookahead horizon should matter less over time.

**Corners.**
- **Open frozen.** If closed firms take every direction the open pool stops, the book stops, and every closed firm's lead grows with its own logs alone. The price grows without bound, as in the no-outside-option Oct 3 version, and public data stops with it.
- **Open takes all.** A closed firm with no users adds nothing to its private pool, so its stock on task k is at most Pᵗ⁻¹ + Qⱼₖ against the open model's Pᵗ. Where Qⱼₖ exceeds one period of open logs it still leads, but the margin, the price it can charge and its revenue all vanish like 1/Pₖ as the open pool grows. The corner is a fade to zero revenue, not a trap at parity; and a firm whose private endowment exceeds one period of open logs leads from the start even with no users.

**Initial lead.** All developers start from P⁰. A closed firm leads on task k at t = 0 by κ·log(1 + Eⱼₖ⁰/Pₖ⁰): the lead is private data relative to the public corpus. With Eⱼ⁰ = 0 the closed firm's ability equals the open model's and it has no users at any positive price. So "who starts ahead" in §3 becomes "who brings private data," and the ratio of P⁰ to a period's usage sets how fast anything moves.

## 3. Simulation results under the superseded rule

All statements in this section are *(computed)* under the Oct 3 to Oct 6 learning rule, ȧ₀ = γ·U₀/‖a₀‖^η and ȧⱼ = γ·(Uⱼ + s·U₀)/‖aⱼ‖^η, with one closed firm, log value, myopic pricing, γ = 1, the Euler schemes below, and 16 fixed random starts plus structured ones. The rule is recorded in §4. None of these results is reproduced by any parameter setting of the §1 model: there the firm chooses its direction of learning, the catch-up force is per task through κ rather than overall through η, and a myopic firm never trains. They are kept as the baseline the §3.6 instance is compared against. §3.1 to §3.3 use the linear rule, η = 0; §3.4 shows what η = 1 changed. §3.1 and §3.2 are two tasks, §3.3 is three.

**Two tasks:** θ = (t, 1 − t) with t ∈ [0, 1], one closed firm. The margin m(t) is a single curve, the firm's static problem is one-dimensional, and the myopic price is found by sorting directions by margin and maximizing margin times the user mass at or above it. Simulation: forward Euler on the ability stocks with γ = 1, step 0.05, horizon 400 to 2000, 801 directions with trapezoid weights, price re-optimized every step. Script: [open-vs-closed-two-task-log-rule.py](assets/open-vs-closed-two-task-log-rule.py).

**Three tasks:** θ on the 2-simplex, one closed firm. Same scheme on a triangular grid of 1891 directions with step 1/60, with ν a Dirichlet density evaluated on the grid and normalized. Script: [open-vs-closed-three-task-log-rule.py](assets/open-vs-closed-three-task-log-rule.py).

Both scripts above use η = 0. The comparison across η on both grids is [open-vs-closed-diminishing-returns.py](assets/open-vs-closed-diminishing-returns.py).

### 3.1 Users spread uniformly over task mixes

No stable interior. Every start ends in a corner, and which corner depends on who leads at the start.
- A closed firm leading by a roughly uniform margin, even five percent, takes every direction. The open model freezes and the closed price grows without bound, about 6.0 log units at horizon 400.
- A closed firm trailing anywhere that matters loses every direction. A firm leading overall but lopsided toward one task loses at s ≤ 0.5 and wins at s ≥ 0.9: at low spillover it prices for its strong task, cedes the other, and the open model grows there until it overtakes; at high spillover it absorbs enough of the open model's learning on the ceded task to keep its lead there.
- Intermediate shares appear at horizon 400 for s between 0.7 and 0.95, but they are slow transients: two of three rechecked at horizon 2000 had collapsed to a closed monopoly and the third was still drifting toward it.
- Higher s enlarges the closed firm's basin: three of sixteen random starts at s = 0 end in closed monopoly, eleven at s = 1.

The uniform case is degenerate because it has no thin tail. Under the earlier depreciation rule the same case had a saddle interior and the same two corners.

### 3.2 Users concentrated on one task

Density Beta(2,5) in the task-1 weight, so most users are task-2 heavy and the task-1 end of the simplex is a thin tail. From every structured start where the closed firm leads, at every s, the long run is a stable interior, reached by horizon 300 and unchanged at 2000. The closed firm specializes toward the mass and cedes the tail. The exception is s = 1, where four of sixteen random starts ended with the open model frozen out: with full spillover the monopoly corner is reachable even with a thin tail.

| s | closed price | closed usage share | a₁/a₀ by task |
|---|---|---|---|
| 0.0 | 2.81 | 0.949 | (7.6, 40) |
| 0.5 | 2.88 | 0.952 | (8.6, 43) |
| 1.0 | 2.96 | 0.955 | (9.5, 47) |

Readings.
- **Where the open model lives.** It holds the task-1-heavy tail, about five percent of usage, where neither model is good. The closed model is eight to ten times better there in ability-ratio terms, but its price, around e^2.9 ≈ 18 in quality-ratio terms, exceeds its margin in those directions, so tail users take the free model. Learning follows users, so the directions the closed firm does not price for are also the directions it is relatively weak in. The two coincide endogenously.
- **Price rises with s, and so does coverage.** The earlier conjecture was that closed firms cede more as spillover rises, to free-ride on public learning. The computation shows price and closed share both rising with s. Spillover makes the closed firm stronger in every direction, so it charges more and covers more. The open model shrinks slightly but survives at s = 1.
- **Who starts ahead decides.** A closed firm starting behind by five percent loses every direction and never recovers. One behind on task 2 only also loses for s < 1, but at s = 1 it absorbs the open model's task-2 learning in full, overtakes, and freezes the open model out. The open-takes-all corner is an artifact of the model having no non-usage input: a firm that falls behind has no way back without R&D funded by profit.

The earlier depreciation run gave the same qualitative picture for this density, with a slightly lower closed share of 0.87 to 0.90, because under depreciation the open model's level was tied to its current usage flow rather than its accumulated stock. Script for that run: [open-vs-closed-two-task-depreciation-rule.py](assets/open-vs-closed-two-task-depreciation-rule.py).

### 3.3 Three tasks

Three user densities: uniform; one popular task, Dirichlet(2,2,6), with mean task mix (0.20, 0.20, 0.60); two popular tasks, Dirichlet(5,5,1), with mean (0.46, 0.46, 0.08). Spillover s ∈ {0, 0.5, 1}. Long-horizon checks at 2000 confirmed every steady state reported here; two near-corner runs under Dirichlet(2,2,6) at s = 1 were transients and are counted as corners.

| density | s | closed share | eᵖ | open-held vertices | a₁/a₀ by task |
|---|---|---|---|---|---|
| uniform | 0 | corners only | | | |
| uniform | 0.5 | 0.38 to 0.75, several stable interiors | 2.0 | one vertex | (0.96, 3.7, 3.7) in one of them |
| uniform | 1 | 0.85 to 0.93 | 4 to 6 | one vertex | (3.0, 18, 18) in one of them |
| one popular task | 0, 0.5, 1 | 0.971 | 28 to 30 | the two unpopular tasks | (16, 16, 65) |
| two popular tasks | 0, 0.5, 1 | 0.977 | 36 to 39 | the unpopular task | (51, 51, 8) |

Readings.
- **Uniform density has interiors in three tasks where it had none in two.** At s = 0 every random start still ends in a corner, and a closed firm leading uniformly takes all at every s. But at s = 0.5 six of sixteen random starts, and at s = 1 fifteen of sixteen, reach a stable interior in which the open model holds one corner of the simplex. Dimension and spillover together produce the interior, not dimension alone.
- **Two survival modes.** In the uniform s = 0.5 interiors the open model leads outright on its task, ratio 0.96. In every other interior it trails on every task, by factors of 3 to 17 at the vertex it holds, and survives only because that corner is too thin to price for.
- **The ceded share is pinned by density geometry.** Under both concentrated densities the closed share is the same to three decimals across s and across starting leads, 0.971 and 0.977, while the price rises with s. The open model holds exactly the corners of the unpopular tasks.
- **Several stable interiors.** The uniform s = 0.5 runs reach closed shares from 0.38 to 0.75 while four of six hold the same vertex, so steady states are not unique even given the held vertex. History selects among them.
- **Lopsided leaders.** A closed firm leading strongly on the popular task loses every direction at s = 0 under uniform density and takes all at s ≥ 0.5, the same pattern as in two tasks.
- **Ratio formula.** The predicted stationary ratios of the Oct 6 rule (§4) match the simulation to about two percent at horizon 2000, with the gap due to initial conditions.

### 3.4 Diminishing returns

Same instances with the overall-quality penalty, closed firm starting ahead by a factor of two, horizon 2000 in two tasks and 1200 in three.

Two tasks, users concentrated on task 2:

| η | s | closed share | eᵖ | a₁/a₀ by task |
|---|---|---|---|---|
| 0 | 0 | 0.949 | 16.6 | (7.6, 40) |
| 0.5 | 0 | 0.902 | 4.4 | (1.9, 8.4) |
| 1 | 0 | 0.851 | 2.5 | (1.0, 4.2) |
| 2 | 0 | 0.752 | 1.6 | (0.7, 2.3) |
| 0 | 1 | 0.955 | 19.2 | (9.5, 47) |
| 1 | 1 | 0.883 | 2.9 | (1.4, 5.1) |
| 2 | 1 | 0.821 | 1.9 | (0.9, 2.8) |

The η = 2 rows are still drifting at horizon 10000 and are not converged.

Readings at η = 1.
- **The open territory grows.** Three-task concentrated-density shares fall from 0.971 to 0.926 at s = 0 and 0.940 at s = 1, and from 0.977 to 0.954. The uniform full-spillover interiors fall from 0.87 to 0.91 down to 0.57 to 0.60. Which vertices the open model holds does not change.
- **Prices fall much more than shares.** Quality ratios at the price point drop from near 30 to near 4 in three tasks and from 17 to 2.5 in two. Leads compress toward one; η is a commoditization dial.
- **An overtaken closed firm keeps a niche.** The lopsided leader under uniform two-task density, overtaken outright at η = 0, holds 3 percent of usage at η = 1 and 19 percent at η = 2.
- **Corners and basins are otherwise unchanged.** A uniformly leading closed firm still takes all; a closed firm starting behind by a uniform factor still loses all.

### 3.5 What the old results say

The thin-tail result is geometric. The open model survives at a corner of the simplex whose user mass is worth less to the closed firm than the price gain from excluding it. Concentrated densities create such corners at the unpopular tasks; uniform density creates them by geometry alone once d ≥ 3, since the mass within distance ε of a vertex scales like ε^{d−1}. Two tasks have no thin corners under uniform density, which is why that case tipped to monopoly. The result held from any start where the closed firm led, except that under full spillover the monopoly corner was also reachable from some starts. Diminishing returns in overall quality enlarged the open territory without changing which corners it held, because they lowered every margin by the same amount and the thin corners were the first to fall below the price.

Two things the old model could not produce, and what the §1 model does about them. A closed firm that fell behind everywhere never recovered, because it had no non-usage input; now a closed firm with no users still has the public book, keeps whatever lead its private pool gives it over one period of open logs, and fades toward zero revenue rather than vanishing. And the closed firm's lead was exogenous, set by the starting point; now it is private data relative to the public corpus at the start and development spending after that.

### 3.6 Instance to compute under the current model

- **Shape.** Two tasks, θ = (t, 1 − t); two closed firms; the uniform and Beta(2,5) densities of §3.1 and §3.2; T = I; κ = 0.7 as a working value pending §6; lookahead H = 2, with H = 1 and H = 3 as checks; β = β₀.
- **Stocks.** Period usage normalized to one. Common corpus P⁰; private endowments E₁⁰, E₂⁰, in two cases: the two closed firms specialize on different tasks, and one simply has more private data.
- **Compute.** Sweep c₀ against revenue of order one to three, and g ∈ {0, small}. Sweep the open developer's budget B, including the asymmetric regime of deep-pocketed closed firms against a budgeted open developer.
- **Regimes.** Open data, as in §1. Open weights with private logs: the book stays at P⁰ forever and the open developer trains on its own logs alone. No open model: the two closed firms from P⁰ plus their endowments.
- **Report.** Prices, territories and ability ratios as before; which tasks each developer exhausts, rations and discards, period by period; how much of the book each closed firm uses; whether the open developer is weaker than its own pool; and any price-stage or training-stage cycle.
- **Checks.** With one closed firm, g > 0 and the delay removed, the long-run ratio should approach §2's formula. With Eⱼ⁰ = 0 a closed firm should get no users at any positive price. Compare every run against the §3.2 baseline, keeping in mind that no parameter setting reproduces it.

## 4. Alternatives explored

Each line says what the alternative was and why it was dropped or deferred.

**User and demand side**
- **Usage vectors x = r·θ with intensity r and a fixed per-user price.** Gave vertical sorting by intensity within each task mix, in the Mussa–Rosen sense, and convex polyhedral demand regions. Dropped because, with intensity factored out of choice under per-unit pricing, heavy users are just density, and the state collapses to a measure on the simplex.
- **Outside option with utility zero.** Needed under subscription pricing so that intensity mattered. Dropped with the move to log utility, which is scale-free only without it. Consequence: in the frozen-open corner the closed price is unbounded.
- **Concave transform of x·aⱼ.** Proposed to remove the ability bound. Rejected because it breaks intensity sorting: for a bounded transform the willingness to pay for quality is hump-shaped in intensity, and for log it is constant in intensity, so heavy users stop paying for quality.
- **Concavity per unit of usage, r·g(θ·aⱼ) − pⱼ.** The fix for the previous item. Subsumed by the simplex normalization with per-unit pricing.
- **Two-part tariff, r·(g(θ·aⱼ) − pⱼ) − Fⱼ.** Nests subscription and per-unit pricing. Deferred as the extension a monopolist facing heterogeneous intensity within a direction would choose.
- **Marginal inference cost c per unit, with p₀ = c.** Deferred. It would restore an outside option and break scale-freeness.

**Learning rules, all superseded by the firm side of §1.3 to §1.5**
- **Bounded abilities in [0, 1]ᵈ with logistic learning, ȧₖ = γUₖ(1 − aₖ).** The first fix for scale. Dropped because the bound was an assumption rather than a definition, and the long run saturates.
- **Success-rate ceiling with failure-driven learning.** Reads aⱼₖ as the probability of completing a task of type k, so the bound is a definition and failures Uⱼₖ(1 − aⱼₖ) are the training signal. Dropped because the long run is commoditization and the content is transient. Under the quanta reading this is ability as the fraction of skill mass learned, against the count used in §1.3.
- **Depreciation, ȧⱼ = γ(Uⱼ + sU₀) − δaⱼ.** Gave closed-form steady states with ability equal to usage flow. Dropped because it turns ability from a stock into a flow and erased losing models, which misstates the persistence of released weights. It is exactly a moving-frontier model with exogenous exponential escalation of task difficulty and learning proportional to difficulty.
- **Moving frontier.** Raw capability stocks measured against a difficulty index. Deferred. With a scalar index it coincides with log utility up to the outside option.
- **Linear learning with linear utility and no bound.** Homogeneous of degree one, analyzable as detrended balanced growth. Superseded by log utility, which gives stationarity in ratios directly.
- **Linear learning with log utility, η = 0, Oct 3 rule.** ȧⱼ = γ(Uⱼ + s·U₀). §3.1 to §3.3 are computed under it. Let leads grow in proportion to usage with no slowdown, so an overtaken closed firm vanished rather than holding a niche.
- **Overall-quality penalty, η = 1, Oct 6 rule.** ȧ₀ = γ·U₀/‖a₀‖^η, ȧⱼ = γ·(Uⱼ + s·U₀)/‖aⱼ‖^η, Euclidean norm. Stationary ratios aⱼ/a₀ → (Vⱼ/V₀)·(‖V₀‖/‖Vⱼ‖)^{η/(1+η)} with Vⱼ = Ūⱼ + s·Ū₀ and V₀ = Ū₀, which matched §3 within a few percent at η ≤ 1. The norm penalty was chosen over a per-task one because, under a mechanical rule, a per-task penalty compresses log-margins uniformly and leaves territories unchanged. Superseded: the scaling-law microfoundation gives per-task diminishing returns, under optimization the firm moves territories through its choice of direction anyway, and the overall-quality effect reappears in the compute cost of §1.4.
- **Per-task penalty, ȧⱼₖ ∝ Uⱼₖ/aⱼₖ^η.** Rejected on Oct 6 for the reason just given. Its integrated form is aₖ ∝ Sₖ^{1/(1+η)}, which is the §1.3 power law with η equal to the Zipf exponent α of skill frequencies. It was the right rule for the wrong reason.
- **Spillover rate s ∈ [0, 1].** The fraction of open-usage learning reaching closed firms through fine-tunes, datasets, distillation and recipes; a free parameter because the old model had no mechanism for the channel. Dropped: the channel is now explicit, closed firms train on the public book, and under the quanta reading a prompt is worth the same whichever model answered it, so s = 1 by construction. What s interpolated between are the openness regimes of §3.6, which are discrete. If partial release is ever wanted it is a choice of the open developer, not an absorption rate of closed firms.
- **Brainstormed and not pursued.** Concave or multiplicative returns to usage; user count, coverage of task space, or failures as the usage measure; closed-to-open distillation κ(max cₘ − c₀); frontier catch-up for everyone.

**Firm side, Oct 7**
- **Forward-looking pricing with costly absorption, continuous time.** A Hamilton–Jacobi–Bellman problem over the ability state with price and an absorption rate s as controls and a convex cost of absorption, in the spirit of Cohen–Levinthal's absorptive capacity. Dropped when the data channel was made explicit, which removed s; and under constant learning rates the ratio dynamics slow, so a calendar-time discounter becomes myopic, which the discrete model inherits as asymptotic myopia (§2).
- **Development cost on any change, ‖a′ − a‖.** Rejected: it charges for making a model worse, which a firm never does since it can keep shipping the old one, and it makes the cost of reaching an ability independent of the data the firm holds.
- **Potential-function cost, f(a′) − f(a).** Rejected for a worse reason than refunding decreases: movement along a level set of f is free, so a firm could shift ability from unvalued tasks to valued ones at no cost; and it is path-independent, so again data plays no role.
- **Quadratic cost of improvement scaled by data, ‖a‖^η·Σₖ Δₖ²/(2γDₖ).** The inverse of a constant-returns production function in data and compute. Its first-order condition gave improvement proportional to data times shadow value, which nested the old rule as the case of constant shadow values. Superseded by the stock view: ability as a function of cumulative training data makes the stock the state and leaves the cost to compute alone.
- **Public data endowments, a per-period flow D̄ or an initial stock S̄.** Added to break the no-users trap. Replaced by the open pool: the public data is the open developer's data, so the public corpus is its initial corpus and the public flow is its logs.
- **Cheap-compute limit.** Every developer trains on everything it can access, the training choice disappears, and the model reduces to forward-looking pricing over the stock rule. Not pursued, by decision on Oct 7: compute costs are part of what the model is about.
- **Static pricing with intensity vectors** reduced to monopoly pricing over the scalar willingness to pay x·(a₁ − a₀), with the envelope result that the firm values ability where marginal users are while learning follows inframarginal heavy users. Under the current model the same tension is in the training rule: data comes from the users a firm has, value from the directions it contests.

## 5. Related work

### 5.1 LLM-era economic models

- **Jamison and Yu (2026), [Competing for the Future of AI](https://bear.warrington.ufl.edu/centers/purc/docs/papers/2605-Economic-Incentives-of-Open-Source-Foundation-Models.pdf).** A two-stage structural model estimated on Hugging Face data: model owners choose a degree of openness, downstream developers choose which model to adopt. Short-run returns cover under half of openness costs; knowledge spillovers from downstream developers, which raise next-generation quality, rationalize the rest. *Comparison:* their spillover runs from downstream developers back to the model owner; ours runs from open-model users to every developer through published data. Their openness is a scalar index with data disclosure as one of six dimensions, estimated on five commercial owners; ours is a discrete regime.
- **Xu, Wang, Chen and Xie (2025), [The Economics of AI Foundation Models](https://arxiv.org/abs/2510.15200).** Two-period game: an incumbent chooses an openness scalar that lowers a deployer's fine-tuning cost, an entrant learns from it, and a data flywheel lowers the incumbent's future cost. Openness is non-monotone in flywheel strength; transparency mandates can backfire. *Comparison:* their learning is a cost reduction keyed to adoption; ours is a vector of abilities keyed to task-weighted training data, so learning has a direction the firm chooses.
- **Qiu, Laufer, Kleinberg and Heidari (2025), [Modeling the Economic Impacts of AI Openness Regulation](https://arxiv.org/abs/2507.14193).** A generalist, a specialist fine-tuner and a regulator who sets an openness threshold. *Comparison:* no user population and no learning dynamics; their object is the regulator's definition.
- **Commey (2026), [Who Does Withholding Delay?](https://arxiv.org/abs/2607.22957)** Release tiers against adversaries who can substitute. Safety side only.
- **Nagle and Yue (2025), [The Latent Role of Open Models in the AI Economy](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5767103).** Empirical: on OpenRouter data closed models hold most tokens despite being several times more expensive, and frontier open models reach parity within months. *Comparison:* a stylized fact for our demand side. Our model gives price-only sorting; their persistence of closed-model share suggests switching costs or brand terms we omit.
- **Linåker, Osborne, Ding and Burtenshaw (2025), [A Cartography of Open Collaboration in Open Source AI](https://arxiv.org/abs/2509.25397).** Qualitative study of 14 open LLM projects. Corporate projects cite ecosystem building; research institutes cite open science; grassroots projects cite access and language representation. Curated datasets are what organizations are reluctant to share. *Comparison:* the motivation taxonomy for endogenizing the open provider, and evidence that excludable value sits in data rather than weights, which is why the open-data regime is the baseline here.

None of the formal models above has a user population in a task space, directional learning, or a single open model whose published data improves rivals. None treats models that release training data as a distinct type.

### 5.2 Models of open source ecosystems

- **Lerner and Tirole (2002), [Some Simple Economics of Open Source](https://onlinelibrary.wiley.com/doi/10.1111/1467-6451.00174).** Contributions as signals of skill paid off later through jobs and reputation. *Comparison:* our agents are firms, so the analog is talent attraction and standard-setting, neither of which is in the setup yet.
- **Johnson (2002), [Open Source Software: Private Provision of a Public Good](https://onlinelibrary.wiley.com/doi/10.1111/j.1430-9134.2002.00637.x).** User-programmers decide whether to build an enhancement that becomes a public good. *Comparison:* in our setting users do not build; they generate data by using. The public good is the open pool, provided by usage rather than effort.
- **Bessen (2005), [Open Source Software: Free Provision of Complex Public Goods](https://www.researchoninnovation.org/opensrc.pdf).** Complex goods cannot be served by standard products, so users customize and share. *Comparison:* our task space is the analog of product complexity; heterogeneity in θ is why no single model serves everyone.
- **von Hippel and von Krogh (2003), [Private-Collective Innovation](https://pubsonline.informs.org/doi/10.1287/orsc.14.2.209.14992)** and **Henkel (2006), [Selective revealing](https://ideas.repec.org/a/eee/respol/v35y2006i7p953-969.html).** Firms reveal when private benefits of revealing exceed the loss. *Comparison:* the open developer's objective, once endogenized. Releasing weights but not data is selective revealing with the know-how retained; it is the second regime of §3.6.
- **Athey and Ellison (2014), [Dynamics of Open Source Movements](https://onlinelibrary.wiley.com/doi/abs/10.1111/jems.12053).** Reciprocal altruism drives a project to a steady-state size, but a need for user support makes zero quality absorbing. *Comparison:* our open-model survival question is the same question with usage-driven data replacing contribution, and zero usage rather than zero quality as the absorbing state, since open weights persist.
- **Benkler (2002), [Coase's Penguin](https://arxiv.org/pdf/cs/0109077).** Peer production wins when tasks are modular and granular. *Comparison:* does not apply to the base-model layer, which is lumpy.
- **Casadesus-Masanell and Ghemawat (2006), [Dynamic Mixed Duopoly](https://www.hbs.edu/faculty/Pages/item.aspx?num=21129).** A profit maximizer against a zero-price rival with demand-side learning. *Comparison:* the closest ancestor. Our additions: a vector of abilities with directional learning, horizontal differentiation in task space, and data that flows from the free rival to the priced ones.
- **Economides and Katsamakas (2006), [Two-Sided Competition of Proprietary vs. Open Source Platforms](https://pubsonline.informs.org/doi/10.1287/mnsc.1060.0549).** Platform pricing toward users and complementors. *Comparison:* we have no complementor side; downstream developers would be a natural extension.
- **Mustonen (2003), [Copyleft](https://research.aalto.fi/en/publications/copyleft-the-economics-of-linux-and-other-open-source-software)** and **Lerner and Tirole (2005), [The Scope of Open Source Licensing](https://www.nber.org/papers/w9363).** License restrictiveness as a strategic variable. *Comparison:* license terms would decide whether closed firms may train on the book at all, which is the difference between the first two regimes of §3.6.
- **Bliss and Nalebuff (1984), Dragon-slaying and ballroom dancing, J. Public Econ. 25.** Private supply of a discrete public good as a war of attrition. *Comparison:* the natural frame for who provides the open model and its budget B, which the setup leaves exogenous.

### 5.3 Theories of the firm and industry dynamics

- **Ericson and Pakes (1995), [Markov-Perfect Industry Dynamics](https://ideas.repec.org/a/oup/restud/v62y1995i1p53-82..html).** Firms invest in a state that determines product-market profit, with Markov-perfect equilibrium in the state. *Comparison:* the frame of §1.5, with training data as the investment input and the stock as the state.
- **Spence (1981), [The Learning Curve and Competition](https://econbiz.de/Record/the-learning-curve-and-competition-spence/10005732041)** and **Fudenberg and Tirole (1983), [Learning-by-Doing and Market Performance](https://ideas.repec.org/a/rje/bellje/v14y1983iautumnp522-530.html).** Firms price below the static optimum because cumulative output lowers future cost, with spillover across firms as a parameter. *Comparison:* our forward-looking price with ability rising in cumulative usage data in place of cost falling in cumulative output. Their spillover parameter is what our public book replaces.
- **Cabral and Riordan (1994), [The Learning Curve, Market Dominance, and Predatory Pricing](https://econometricsociety.org/publications/econometrica/1994/09/01/learning-curve-market-dominance-and-predatory-pricing)** and **Besanko, Doraszelski, Kryukov and Satterthwaite (2010), [Learning-by-Doing, Organizational Forgetting, and Industry Dynamics](https://www.kellogg.northwestern.edu/faculty/satterthwaite/research/Learning%20by%20Doing.pdf).** When the learning curve produces increasing dominance; computational Markov-perfect treatment with forgetting. *Comparison:* "who starts ahead decides" is their increasing-dominance question; their forgetting is the depreciation rule in §4.
- **Athey and Schmutzler (2001), [Investment and Market Dominance](https://scholar.harvard.edu/files/athey/files/invest_mkt_dominance.pdf)** and **Budd, Harris and Vickers (1993), [A Model of the Evolution of Duopoly](https://ideas.repec.org/a/oup/restud/v60y1993i3p543-573..html).** Whether the leader or the laggard invests more; leaders usually do unless the laggard's investment is more effective. *Comparison:* the per-task concavity κ < 1 is the countervailing effect, since a token raises a smaller stock by more.
- **Cohen and Levinthal (1989), [Innovation and Learning: The Two Faces of R&D](https://ideas.repec.org/a/ecj/econjl/v99y1989i397p569-96.html).** Firms invest partly to absorb knowledge produced elsewhere. *Comparison:* the dropped absorption-cost version in §4. In the current model absorption is training on the book at the common compute price, so absorptive capacity is just compute.
- **Dierickx and Cool (1989), [Asset Stock Accumulation and Sustainability of Competitive Advantage](https://josephmahoney.web.illinois.edu/BA545_Fall%202022/Dierickx%20and%20Cool%20(1989).pdf).** Competitive assets are accumulated by flows, not bought; asset-mass efficiencies and time-compression diseconomies. *Comparison:* the training stock is such an asset. Their asset-mass efficiency has the opposite sign to our per-task concavity, which is worth saying when the sign for LLMs is argued.
- **Teece (1986), [Profiting from Technological Innovation](https://www.edegan.com/wiki/Teece_(1986)_-_Profiting_From_Technological_Innovation).** Profit from an innovation goes to whoever holds the scarce complementary assets. *Comparison:* under open data the scarce asset is private logs, which is why a closed firm's lead is its private pool relative to the public one.
- **Bolton and Scharfstein (1990), [A Theory of Predation Based on Agency Problems in Financial Contracting](https://ideas.repec.org/a/aea/aecrev/v80y1990i1p93-106.html).** Financial constraints invite rivals to drive a firm's performance down. *Comparison:* the open developer's budget B is such a constraint; a financing limit on closed firms is the extension in §5.5.
- **Hagiu and Wright (2023), [Data-enabled learning, network effects, and competitive advantage](https://awards.concurrences.com/en/awards/2024/academic-articles/data-enabled-learning-network-effects-and-competitive-advantage).** Dynamic competition between firms whose products improve with customer data, across-user and within-user learning, and how the shape of the learning function sets advantage. *Comparison:* the nearest published model. Ours adds a task space, a free rival whose data is public, and a compute cost of using data.
- **Farboodi and Veldkamp, [A Model of the Data Economy](https://www.nber.org/papers/w28427).** Data as an intangible asset generated by transactions that is stored, traded and depreciates. *Comparison:* our stock view of data without depreciation.

### 5.4 Scaling laws used in §1.3 and §1.4

- **Michaud, Liu, Girit and Tegmark (2023), [The Quantization Model of Neural Scaling](https://arxiv.org/abs/2303.13506v3).** Discrete skills with Zipf use frequencies pₙ ∝ n^{−(α+1)}, learned once seen about τ times, so the count learned from D samples grows like D^{1/(α+1)}, the data exponent of the loss is α/(α+1), and each skill needs a fixed number of parameters. *Use:* the power law, κ = 1/(1+α) = 1 − α_D, and model size proportional to total ability.
- **Hoffmann et al. (2022), [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556v1).** Training compute proportional to parameters times tokens; parameters and tokens scaled together at the compute-optimal frontier. *Use:* cost per token proportional to model size. Their fitted data exponent is the other route to κ.
- **Muennighoff et al. (2023), [Scaling Data-Constrained Language Models](https://arxiv.org/abs/2305.16264v2).** Repeated epochs add little beyond a few. *Use:* stocks count unique tokens.
- **Hernandez, Kaplan, Henighan and McCandlish (2021), [Scaling Laws for Transfer](https://arxiv.org/abs/2102.01293v1)** and **Ye et al. (2024), [Data Mixing Laws](https://arxiv.org/abs/2403.16952v1).** Pretraining on one distribution multiplies the effective size of data on another; per-domain loss is a predictable function of the mixture. *Use:* the transfer matrix T, if it is ever set away from I.

### 5.5 What the setup leaves out

- The open developer's choice to release or withhold, and partial release. It publishes everything by construction; the second regime of §3.6 is the comparison, not a choice.
- The open provider's identity and the source of B: a complement-seller commoditizing the model layer, a nonprofit, or a state. This is the discrete-public-good game among heterogeneous firms that none of the LLM-era models studies.
- A financing limit on closed firms. They are assumed able to run losses; the discounted sum has deep pockets built in.
- Any difference between open logs and closed logs as training data, such as responses from a weaker model.
- Switching costs, brand and information frictions on the demand side, which Nagle and Yue suggest are large.
- A downstream developer layer, which is where Jamison–Yu locate the spillover.

## 6. Open issues

- **κ.** 0.7 is a working value. It should be read off the exponents fitted in Michaud et al.'s Appendix F or from Hoffmann et al.'s data exponent via κ = 1 − α_D.
- **Ability as a skill count.** A modeling choice the scaling-law papers do not make; stated as an assumption in §1.3 and worth revisiting if the bounded reading turns out to matter.
- **Existence in the price and training stages.** Demand in own price is step-like, so the per-period games may lack a pure fixed point. The simulation reports cycles; a tie-breaking or smoothing rule may be needed.
- **Lookahead as an approximation.** H = 2 contains every channel but is not the infinite-horizon equilibrium. The asymptotic-myopia argument of §2 says the gap shrinks over time; it should be checked by varying H.
- **Units and speed.** The ratio of P⁰ to a period's usage sets how fast anything moves and is now a parameter, as are c₀ relative to revenue and B.
- **Whether the open model is weaker than its own pool** in realistic parameter ranges, since that regime is what makes the sponsor's budget matter.
