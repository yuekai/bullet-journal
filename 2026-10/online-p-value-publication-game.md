---
title: Online p-value publication game
description: Online version of the editor–author p-value publication game, where hypotheses are registered one at a time under a budget rule; validity for every author strategy, subgame-perfect best responses, and padding under alpha-investing
date: 2026-10-01
---

This note is a companion to the [basic-game note](../2026-09/strategic-p-value-publication-game.md), which studies an editor who commits to a publication rule and an author who holds N p-values and chooses which to submit. There, the editor must know N (its Result 1), and once it does, the game reduces to offline multiple testing (its Results 2–3), with Holm as the FWER equilibrium and BY as the FDR equilibrium. Here hypotheses are registered and tested one at a time, so the number of tests becomes the author's choice and the editor never needs to know it in advance. The editor's constraint is FWER ≤ α (§2.1–2.2) or mFDR ≤ α (§2.3).

## 1. Setup

- **Why registration is needed.** Suppose the author has already seen all p-values and feeds them in one at a time. Then any online rule can be gamed: the author puts the smallest p-value where the threshold is most generous, which is cherry-picking again (Result 1 of the [p-value publication game note](../2026-09/strategic-p-value-publication-game.md)). So in the online game the author registers each hypothesis, and its level, before its data exist.
- **Timing.** In period t = 1, 2, …:
  1. The author either stops, or registers a new hypothesis H_{i_t} together with a level a_t ∈ [0, 1]. The registration is public.
  2. Fresh data are collected at cost c to the author, producing p_t.
  3. If p_t ≤ a_t the author may submit it, and the editor publishes H_{i_t}. Otherwise nothing is published.
- **Information.** Let F_{t−1} be everything observed before p_t: past registrations, levels and p-values, and the current registration. The author's choices (i_t, a_t) and whether to stop may depend on F_{t−1} in any way, and may be randomised.
- **Validity (the online analogue of the standing assumptions in §1.2 of the [basic-game note](../2026-09/strategic-p-value-publication-game.md)).** If H_{i_t} is a true null, then P(p_t ≤ u | F_{t−1}) ≤ u for every F_{t−1}-measurable u. Each test uses fresh data, so the past can't make a null p-value look small. Beyond this, dependence is arbitrary.
- **Preferences.**
  - **Author:** a reward R per publication and a cost c per test: U = R·(publications) − c·(tests). The number of tests N is now the author's choice.
  - **Editor:** maximise publications subject to the error constraint, for every author strategy.
- **Editor's rules.** The editor commits to a *budget rule*, i.e. which level sequences the author may register.
  - **Spending:** Σ_t a_t ≤ α.
  - **Recycling:** each rejection refunds its level. The outstanding commitment O_t = Σ_{s ≤ t} a_s − Σ_{s < t, H_{i_s} published} a_s must satisfy O_t ≤ α at every t.
  - **Investing (Foster & Stine):** alpha-wealth W₀ = α. A rejection earns ω = α; a non-rejection costs a_t/(1 − a_t). The author may register a_t only if it can pay the cost.

  In each case the author, not the editor, chooses which hypotheses to test, in what order, and at what levels. The editor only enforces the budget.
- **Solution concept.** The editor commits to its rule before the game starts, so each round is a decision node for the author alone. The author's problem is a single-agent dynamic program, and by a *best response* we mean a subgame-perfect one: a strategy that is optimal after every history, including histories it would never reach itself.
- **Submissions.** The last move of every round is whether to submit p_t. Submitting a rejection is strictly optimal in that subgame under all three rules: it pays R > 0, and under recycling and investing it also earns a refund or a payout; under spending it costs nothing. So the author submits exactly the published results. This is the online counterpart of Result 3.4 of the [basic-game note](../2026-09/strategic-p-value-publication-game.md): the editor needs only the registrations and the rejections.

## 2. Results

### 2.1 Validity for every author strategy

**Result 1.** Under spending or recycling, FWER ≤ α for every author strategy: adaptive choice of hypotheses, levels and stopping, including randomised strategies.

*Proof.* Spending is recycling without refunds, so it suffices to prove the result for recycling.
- Let τ be the period of the first false rejection, with τ = ∞ if there is none. Write nullₜ = 1{H_{i_t} is a true null}.
- **Pathwise budget bound.** Fix t ≤ τ. Every null hypothesis tested before t was not rejected (otherwise τ < t), so its level was never refunded. Refunds before t come only from rejected, hence non-null, hypotheses. So

  Σ_{s ≤ t} null_s·a_s ≤ Σ_{s ≤ t} a_s − Σ_{s < t, rejected} a_s = O_t ≤ α.

  Letting t ↑ τ, we get Σ_{s ≤ τ} null_s·a_s ≤ α on every path, including τ = ∞.
- **Union bound over periods.** The event {t ≤ τ} means there is no false rejection before t. It lies in F_{t−1}, as do nullₜ and aₜ. So

  FWER = P(τ < ∞) = Σ_t P(τ = t) ≤ Σ_t E[nullₜ·1{t ≤ τ}·P(pₜ ≤ aₜ | F_{t−1})] ≤ E[Σ_{t ≤ τ} nullₜ·aₜ] ≤ α.

  The middle step uses the validity assumption; the last uses the pathwise bound. Monotone convergence handles the infinite horizon. ∎

**Remarks.**
- Recycling is the online analogue of Holm. Holm is the graphical procedure with equal initial weights and equal transition coefficients: every rejection passes its level on to the remaining hypotheses ([Bretz et al. 2009](https://onlinelibrary.wiley.com/doi/10.1002/sim.3495)). Recycling with a pre-specified order is online fallback, proved valid under arbitrary dependence by [Tian & Ramdas 2021](https://arxiv.org/abs/1910.04900). Result 1 extends that validity to hypotheses and levels chosen adaptively by the author, under the conditional validity assumption.
- **Investing:** Foster & Stine's Theorem 1 gives E[V(T_r)] ≤ α(r + 1), where T_r is the time of the r-th rejection. That is uniform control of mFDR₁ = E[V]/(E[R] + 1). It requires only that each null test have conditional level at most aₜ given the past outcomes, and the next hypothesis may be chosen using past rejections ([Foster & Stine 2008](http://www-stat.wharton.upenn.edu/~stine/research/mfdr.pdf)). So the guarantee also holds for every author strategy.
- Online FDR (rather than mFDR) is harder. LORD controls FDR when the null p-values are independent ([Javanmard & Montanari 2018](https://projecteuclid.org/journals/annals-of-statistics/volume-46/issue-2/Online-rules-for-control-of-false-discovery-rate-and-false/10.1214/17-AOS1559.pdf)); a reshaped LOND controls it under arbitrary dependence.

### 2.2 Best responses under FWER budgets

**Result 2 (spending).** Suppose the author's beliefs treat hypotheses independently: testing Hᵢ at level a yields a publication with probability Gᵢ(a), whatever happened before. Then under spending:
1. **No adaptivity gain:** the optimal payoff is attained by a static plan, a set T of hypotheses with levels (aᵢ)_{i ∈ T}, Σaᵢ ≤ α. It maximises Σ_{i ∈ T} (R·Gᵢ(aᵢ) − c). The order of testing is irrelevant.
2. **Finite N:** every tested hypothesis has R·Gᵢ(aᵢ) ≥ c, so N = |T| ≤ α/a_c, where a_c = min_i Gᵢ⁻¹(c/R) is the smallest level at which any hypothesis has publication probability c/R.
3. **Equal marginal power:** if each Gᵢ is concave and differentiable, the levels satisfy R·Gᵢ′(aᵢ) = λ for every tested hypothesis, for a common λ ≥ 0, whenever the budget binds.
4. **Equivalence to pre-registered weights:** the outcome is offline weighted Bonferroni with weights wᵢ = aᵢ/α chosen by the author.
5. **Subgame perfection:** a static plan says nothing about histories off its own path. The strategy that depends only on the current state is subgame perfect and agrees with the static plan on the plan's path: *at any history, solve the static problem on the remaining hypotheses with the remaining budget α − Σ(spent), and test the next hypothesis of that solution, breaking ties in a fixed order.*

*Proof.*
1. Under spending, the budget used depends only on the levels registered, not on outcomes. Given F_{t−1}, the expected reward of period t is R·G_{i_t}(a_t) − c, by the independence assumption. So the expected payoff of any strategy is E[Σ_t (R·G_{i_t}(a_t) − c)].

   Every realised sequence of registrations is a feasible static plan (Σa ≤ α, distinct hypotheses), so its sum is at most the best static plan's value. Taking expectations, no adaptive strategy beats the best static plan, and that plan can be carried out in any order.
2. If a tested i had R·Gᵢ(aᵢ) < c, dropping it would raise the payoff and free budget. So R·Gᵢ(aᵢ) ≥ c, i.e. aᵢ ≥ Gᵢ⁻¹(c/R) ≥ a_c, and Σaᵢ ≤ α gives |T| ≤ α/a_c.
3. This is the KKT condition for maximising a separable concave objective under Σaᵢ ≤ α.
4. The static plan rejects Hᵢ iff pᵢ ≤ αwᵢ with Σwᵢ ≤ 1, which is weighted Bonferroni.
5. Under spending and independent beliefs, the continuation problem after any history depends only on which hypotheses remain and how much budget remains: past outcomes don't matter, because nothing is refunded. By part 1 applied to that continuation problem, re-solving the static problem is optimal after every history. On the path of an ex-ante optimal plan, the rest of the plan is optimal for the remaining hypotheses and budget: a better continuation, combined with the part already carried out, would beat the ex-ante optimum, since the payoff is a sum of separate terms R·Gᵢ(aᵢ) − c. So, with the same tie-breaking, the state-based strategy reproduces the plan on its path. ∎

**Notes on Result 2.**
- **Endogenous N without knowing N.** The editor never needs N. The budget plus the cost c bound the number of tests. When G′(0) = ∞, as for Gaussian alternatives, levels can be tiny; a_c is still positive, so N is finite.
- **Optimal levels are not monotone in strength.** A near-certain hypothesis clears a tiny level, so it gets little budget, and the generous levels go to borderline hypotheses. This is the Roeder–Wasserman optimal weighting, carried out by the author, who holds the beliefs.
- **An editor-fixed schedule is weakly worse.** If the editor fixes γ_t and the author only chooses the order, the author solves an assignment problem over a smaller set of plans, so their best payoff can only be lower.
- **When adaptivity helps.** If outcomes are informative about other hypotheses (correlated beliefs), adaptivity can help even under spending, because learning changes the Gᵢ. The state must then include the author's posterior beliefs. Backward induction still gives a subgame-perfect strategy, but it is no longer static.

**Recycling.** Under recycling, a hypothesis tested at level a costs budget a·(1 − Gᵢ(a)) in expectation, since rejections are refunded. Two consequences:
- **Order matters.** The state is the remaining pool plus the outstanding commitment, and transitions are random, because rejections refund.
  - With a finite pool and c > 0 the problem has a finite horizon; levels lie in a compact set and payoffs are continuous; so backward induction yields a subgame-perfect strategy.
  - Intuitively that strategy front-loads high-power hypotheses, since testing likely rejections first frees budget for later tests. But this is only a heuristic: the problem resembles a stochastic knapsack, where simple index rules are generally not optimal. Characterising the subgame-perfect strategy is left open (§4.1).
  - With an unlimited supply of near-certain hypotheses and R > c, the author could keep testing them for R − c each. Payoffs would be unbounded and no best response would exist. So a finite pool, or R ≤ c for trivial hypotheses, is needed.
- **Padding is neutral.** A near-certain hypothesis is refunded almost surely, so it uses no budget. It earns a trivial publication worth R − c but doesn't loosen any other threshold, and by Result 1 FWER ≤ α still bounds the probability of any false publication.

### 2.3 Investing rewards padding

**Result 3.** Under alpha-investing (W₀ = ω = α), suppose the author can test near-certain hypotheses (rejected with probability 1 at any level a > 0).
1. **Padding inflates false publications:** for every K there is an author strategy that keeps mFDR₁ ≤ α while the expected number of false publications exceeds K.
2. **Padding is sequentially rational:** at every history, a subgame-perfect strategy tests every profitable near-certain hypothesis before anything speculative. A near-certain hypothesis is profitable if R − c plus the value of the extra wealth ω is positive, which can hold even when R < c.

*Proof sketch of 1.*
- Test k near-certain hypotheses at tiny levels. Each is rejected and earns ω = α, so the wealth becomes W = α + kα.
- Then test true nulls at a fixed level a until the wealth can't cover a/(1 − a). For a uniform null p-value, a test changes the wealth by +ω with probability a and −a/(1 − a) otherwise, so the expected change is −a(1 − α).
- Let M be the number of null tests. Wald's identity gives E[M]·a(1 − α) = W − E[W_end], and W_end < a/(1 − a). So

  E[V] = a·E[M] ≥ (α(1 + k) − a/(1 − a))/(1 − α),

  which grows linearly in k.
- Foster–Stine's theorem still gives mFDR₁ ≤ α, because the padded rejections also inflate E[R]. ∎

*Proof of 2.*
- The state is wealth w plus the remaining pool. The continuation value V(w, pool) is nondecreasing in w, because more wealth only enlarges the set of affordable levels.
- Tested at a tiny level, a near-certain hypothesis is rejected with probability 1. It earns R − c plus the payout ω, and costs no wealth.
- **Exchange argument:** moving it earlier leaves its own payoff unchanged and gives the author ω sooner, which by monotonicity of V can only help. So after every history, testing the remaining profitable near-certain hypotheses first is optimal. ∎

Part 1 shows a strategy with large false publications exists; part 2 shows that a sequentially rational author actually plays its padding phase.

This is the online version of Finner–Roters padding, and Foster & Stine flag it themselves with the example of first testing "gravity does not exist". Under spending, padding uses budget; under recycling it is neutral; only investing pays for it. Counters are a per-test cost c with R·α ≤ c, so that farming wealth doesn't pay; payouts withheld for hypotheses that aren't novel, which the editor can't verify; or an FWER budget instead.

### 2.4 Summary

| Budget rule | Guarantee for every author strategy | Subgame-perfect best response | Padding |
|---|---|---|---|
| Spending | FWER ≤ α (Result 1) | Re-solve the static plan at each history; on path, author-weighted Bonferroni with N ≤ α/a_c (Result 2) | Uses budget |
| Recycling | FWER ≤ α (Result 1) | Dynamic-programming solution (exists for a finite pool and c > 0); front-loading likely rejections is a heuristic (open) | Neutral |
| Investing | mFDR₁ ≤ α (Foster–Stine) | Pad first with every profitable near-certain hypothesis, then speculate (Result 3.2) | Rewarded: E[V] unbounded (Result 3.1) |

For an editor facing strategic authors, recycling is the online counterpart of Holm, and the best of the three. Investing needs a per-test cost to stop padding.

## 3. Related work

### 3.1 Online multiple testing

- **[Foster & Stine (2008), "α-investing"](http://www-stat.wharton.upenn.edu/~stine/research/mfdr.pdf)** (JRSSB 70:429–444).
  Alpha-investing, the investing rule of §1, starts with alpha-wealth W(0) and tests hypotheses in sequence at levels set by an investing rule. A rejection earns a payout ω; a non-rejection costs αⱼ/(1 − αⱼ). With W(0) = ω = α, their Theorem 1 gives E[V(T_r)] ≤ α(r + 1) at the time of the r-th rejection, i.e. uniform control of mFDR₁ = E[V]/(E[R] + 1). The only requirement is that each null test have conditional level at most αⱼ given past outcomes, which is our online validity assumption. Tests may be dependent, and the next hypothesis may be chosen using past rejections, so the guarantee holds for every author strategy. They also note that trivially false hypotheses ("gravity does not exist") inflate the wealth, and that step-down tests share the problem. Result 3 makes the remark quantitative: expected false publications can be unbounded while mFDR stays controlled.
- **[Javanmard & Montanari (2018), "Online rules for control of false discovery rate and false discovery exceedance"](https://projecteuclid.org/journals/annals-of-statistics/volume-46/issue-2/Online-rules-for-control-of-false-discovery-rate-and-false/10.1214/17-AOS1559.pdf)** (Ann. Statist. 46:526–554).
  LORD ("levels based on recent discovery") is a generalized alpha-investing rule. It controls FDR, not just mFDR, at every fixed time when the null p-values are independent. A reshaped version of LOND controls FDR under arbitrary dependence, and they also study the false-discovery exceedance. Later work (GAI++, LORD++) improves power while keeping FDR control when the null p-values are independent of the rest. These are the natural rules for an FDR, rather than mFDR, online game. But they inherit the padding problem, since rejections raise future levels, and LORD needs independent null p-values, which is stronger than our online validity assumption.
- **[Tian & Ramdas (2021), "Online control of the familywise error rate"](https://arxiv.org/abs/1910.04900)** (Stat. Methods Med. Res.).
  They show that alpha-spending (online Bonferroni) and online fallback, which recycles each rejected hypothesis's level to later tests, control FWER under arbitrary dependence. Online fallback is at least as powerful as alpha-spending (Proposition 2), with large gains only when non-nulls come early. These are our spending and recycling rules with levels and order fixed in advance. Result 1 extends their validity to hypotheses and levels chosen adaptively by a strategic author, under conditional validity, and their early-non-null observation is why our author front-loads likely rejections. Their ADDIS-spending adds adaptivity and discarding of conservative nulls, with FWER control under independence or local dependence.
- **[Bretz, Maurer, Brannath & Posch (2009), "A graphical approach to sequentially rejective multiple test procedures"](https://onlinelibrary.wiley.com/doi/10.1002/sim.3495)** (Stat. Med. 28:586–604).
  Their weighted-Bonferroni procedures pass the level of each rejected hypothesis to others along a directed weighted graph. They control FWER strongly and include gatekeeping, fixed-sequence and fallback procedures. With equal initial weights and equal transition coefficients, the graph reproduces Holm. Recycling in our online game is a sequential version of such a graph, designed by the author as they go, which is why we call it the online analogue of Holm (§2.1).

### 3.2 Strategic-testing papers

These papers are described in detail in §3 of the [basic-game note](../2026-09/strategic-p-value-publication-game.md); here are their connections to the online game.

- **Kasy & Spiess, ["Optimal Pre-Analysis Plans"](https://arxiv.org/abs/2208.09638).** The author's registered levels play the role of their pre-analysis message: the author chooses how to spend the error budget before the data exist, using private beliefs. Unlike their single-decision setting, the online author sends a sequence of messages, each after seeing earlier outcomes.
- **McCloskey & Michaillat, ["Critical Values Robust to P-hacking"](https://pascalmichaillat.org/12.pdf).** Their scientist runs experiments until one is significant, and the journal never sees how many were run; they escape the "unknown N" impossibility by dividing α by the equilibrium expected number of attempts, which gives only an average guarantee. The online game is another way out: registering each test makes the count observable, and the budget and per-test cost bound how many tests the author runs (Result 2), with a guarantee for each author rather than an average one.
- **Bates, Jordan, Sklar & Soloff, ["Principal-Agent Hypothesis Testing"](https://arxiv.org/abs/2205.06812).** Their agent pays C for a trial given private beliefs, and a contract is incentive-aligned iff no null agent profits (license functions divided by C are e-values). In the online game the author pays c to test each hypothesis given private beliefs about it, and incentive alignment becomes R·P_null(published) ≤ c for each hypothesis. A hypothesis registered at level a is published with null probability at most a, so testing a hypothesis the author believes null is unprofitable once a ≤ c/R; by their Proposition 4, c/R is the level a profit-capped agent's own likelihood-ratio test would use. Under spending, Result 2.2 is this condition at the margin: every tested hypothesis has R·Gᵢ(aᵢ) ≥ c. So the online game gets a per-author FWER guarantee plus their screening effect: only hypotheses the author thinks promising get tested, which raises the share of true effects among those tested. Their Theorem 2 (offer the largest incentive-aligned menu) corresponds to letting the author choose levels within the budget rather than imposing a fixed schedule, which Result 2 shows is weakly worse. Their multi-round contracts, where a null agent's net profit is a supermartingale, parallel alpha-investing, where a null test lowers expected wealth. Result 3 shows the difference: our author can also test hypotheses that are certain to be rejected, and farm wealth.
- **Hossain, Chen & Chen, ["Strategic Hypothesis Testing"](https://arxiv.org/abs/2508.03289).** Their agent chooses whether to participate and how large a trial to run, against a committed p-value threshold α; the analogue here is the author's choice of how many hypotheses to test. Their critical threshold α̂ (the most stringent α at which exactly the effective agents participate) is the analogue of choosing the budget α so that testing a believed-null hypothesis is unprofitable (levels a ≤ c/R) exactly at the margin the editor wants. Below it, only hypotheses the author believes in get tested and false publications come only from mistaken beliefs, which parallels their Theorem 4.1; stricter thresholds then only lose true discoveries, which parallels their abstention false negatives. Their non-monotonicity below α̂ warns that an editor tuning α for welfare should expect non-monotone effects on discoveries. A natural editor objective in their style is expected true discoveries minus c·N, subject to FWER, with N the number of tests the author chooses in Result 2.
- **Viviano, Wüthrich & Niehaus, ["A model of multiple hypothesis testing"](https://arxiv.org/abs/2104.13367).** They derive the amount of multiple-testing correction from research costs: corrections are warranted to the extent that costs don't scale with the number of hypotheses. In the online game the per-test cost c plays a similar role: it, not the editor, determines how many hypotheses get tested.

## 4. Open directions

### 4.1 Unproven claims

1. The author's subgame-perfect strategy under recycling (§2.2), a stochastic knapsack-type dynamic program, and whether front-loading likely rejections is optimal.
2. Result 2 when the author's beliefs are correlated across hypotheses, so that outcomes are informative and adaptivity helps even under spending.
3. Result 3 with near-certain rather than certain hypotheses, and with the per-test cost c included.

### 4.2 Directions

1. **Endogenous N.** The author pays c per test and earns R per publication, so U = R·(publications) − c·N, and Result 2 bounds N under spending: N ≤ α/a_c with a_c = min_i Gᵢ⁻¹(c/R). Questions:
   - Comparative statics of N* and of publications as c/R → 0, for concrete families such as Gaussian shifts, where G′(0) = ∞.
   - The welfare-optimal budget α for an editor who values expected true discoveries minus the author's cost c·N, in the style of Hossain, Chen & Chen (§3.2). Is there an analogue of their critical threshold α̂? They show the principal's optimal α is at least α̂ and that false positives are zero below α̂.
   - The same questions under recycling, where the author's subgame-perfect strategy is open.
2. **Padding under investing.** Result 3 shows alpha-investing rewards padding: expected false publications are unbounded under mFDR control, and padding first is subgame perfect. How large must the per-test cost c be, relative to R and α, to make padding unprofitable? A first guess is R·α ≤ c (sketch). Do FDR rules such as LORD (§3.1) admit the same attack, and can payouts be designed so that near-certain rejections earn nothing without the editor having to judge novelty?
3. **FDR instead of mFDR.** Online FDR control under our conditional-validity assumption alone: LORD needs independent null p-values and a reshaped LOND pays a dependence penalty. Which online FDR rule is valid for every author strategy, and what does the author's best response look like?
