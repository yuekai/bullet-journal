---
title: Strategic p-value publication game
description: Write-up of an editor–author Stackelberg game over which p-values to publish; with N known the game reduces to offline multiple testing, so Holm is the equilibrium under FWER and BY under FDR; extensions, related work and open questions
date: 2026-09-29
---

## 1. Setup

### 1.1 The game

- **Players.** An editor and an author.
- **Data.** The author holds p-values p₁, …, p_N for hypotheses H₁, …, H_N, of which N₀ are true nulls. Each null p-value is valid on its own: P(pᵢ ≤ t) ≤ t. The dependence between p-values is arbitrary unless stated otherwise.
- **Timing (Stackelberg).**
  1. The editor commits to a publication rule, which maps a submitted set S and a count N to a published set R(S; N) ⊆ S.
  2. The author sees all p-values and submits S.
  3. The editor publishes R(S; N).
- **Preferences.**
  - **Author:** maximise |R|, then minimise |S| (lexicographic).
  - **Editor:** maximise |R| subject to an error guarantee on R.
- **Error guarantees.** FWER = P(R contains a true null), or FDR = E[|R ∩ H₀| / max(|R|, 1)]. We distinguish:
  - **All-strategy guarantees:** they hold for every submission S, however it depends on the data.
  - **Equilibrium guarantees:** they hold only at the author's best response.

### 1.2 Standing assumptions

1. N is fixed in advance, covers every test the author ran, and is known to the editor.
2. Each p-value comes from one pre-specified analysis of its hypothesis.
3. The family of hypotheses is not chosen after seeing results.

Every result below fails if any of these fails.

## 2. Results

Throughout, the p-values may be arbitrarily dependent unless stated otherwise. §2.1 shows the editor must know N. §2.2 shows that, once N is known, the game reduces to offline multiple testing. §2.3 gives two refinements of the reduction, and §2.4–2.5 apply it to FWER (Holm) and FDR (BY). An online version, in which hypotheses are registered one at a time and the author chooses how many to test, is developed in a [companion note](../2026-10/online-p-value-publication-game.md).

### 2.1 N must be known

**Result 1.** Any rule that depends only on the submitted p-values can be gamed. For example, with Bonferroni on the submitted count, α/|S|, the author submits only the smallest p-value. With N₀ nulls that p-value is about 1/N₀, so FWER → 1 as N₀ → ∞. If N is unknown and can be arbitrarily large, the only rule with FWER ≤ α for every author is to publish nothing.

### 2.2 With N known, the game reduces to offline multiple testing

**Definitions.**
- An *offline procedure* D maps the full vector of p-values p ∈ [0,1]^N to a rejection set D(p) ⊆ [N]. It may be randomised through an independent variable U, which we suppress.
- An *error metric* M is a function of the rejected set and the true nulls, such as FWER or FDR. D is *valid* for M at level α if E[M(D(p))] ≤ α for every joint distribution in the assumed class (here, arbitrary dependence with valid null p-values).
- For a submission S, a *completion* is any p′ ∈ [0,1]^N with p′_S = p_S. D's *worst-case rule* publishes the submitted hypotheses that D rejects under every completion:

  R_D(S) = { i ∈ S : i ∈ D(p′) for every completion p′ of p_S }.

  This adapts the worst-case imputation of Kasy & Spiess (§3.1) to rejection sets.
- The editor's *equilibrium payoff* is any function of the published set and the truth, for example expected publications or expected true publications.

**Result 2 (reduction).** Fix the error metric M and the dependence class.
1. **Every valid procedure can be implemented.** If D is valid, then under the rule R_D every best response of the author publishes exactly D(p). So R_D has equilibrium guarantee α, and the same equilibrium payoff as running D offline.
2. **No rule does better.** For any editor rule R and any best-response strategy of the author, the published set is D_R(p) for a (possibly randomised) offline procedure D_R. If R has equilibrium guarantee α, then D_R is valid.
3. **So the game's value equals the offline value.** The editor's best rule implements the best valid offline procedure, and the editor's optimum in the game equals the optimum over valid offline procedures.

*Proof of 1.*
- The true vector p is itself a completion of p_S, so R_D(S) ⊆ D(p) for every S.
- If the author submits every p-value (S = [N]), the only completion is p, so R_D([N]) = D(p).
- Every best response maximises |R_D(S)|. That maximum is |D(p)|, because R_D(S) ⊆ D(p) and S = [N] attains it. A set R_D(S) ⊆ D(p) with |R_D(S)| = |D(p)| equals D(p).
- Hence every best response publishes D(p), whatever the tie-breaking. The published set's error is that of D, so the equilibrium guarantee and payoff are D's.
- (Measurability: for monotone D, part 3 of Result 3 shows R_D(S) = D(p^S), which is measurable whenever D is. For general D we assume R_D is measurable.)

*Proof of 2: the induced procedure is well defined under arbitrary tie-breaking.*
- Let R be any rule with each R(S, p_S) measurable in p_S. For a fixed S, |R(S, p_S)| is a measurable function of p.
- The author's best-response set is

  BR(p) = { S : |R(S, p_S)| = max_T |R(T, p_T)|, and |S| is minimal among such S }.

  It is non-empty because there are only 2^N subsets. For each S, the event {S ∈ BR(p)} is defined by finitely many comparisons of measurable functions, so it is measurable.
- A *best-response strategy* is a map σ(p, U) ∈ BR(p), measurable in (p, U), where U is the author's independent randomisation. Such maps exist; for example, take the first element of BR(p) in a fixed order of the 2^N subsets. Any measurable way of mixing over BR(p) is also allowed.
- Define D_R(p, U) = R(σ(p, U), p_σ(p,U)) = ⋃_S 1{σ(p, U) = S}·R(S, p_S). This is a finite union of measurable pieces, so it is measurable. It depends on the data only through p, plus the independent U, so it is a randomised offline procedure.
- On the equilibrium path the published set is exactly D_R(p, U), so its error under every distribution is that of D_R. If R guarantees error ≤ α at the best response σ, then D_R is valid. If the editor wants the guarantee whatever the author's tie-breaking, the same holds for every σ.
- The editor's payoff under (R, σ) equals the offline payoff of D_R, which is at most the offline optimum over valid (randomised) procedures. Part 1 shows the optimum is attained by R_D, and there tie-breaking doesn't matter. ∎

**Connection.** Result 2 extends the observation of Kasy & Spiess (§3.1) that when the decision-maker knows which statistics exist, selective reporting has no bite, and their worst-case imputation mechanism to multiple decisions. Kasy–Spiess leave the multiple-decision version of their full setting (unknown availability, private expertise, pre-analysis plans) for future work; we leave it open too. What our setting adds beyond their intuition is in §2.3 (minimal submissions, and FDR guarantees for every submission) and in padding (§2.5).

### 2.3 Refinements: guarantees for every submission, and minimal submissions

Result 2 is about the author's best response. Two further questions are:
- Does the guarantee survive an author who submits something else, for example one who cares about which results get published?
- Does the author submit only what gets published?

**Definitions.**
- D is *monotone* if p′ ≤ p coordinatewise implies D(p) ⊆ D(p′): a smaller p-value can only add rejections.
- D is *self-sufficient* if D(p^{D(p)}) = D(p), where p^T sets every p-value outside T to 1. Equivalently, D's rejections depend only on the p-values it rejects.
- D *ignores p = 1* if it never rejects a hypothesis whose p-value is 1.
- A metric is *V-monotone* if it is a nondecreasing function of the number of false rejections V. Examples: FWER = P(V ≥ 1), k-FWER = P(V ≥ k), E[V] and E[f(V)] for nondecreasing f. FDR and tail bounds on the false-discovery proportion are not V-monotone.

**Result 3.**
1. **Guarantees for every submission, V-monotone metrics.** If D is valid for a V-monotone metric, then R_D(S) satisfies the guarantee for every submission S, however S depends on the data.
2. **Guarantees for every submission, FDR.** If D is the BY step-up procedure, which is monotone, self-sufficient and ignores p = 1, then R_D(S) has FDR ≤ αN₀/N for every submission S, under arbitrary dependence.
3. **Monotone procedures use p = 1 as the worst case.** If D is monotone and ignores p = 1, then R_D(S) = D(p^S). So the editor runs D with unreported p-values set to 1.
4. **Minimal submissions.** If D is also self-sufficient, the author's unique minimal best response is S = D(p): the author submits exactly what gets published.
5. **Fixed-threshold step-down and step-up procedures qualify.** Any step-down or step-up procedure with nondecreasing critical values c₁ ≤ … ≤ c_N < 1 is monotone, self-sufficient and ignores p = 1. This covers Bonferroni, Holm, Hochberg, BH and BY.

*Proof of 1.* R_D(S) ⊆ D(p) pointwise, so the number of false rejections satisfies V(R_D(S)) ≤ V(D(p)) for every realisation and every S. A nondecreasing function of V is therefore no larger than D's, so its expectation is at most α. ∎

*Proof of 3.*
- Let p^S be p with unreported p-values set to 1. Every completion p′ of p_S satisfies p′ ≤ p^S coordinatewise, so monotonicity gives D(p^S) ⊆ D(p′).
- Hence D(p^S) ⊆ ⋂ D(p′). Since p^S is itself a completion, the intersection equals D(p^S).
- Because D ignores p = 1, D(p^S) ⊆ S, so R_D(S) = D(p^S). ∎

*Proof of 4.*
- By Result 2.1, every best response publishes D(p), and R_D(S) ⊆ S. So every best response contains D(p).
- By part 3 and self-sufficiency, R_D(D(p)) = D(p^{D(p)}) = D(p). So S = D(p) is a best response, and it is the unique smallest one. ∎

*Proof of 2.*
- By part 3, R_D(S) = BY(p^S). BY is a step-up procedure with critical values c_j = αj/(N·H_N), so BY(p^S) = {i : p^S_i ≤ c_k}, where k = |BY(p^S)| (see the proof of part 5).
- Every published i lies in S, so p_i = p^S_i ≤ αk/(N·H_N). The published set is therefore self-consistent with respect to the true p, with the Benjamini–Yekutieli shape β(r) = r/H_N.
- Blanchard & Roquain's Propositions 2.7 and 3.7 show that any self-consistent set with this shape has FDR ≤ αN₀/N under arbitrary dependence, however the set was chosen. ∎

*Proof of 5.* Let p_(1) ≤ … ≤ p_(N) be the order statistics.
- **The rejection index:**
  - step-down: k(p) = max{ j : p_(i) ≤ c_i for all i ≤ j };
  - step-up: k(p) = max{ j : p_(j) ≤ c_j };
  - with k = 0 if the set is empty.
- **Set form:** D(p) = { i : pᵢ ≤ c_k(p) }, with c₀ = −∞.
  - For i ≤ k: p_(i) ≤ c_i ≤ c_k in the step-down case, and p_(i) ≤ p_(k) ≤ c_k in the step-up case.
  - For j > k: in the step-down case p_(k+1) > c_(k+1) ≥ c_k, and every later order statistic is at least p_(k+1). In the step-up case p_(j) > c_j ≥ c_k by maximality of k.
  - So the k smallest p-values are exactly those at most c_k, ties included.
- **Monotone:** suppose p′ ≤ p coordinatewise. Then p′_(i) ≤ p_(i) for every i (a standard property of order statistics), so every condition defining k(p) still holds for p′, and k(p′) ≥ k(p). For i ∈ D(p): p′ᵢ ≤ pᵢ ≤ c_k(p) ≤ c_k(p′), so i ∈ D(p′).
- **Ignores p = 1:** a rejected pᵢ is at most c_k ≤ c_N < 1.
- **Self-sufficient:** let k = k(p) and q = p^{D(p)}. The k smallest values of q equal those of p, since the other values were raised to 1, and q_(j) = 1 > c_j for j > k.
  - Step-down: the conditions for i ≤ k are unchanged, and q_(k+1) = 1 fails its condition, so k(q) = k.
  - Step-up: q_(k) = p_(k) ≤ c_k, and every j > k fails, so k(q) = k.
  - Then D(q) = { i : qᵢ ≤ c_k } = D(p), since rejected values are unchanged and the others equal 1 > c_k. ∎

**Procedures outside Result 3.4.** Procedures whose rejections depend on the p-values they don't reject are still implementable by Result 2.1. The author then has to submit more than gets published, up to everything (or the raw data). Examples:
- adaptive procedures that estimate the null proportion, such as Storey-BH;
- Hommel's procedure;
- resampling procedures such as Westfall–Young or Romano–Wolf.

Two concrete failures of self-sufficiency at α = 0.1, computed with statsmodels' implementations:
- **Hommel:** p = (0.032, 0.035, 0.012, 0.411, 0.078) rejects H₁ and H₃. With the three non-rejected p-values set to 1, it rejects only H₃.
- **Storey-BH** (λ = 0.5): p = (0.116, 0.09, 0.251, 0.016, 0.046) rejects all but H₃. Setting p₃ = 1 raises the estimated null proportion from 0.4 to 0.8, and only H₄ and H₅ remain rejected.

In both cases the author must also submit some p-values that don't get published, to certify the ones that do.

**Relation to the earlier self-consistency formulation.** Self-consistent sets (pᵢ ≤ c·β(|R|) for all i ∈ R, with c = α/N) are closed under unions, because the threshold depends on the set only through |R| and doesn't decrease as |R| grows. So "publish the largest self-consistent subset of S" is the same rule as running the step-up procedure on p^S. Bonferroni on the submitted count, α/|R|, violates this, which is why it invites cherry-picking.

### 2.4 FWER version: Holm

In this version of the game, the editor's constraint is FWER ≤ α on the published set.

**Corollary (Holm).** Holm is the step-down procedure with critical values α/(N − j + 1), which are nondecreasing and at most α < 1. FWER controls V ≥ 1, so it is V-monotone. By Results 2 and 3:
- **Editor's rule:** run Holm on the submission with unreported p-values set to 1.
- **Best response:** the author submits exactly Holm's rejection set on all N p-values. That is what gets published.
- **Guarantee:** FWER ≤ α for every submission, under arbitrary dependence. Directly: before the first false rejection only non-nulls have been rejected, so that step's threshold is at most α/N₀, and a union bound over the nulls finishes.
- **Optimality:** by Result 2.3, Holm is as good in the game as it is offline. It can't be improved among monotone procedures that control FWER under arbitrary dependence ([Gordon 2011](https://doi.org/10.1016/j.stamet.2010.08.003); Gordon & Salzman 2008). It is not uniformly best: weighted or other closed-testing procedures can beat it on some data.
- **Padding is neutral:** adding k near-certain hypotheses adds k to N, but they are rejected first, so the next threshold stays at α/N.

### 2.5 FDR version: BY

In this version of the game, the editor's constraint is FDR ≤ α on the published set.

**Corollary (BY).** BY is the step-up procedure with critical values αj/(N·H_N), where H_N = 1 + 1/2 + … + 1/N ≈ log N. By Results 2 and 3:
- **Editor's rule:** run BY on the submission with unreported p-values set to 1. Equivalently, publish the largest subset of S that is self-consistent with shape r/H_N.
- **Best response:** the author submits exactly BY's rejection set on all N p-values. That is what gets published.
- **Guarantee:** FDR ≤ αN₀/N for every submission, under arbitrary dependence (Result 3.2; [Blanchard & Roquain 2008](https://arxiv.org/abs/0802.1406); [Wang & Ramdas 2022](https://sas.uwaterloo.ca/~wang/papers/2021Wang-Ramdas-JRSSB.pdf)).
- **Strategic authors cost nothing extra.** Under arbitrary dependence, the log N factor would be needed even for a non-strategic author ([Guo & Rao 2008](https://www.sciencedirect.com/science/article/abs/pii/S0378375808000165)), and BY is already valid for every submission. So guarding against strategic authors costs nothing beyond what arbitrary dependence already forces.
- **How the author can still game it: padding.** Padding changes the family of hypotheses itself, which Result 2 takes as fixed. The author can add near-certain hypotheses. This raises |R| and N and loosens every threshold α|R|/(N·H_N) ([Finner & Roters 2001](https://www.researchgate.net/publication/229892584_On_the_False_Discovery_Rate_and_Expected_Type_I_Errors)).
  - FDR ≤ α still holds, but the number of false publications can grow without bound.
  - Padding is a best response, because padded hypotheses are publications in their own right.
  - Counters: a cost per hypothesis tested, not counting trivial hypotheses as publications, or controlling a V-monotone metric (k-FWER, the expected number of false publications) instead. Holm (§2.4) is immune.

## 3. Related work

### 3.1 Kasy & Spiess, ["Optimal Pre-Analysis Plans: Statistical Decisions Subject to Implementability"](https://arxiv.org/abs/2208.09638)

**Setup.**
- **Players.** A decision-maker (a regulator, editor or policymaker) and an analyst (a drug manufacturer or researcher).
- **Data.** Statistics X = (X₁, …, Xₙ), for example treatment-effect estimates from different sites, specifications or outcomes. X | θ has a known distribution given a parameter θ.
- **Information.**
  - **Availability:** a random set J ⊆ {1, …, n} says which statistics the analyst actually obtains (for example, a site's experiment can fail). The analyst learns J; the decision-maker never does.
  - **Expertise:** before any data, the analyst sees a private signal π. It may be informative about θ ("which hypotheses are likely to be correct", effect sizes) and about J (which experiments will work).
  - **Common prior** over (π, θ, J, X), with X | θ, J, π distributed as X | θ: availability and expertise say nothing about the data beyond θ.
- **Timing (their Assumption 1).**
  1. The decision-maker picks a message space M and commits to a decision function a: (M, X_I, I) ↦ A.
  2. The analyst sees π and sends a message M ∈ M before seeing data. This message is the pre-analysis plan.
  3. The analyst sees (X_J, J) and reports a subset I ⊆ J. Reported values are truthful: hiding is allowed, lying (fraud) is not. Only the non-availability of unreported statistics is unverifiable.
  4. The decision-maker applies A = a(M, X_I, I).
- **Preferences.**
  - **Analyst (Assumptions 2–3):** expected utility v(A), strictly increasing in a real-valued decision A. In testing, A ∈ [0, 1] is the rejection probability and v(A) = A, so the analyst maximises expected power under their own beliefs, conditional on π.
  - **Decision-maker:** left unspecified for the implementability results, and not necessarily an expected-utility maximiser, so frequentist criteria are allowed. In testing it maximises expected power subject to size control (Definition 2): sup over π, null θ and J of E[ā | θ, π, J] ≤ α.
- **Why uncertainty about J matters.** If the decision-maker knew J, it could demand every statistic and take the worst action otherwise. Not knowing J gives the analyst plausible deniability, so selective reporting (p-hacking) can't be detected.

**Results.** A *reduced-form rule* ā(π, X_J, J) is the decision as a function of everything the analyst knows. It is *implementable* if some decision function a, together with the analyst's best responses (M*, I*), produces it.

- **Theorem 1 (implementability).** ā is implementable iff (up to null sets) it satisfies:
  - **Truthful message:** E[v(ā(π′, X_J, J)) | π] ≤ E[v(ā(π, X_J, J)) | π] for all π, π′;
  - **Monotonicity:** ā(π, X_I, I) ≤ ā(π, X_J, J) for all I ⊆ J; reporting more never hurts the analyst.
- **Proposition 1 (two canonical implementations).**
  - **Truthful revelation:** the message space is the set of signals, and the analyst reports π.
  - **Delegation:** the decision-maker offers a menu B of decision functions b(X_I, I), and the analyst picks one before seeing data. This is what a real pre-analysis plan looks like, and restricting to it is without loss.
- **The implementable set is a convex polytope** when A is convex, v is linear and π has finite support.
- **Proposition 2:** the truthful-message condition holds iff the analyst's payoff is a proper scoring rule of their beliefs.
- **Proposition 3:** with aligned preferences, the first-best rule is implementable even if the message is sent after the data. So pre-analysis plans matter only when there are both private information and misaligned preferences.
- **Proposition 4:** without a pre-analysis message, the implementable rules are exactly those that are monotone in the reported set and don't depend on π. The analyst's expertise is wasted.
- **Theorem 2 (optimal testing mechanism).** Let T be the class of full-data tests t: X → [0, 1] with sup over null θ of E[t(X) | θ] ≤ α. The power-maximising implementable rule with size control can be implemented as follows:
  1. The analyst pre-registers some t ∈ T.
  2. The decision-maker rejects with probability b(X_I, I) = inf{t(X′) : X′_I = X_I}.
  - **Worst-case imputation.** The unreported statistics (never obtained or hidden) are filled in with whatever values make t least likely to reject.
  - **Why it works:** b ≤ t pointwise, since the true X is one of the completions, so size control of t carries over to every J. Reporting more shrinks the set of completions, so monotonicity holds automatically. At the optimum, monotonicity binds, so worst-case imputation costs nothing.
- **The analyst's problem is a linear program** over a convex polytope B of rules. The constraints are size ≤ α with full data, values in [0, 1], and b(X_J, J) ≤ b(X, K) (monotonicity). The objective is interim expected power E_π[b(X_J, J)]. They provide an app that solves it.
  - **Proposition 5:** if J is known in advance, the optimal plan is a likelihood-ratio test on X_J: the marginal likelihood under the analyst's beliefs against the null likelihood.
  - **Proposition 6:** some optimal test is extremal in B and, if finite-valued, takes at most three values {0, q, 1}.
  - **Proposition 7:** every size-binding test that never randomises is optimal for some analyst prior.
- **Two-site example.** Xᵢ ~ N(θ, 1), H₀: θ ≤ 0, site 1 observed with probability 0.9 and site 2 with probability 0.5.
  - A naive test that treats the reported set as everything doesn't control size; with n = 10, the rejection probability under the null is close to 0.5.
  - Pre-registering the pooled test 1{(X₁ + X₂)/√2 > z} controls size but never rejects when X₂ is missing, since the worst case is X₂ → −∞.
  - Pre-registering 1{X₁ > z} is unaffected by a missing X₂, and has more power here.
  - The optimal plan with a pre-analysis message beats the best rule without one.
- **Case study.** Calibrated to DellaVigna & Pope (2018): 15 effort-incentive treatments, with priors from 208 experts' predictions.
- **Scope.** A single joint hypothesis; deciding which of multiple hypotheses to reject is left for future work.

**Connection to this work.**
- The author is the analyst, and the statistics are the N p-values. The editor knows N, so there is no deniability about how many tests exist; there is deniability about the values of unreported ones. The author also wants few submissions, so demanding a full report is costly.
- Holm with unreported p-values set to 1 is their worst-case imputation: Holm can only reject more when a p-value gets smaller, so p = 1 is the worst completion.
- Monotonicity in the reported set is why the author submits Holm's rejection set, and why the editor loses nothing by not demanding a full report.
- Our game extends their mechanism to a set-valued decision, a reward equal to the size of the published set, and an FWER or FDR constraint instead of size. Their results don't apply directly, but the same intuition drives Result 2.
- In the online version of the game ([companion note](../2026-10/online-p-value-publication-game.md)), the author's registered levels play the role of their pre-analysis message.
- Beyond their intuition, our setting adds:
  - monotonicity and self-sufficiency for set-valued decisions, which determine when the author submits only what gets published (Result 3);
  - FDR guarantees for every submission, which have no single-decision analogue (Result 3.2);
  - padding under FDR (§2.5).

### 3.2 McCloskey & Michaillat, ["Critical Values Robust to P-hacking"](https://pascalmichaillat.org/12.pdf) (REStat 2024)

**Setup.**
- **Players.** A scientist, and a journal or reader who sets the critical value z.
- **Data.** One simple null hypothesis. Experiment n yields a test statistic T_n; the statistics are iid across experiments (each experiment collects a fresh dataset of the same size from the same population). Under the null, P(T_n > z) = S(z) and F(z) = 1 − S(z).
- **Resources.**
  - Experiment n needs a random amount of resources; the cumulative requirements D₁, D₂, … form a renewal process.
  - The project has a resource limit L ~ Exponential(λ), independent of everything else.
  - The **completion probability** γ = P(D₁ < L) = E[exp(−λD₁)] is the model's only behavioural parameter. The index K of the first experiment that can't be completed is geometric: P(K > k) = γᵏ.
- **Timing.**
  1. The critical value z is set.
  2. The scientist runs experiments one by one. After each completed experiment, they either stop and submit the best statistic so far, max{T₁, …, T_n}, or run another.
  3. If resources run out mid-experiment, they must stop and submit the best statistic so far.
  4. The number of experiments is not observed by the journal or reader.
- **Preferences.**
  - **Scientist:** payoff v_s for a significant result and v_i for an insignificant one, with v_s > v_i > 0. The payoff is 0 if nothing is obtained or the scientist never stops. There is no discounting and research is costless in the baseline; the appendices show costs and discounting don't change the robust critical value.
  - **Journal:** choose z so that the probability of type I error in a reported test equals α, anticipating the scientist's stopping rule.

**Results.**
- **Lemma 1 (optimal stopping).** The scientist stops at the first significant result or when resources run out. They never stop at an insignificant result while resources remain.
- **Proposition 1.** Under the null, the stopping time N(z) is geometric, with E[N(z)] = 1/(1 − γF(z)). P-hacking is prevalent (E[N] > 1), and scientists p-hack more when z is stricter.
  - **Corollary 1:** at the classical critical value, E[N] = 1/(1 − γ(1 − α)).
- **Proposition 2.** The type I error of a reported test is S*(z) = S(z)/(1 − γF(z)) = S(z)·E[N(z)]. It grows linearly with the expected number of experiments.
  - **Corollary 2:** at the classical critical value, S* = α/(1 − γ(1 − α)) > α.
  - **Two channels:** a stricter z lowers S(z) (mechanical) but raises E[N(z)] (behavioural).
- **Robust critical value.** z* solves S(z*)/(1 − γF(z*)) = α, and z* is always above the classical value.
  - **Corollary 3:** under z*, E[N(z*)] = (1 − αγ)/(1 − γ).
  - **Corollary 4 (a non-standard Bonferroni correction):** z* is the classical critical value at level α* = α/E[N(z*)]. The count used in the correction is not observed; it is the equilibrium expected number of experiments under the null.
  - **Corollary 5:** higher γ (more resources, easier p-hacking) means a higher z*.
  - **Corollary 6:** as γ → 1, the classical type I error → 1 and z* → ∞.
- **Calibration.** Using data on the life cycle of medical studies (Dwan et al. 2008), γ = 0.8. So E[N(z*)] = (1 − 0.04)/0.2 = 4.8, and α* ≈ α/5. For a z-test at 5%, the robust critical value is 2.31 one-sided and 2.57 two-sided, instead of 1.65 and 1.96.
- **Robustness (appendices).** The robust critical value still controls type I error when p-hacking produces positively dependent statistics (pooling data, removing outliers, searching specifications), and when experiments get harder over time.

**Connection to this work.**
- It is our game with N unobserved and one hypothesis. Their N counts analyses of one hypothesis rather than distinct hypotheses, but the selection is the same: the minimum of N p-values.
- Their Corollary 6 is our Result 1. When resources are unlimited (γ → 1), no finite critical value works. They escape it because resources bound N: they give up the worst case over N and divide α by the equilibrium expected N.
- The costs: the guarantee holds on average across researchers, not for each author; it relies on a calibrated γ; and researchers with unusually deep resources (high γ) break it. Their own Corollary 5 says critical values should rise with a team's resources.
- The online version of the game ([companion note](../2026-10/online-p-value-publication-game.md)) is another way out of Result 1: registering each test makes the count observable, and a budget plus a per-test cost bound how many tests the author runs, with a guarantee for each author rather than an average one.

### 3.3 Bates, Jordan, Sklar & Soloff, ["Principal-Agent Hypothesis Testing"](https://arxiv.org/abs/2205.06812)

**Setup.**
- **Players.** A principal (a regulator such as the FDA) and an agent (a drug company).
- **Types.** The agent knows a quality parameter θ ∈ Θ = Θ₀ ∪ Θ₁ (null and non-null). The principal doesn't know θ and has no prior over it.
- **Timing (a statistical contract).**
  1. The principal offers a menu F of license functions.
  2. The agent decides whether to opt in (I ∈ {0, 1}). If it opts in:
     - it chooses a license function f ∈ F;
     - it pays a cost C to run a trial;
     - it observes evidence Z ~ P_θ;
     - it receives a license to make profit at most L = f(Z).
- **Preferences.**
  - **Agent:** maximises expected profit E_θ[f(Z)] − C, and opts out if no f has positive expected profit. With a concave utility of profit, Jensen's inequality makes the linear case the conservative one.
  - **Principal:** utility u(θ, L), with u ≥ 0 and nondecreasing in L for non-nulls, u ≤ 0 and nonincreasing in L for nulls, and u = 0 if the agent opts out. Expected utility is E_{θ~Q}[E[u(θ, L)·I]] for a distribution Q of agent types.
  - **The principal is maximin:** it picks F to maximise the worst case over Q, rather than a Bayesian Stackelberg equilibrium under a known prior.

**Results.**
- **Motivating example.** A $10 million trial has 5% type I error and 80% power.
  - If approval pays $100 million (10× the cost), a null agent's expected profit from a trial is −$5 million, so it stays out and every approved drug is effective.
  - At $1 billion (100×), the null agent's expected profit is +$40 million, so it runs the trial. If ineffective drugs outnumber effective ones 20 to 1, 56% of approved drugs are ineffective. Looser standards attract more trials of less promising candidates.
- **Definition 1 (incentive-aligned contract):** E_θ[f(Z)] ≤ C for every null θ and every f ∈ F. No null agent profits, so bluffing is deterred.
- **Proposition 1:** F is incentive-aligned iff F/C ⊂ E, the set of e-values (non-negative, with null expectation ≤ 1). Payoff functions that deter bluffing correspond exactly to e-values.
- **Theorem 1:** a menu is maximin optimal iff it is incentive-aligned.
  - **Proposition 2** gives the intuition: as the fraction of nulls π₀ → 1, only incentive-aligned menus avoid negative utility.
- **Theorem 2:** if the principal's utility is affine in L for non-nulls, the menu of all rescaled e-values, F = C·E, is optimal among incentive-aligned menus for every Q.
  - **Proposition 3:** even without linearity, this largest menu maximises participation and the expected profit cap.
- **Proposition 4 (the agent's best response).** With a simple null θ₀ and a profit cap R > C, the agent's optimal license is R·1{dP_θ₁/dP_θ₀(Z) > λ}. That is a Neyman–Pearson likelihood-ratio test with type I error C/R. The cost-to-profit ratio sets the effective significance level.
- **Status-quo comparison.** A license R·1{p < 0.05} is incentive-aligned only when C/R > 0.05, i.e. when profit is less than 20× the trial cost.
- **Multi-round contracts (their Appendix B).** The agent invests over T rounds and evidence accumulates. The contract is incentive-aligned iff each round's menu consists of e-values (Proposition 5); the proof shows a null agent's net profit is a supermartingale. Maximin and optimal-menu results parallel Theorems 1–2 (Theorem 3, Proposition 6).
- **FDA analysis.** Three simplified protocols:
  - **Standard:** two trials, each significant at one-sided 0.025. A placebo is approved with probability 0.025² = 0.000625.
  - **Modernized:** placebo approval probability 0.005.
  - **High-discretion accelerated:** approval if either of two trials has a two-sided p < 0.05. A placebo is approved with probability 0.0494.

  Comparing these probabilities with the profit-to-cost ratios of drug categories, some pathways are exploitable for high-profit drugs.

**Connection to this work.**
- It is the participation decision for each hypothesis when testing is costly. Their agent pays C for a trial given private beliefs; an author who pays c to test each hypothesis faces the same choice for every hypothesis (§4.2, direction 2).
- Incentive alignment becomes R·P_null(published) ≤ c for each hypothesis. Under Holm with N observed, P_null(published) ≤ α/N, so testing a believed-null hypothesis is unprofitable once α/N ≤ c/R. By their Proposition 4, c/R is the level a profit-capped agent's own likelihood-ratio test would use.
- The online version of the game develops this connection further, including the parallel between their multi-round contracts and alpha-investing ([companion note](../2026-10/online-p-value-publication-game.md)).
- Differences: they have one test per agent and a maximin guarantee over the population of agents; we have many hypotheses per author and a frequentist guarantee for each author.

### 3.4 Hossain, Chen & Chen, ["Strategic Hypothesis Testing"](https://arxiv.org/abs/2508.03289)

**Setup.**
- **Players.** A principal (a regulator such as the FDA) and agents (firms).
- **Data.** Each product has effectiveness μ₀ = E[X], where the outcome X is Bernoulli. μ₀ is private to the agent, but its distribution q is public. H₀: μ₀ ≤ μ_b against a known baseline μ_b.
- **Timing (Bayesian Stackelberg; their Definition 2.3).**
  1. The principal commits to a p-value threshold α.
  2. Each agent chooses a sample size n ∈ {0} ∪ [n_min, n_max], where n = 0 means not participating.
  3. The agent submits Xₙ, and the product is approved if its p-value (via a normal approximation to the binomial) is at most α.
- **Preferences.**
  - **Agent (Definition 2.2):** u(α, μ₀, n) = R·Pass(α, μ₀, n) − 1{n ≠ 0}(c₀ + c·n), with revenue R if approved, fixed cost c₀ and per-sample cost c. It participates iff its best utility is ≥ 0.
  - **Principal:** minimises L(α) = λ_fp·E[Pass | μ₀ < μ_b] + λ_fn·E[Fail | μ₀ ≥ μ_b] (false positives plus false negatives), with expectations over q under the agents' best responses. The Stackelberg equilibrium is α* = argmin L(α).

**Results.**
- **Theorem 3.1:** an agent's best response is computable in O(log n_max) time. An ineffective agent (μ₀ < μ_b) that participates uses n_min.
- **Lemma 3.1 (monotone participation):** if an agent with effectiveness μ₀ participates, so does every agent with higher effectiveness. So there is a participation threshold μ_τ(α).
- **Lemma 3.2:** μ_τ(α) decreases in α (easier tests draw in weaker products), and can be computed efficiently.
- **Lemma 3.3:** the agent's optimal utility increases in μ₀.
- **Definition 4.1 (critical threshold α̂):** the α at which μ_τ(α̂) = μ_b, so that exactly the effective agents participate. It doesn't depend on q or on λ_fp, λ_fn.
- **Lemma 4.1:** for effective agents, the pass probability is non-decreasing in α even after they re-optimise n. The introduction raises the possibility that a looser α could lower passing by inducing smaller trials; this lemma rules it out for effective agents.
- **Theorem 4.1:** false positives are 0 for α < α̂ (only effective agents take part) and non-decreasing for α ≥ α̂.
- **Proposition 4.1:** false negatives from abstention are non-increasing in α and 0 for α ≥ α̂.
- **Proposition 4.2:** false negatives among participants are non-increasing for α ≥ α̂. Below α̂ they can be non-monotone (their §5.1): a looser α draws in marginally effective agents who then fail often.
- **Theorem 4.2:** total false negatives are non-increasing in α on each side of α̂.
- **Theorem 4.3:** α* ≥ α̂, and α̂ can be computed to ε accuracy in O(log²(1/ε)·log n_max). When false positives are very costly, α* is close to α̂.
- **Drug-approval case study.** Costs and revenues are calibrated for oncology, cardiovascular drugs and vaccines.
  - At median revenue, α = 0.05 is about the ideal threshold.
  - For oncology drugs with revenue around $5 billion, α̂ is between 0.1 and 0.2.
  - Standards stricter than α̂ deter effective but low-margin products, such as orphan drugs.

**Connection to this work.**
- Their sample-size choice is the analogue of the author's choice of how many hypotheses to test when testing is costly (§4.2, direction 2): how much evidence to generate at a cost.
- Their critical threshold α̂ is the analogue of choosing α so that testing a believed-null hypothesis is unprofitable exactly at the margin the editor wants. Their non-monotonicity below α̂ warns that an editor tuning α for welfare should expect non-monotone effects on discoveries.
- A natural editor objective in their style is expected true discoveries minus c·N, subject to FWER. The online version of the game ([companion note](../2026-10/online-p-value-publication-game.md)) makes N the author's choice and develops these analogies.
- Differences: they control a Bayes-weighted Type I/II loss over a population of single-product agents with a known prior q; we have many hypotheses per author and a frequentist guarantee for each author.

### 3.5 Other related work

**Offline multiple testing results used in §2.**
- **Gordon & Salzman (2008), "Optimality of the Holm procedure among general step-down multiple testing procedures"; [Gordon (2011), "A new optimality property of the Holm step-down procedure"](https://doi.org/10.1016/j.stamet.2010.08.003).**
  Call a procedure *monotone* if lowering p-values can only add rejections. Gordon & Salzman show that among monotone step-down procedures that control FWER at level α under arbitrary dependence, Holm dominates: whenever such a procedure rejects a hypothesis, Holm does too. Gordon (2011) extends this to all monotone procedures: Holm can't be improved without losing FWER control. Because the editor's optimum in the game equals the offline optimum (Result 2.3), these results carry over directly: among monotone rules, no publication rule beats Holm in the FWER game (§2.4). The same monotonicity is what makes "unreported p-values set to 1" the editor's worst case (Result 3.3).
- **[Blanchard & Roquain (2008), "Two simple sufficient conditions for FDR control"](https://arxiv.org/abs/0802.1406).**
  They show that FDR ≤ α·π(H₀) follows from two conditions (Proposition 2.7). *Self-consistency* is a condition on the procedure alone: every rejected pᵢ ≤ α·β(|R|)/m. *Dependency control* links each null p-value to |R|. Dependency control holds for step-up procedures with linear shape under independence or PRDS. Under arbitrary dependence it holds for *any* procedure, with no restriction on how R is chosen, when the shape is β(r) = ∫₀ʳ x dν(x) for a probability measure ν (Proposition 3.7); taking ν ∝ 1/k gives Benjamini–Yekutieli. Proposition 3.7 is the engine of our Result 3.2: since it covers every self-consistent set, however chosen, the BY guarantee survives authors who submit something other than their best response. Self-consistent sets are also closed under unions, which gives the "largest self-consistent subset" form of the editor's rule (§2.3). The framework also covers weighted FDR, p-value weights and adaptive step-up procedures.
- **[Guo & Rao (2008), "On control of the false discovery rate under no assumption of dependency"](https://www.sciencedirect.com/science/article/abs/pii/S0378375808000165)** (JSPI 138:3176–3188).
  They show that BY's critical values can't be enlarged without losing FDR control under arbitrary dependence, because some joint distribution of p-values attains the bound. That is why the log N factor in the FDR game (§2.5) would be needed even for a non-strategic author, so guarding against strategic authors costs nothing beyond it. They also propose a step-down procedure that uses BH's critical constants and has a much smaller FDR bound than BY's.
- **[Wang & Ramdas (2022), "False discovery rate control with e-values"](https://sas.uwaterloo.ca/~wang/papers/2021Wang-Ramdas-JRSSB.pdf)** (JRSSB 84:822–852).
  e-BH rejects the k largest e-values, where k is the largest index such that the k-th largest e-value is at least N/(αk). It controls FDR at α·N₀/N under arbitrary dependence, with no log factor. More strongly, their Proposition 2 says any self-consistent e-procedure (every rejected eᵢ ≥ N/(α|R|)) controls FDR under arbitrary dependence, and e-BH dominates them all. This makes e-BH the e-value analogue of our Result 3.2 without the log N penalty; proving the e-BH version of Result 3 is listed in §4.1. In the game the e-values would have to be pre-registered, since choosing the e-value after the data is selection again. Wang & Ramdas also show that applying e-BH to p-values transformed by calibrators recovers BH and BY (BY is e-BH with a step calibrator). By contrast, self-consistent p-procedures under PRDS-type conditions get only the weaker bound α(1 + log(1/α)) (they cite Su 2018).
- **[Lehmann & Romano (2005), "Generalizations of the familywise error rate"](https://projecteuclid.org/euclid.aos/1120224098)** (Ann. Statist. 33:1138–1154).
  They control the k-FWER, P(at least k false rejections) ≤ α, under arbitrary dependence. They give a single-step procedure that rejects pᵢ ≤ kα/N, and a step-down procedure generalising Holm, with critical values kα/N for i < k and kα/(N + k − i) for i ≥ k. They prove the step-down procedure can't be improved without losing k-FWER control, and also give procedures controlling the false-discovery proportion. Since k-FWER is V-monotone and the step-down critical values are nondecreasing with last value α < 1, our Result 3 applies verbatim. In a k-FWER version of the game, the editor runs Lehmann–Romano with unreported p-values set to 1, the author submits exactly its rejection set, and the guarantee holds for every submission. Unlike FDR, k-FWER bounds the number of false publications, so it resists padding (§2.5).
- **[Finner & Roters (2001), "On the false discovery rate and expected type I errors"](https://www.researchgate.net/publication/229892584_On_the_False_Discovery_Rate_and_Expected_Type_I_Errors)** (Biometrical Journal 43:985–1005).
  Their discussion of undesirable properties of FDR, notably "cheating", is the padding problem of our FDR game (§2.5). Adding a hypothesis known to be rejected with probability near 1 lets the hypothesis of interest be tested at about level 2α. More generally, the expected number of type I errors can grow while FDR stays controlled. The game sharpens their point: padding becomes a best response, because padded hypotheses are publications in their own right.

**Other.**
- **[Bogomolov & Heller (2013), "Discovering findings that replicate from a primary study of high dimension to a follow-up study"](https://www.tandfonline.com/doi/abs/10.1080/01621459.2013.829002)** (JASA 108:1480–1492).
  A primary study screens many hypotheses and selects some for a follow-up study. They give procedures controlling the FWER, and more powerful ones controlling the FDR, of replicability claims (findings significant in both studies). These are valid under arbitrary dependence within each study, and they show standard meta-analysis is inappropriate. Their design is another way to remove selection after the data without knowing N. Selection happens in the primary study, and the follow-up family is just the selected set, tested on fresh data, with the procedure accounting for the selection. It suggests a version of our game in which the editor publishes only replicated findings.
- **[Viviano, Wüthrich & Niehaus, "A model of multiple hypothesis testing"](https://arxiv.org/abs/2104.13367).**
  Their economic model of a researcher and a planner, aimed at settings such as regulatory approval of clinical trials, derives the *amount* of multiple-testing correction from incentives and costs. We instead take the error guarantee as given and derive the editor's rule and the author's best response. Corrections are warranted to the extent that research costs don't scale with the number of hypotheses: controlling average size, as with Bonferroni, emerges when all costs are fixed, and no correction is needed when costs are proportional to the number of hypotheses. Calibrating to drug-approval and program-evaluation costs, they find some adjustment is warranted, but less than standard practice. When testing costs c per hypothesis (§4.2, direction 2, and the [companion note](../2026-10/online-p-value-publication-game.md)), c plays a role like their costs: it, not the editor, determines how many hypotheses get tested.

## 4. Open directions and unresolved questions

### 4.1 Unproven claims (sketches to turn into proofs)

1. Result 3.2 for other procedures valid for every self-consistent subset: Blanchard–Roquain step-up procedures with other shape functions, and e-BH. The proof should go through as for BY.

### 4.2 Other directions

Statements marked *(computed)* come from our own numerical calculations and *(sketch)* from arguments not yet written as proofs; everything else is from the cited papers.

1. **Self-consistent e-BH as the editor's FDR rule.**
   - *Why:* under arbitrary dependence, BY (§2.5) pays a log N factor (H_N ≈ log N in its thresholds αk/(N·H_N)). That factor would be needed even for a non-strategic author ([Guo & Rao 2008](https://www.sciencedirect.com/science/article/abs/pii/S0378375808000165)). e-BH avoids it. [Wang & Ramdas 2022](https://sas.uwaterloo.ca/~wang/papers/2021Wang-Ramdas-JRSSB.pdf), Proposition 2: *any* self-consistent set of e-values (every rejected eᵢ ≥ N/(α|R|)) has FDR ≤ α·N₀/N under arbitrary dependence, however the set was chosen. So the e-BH analogue of Result 3.2, a guarantee for every submission, should come almost for free.
   - *Large-N publication rates (computed).* Large-N population fixed-point calculations, with fraction π₁ = 0.1 of non-nulls, one-sided Gaussian signals of mean μ and α = 0.1. Fraction of hypotheses published:
     - **μ = 3.5:** BY falls from 0.065 (N = 10³) to 0.047 (N = 10¹²). Likelihood-ratio e-BH (e = exp(μX − μ²/2) with the true μ) stays at 0.062 for every N. BH, not valid under arbitrary dependence, gives 0.096.
     - **μ = 2.5:** likelihood-ratio e-BH publishes nothing, while BY publishes 0.015 to 0.005. e-values carry less evidence than 1/p at moderate signals.
     - **Analytic picture:** with a fixed fraction of non-nulls, BY publishes only N^(1−o(1)), because its threshold t solves G(t)/t ≈ log N/(απ₁), where G is the non-null p-value CDF. BH and e-BH publish Θ(N).
     - **A Blanchard–Roquain shape between the two:** ν ∝ 1/k on [cN, N], so β(r) ≈ (r − cN)/log(1/c). It is valid for every submission under arbitrary dependence, has penalty log(1/c) instead of log N, and gives Θ(N) publications (0.016 at μ = 2.5 and 0.067 at μ = 3.5 with c = 0.002; computed). But it has a cliff: if fewer than about cN findings exist, almost nothing is published.
   - *Strategic issue:* each e-value must be fixed before the data. Choosing e = exp(λX − λ²/2) with λ picked after seeing X is selection again. So the game needs pre-registered e-values, i.e. pre-registered alternatives, or mixture e-values that don't require a chosen alternative. Pre-registering the alternative is a Kasy–Spiess-style pre-analysis message (§3.1) carrying the author's private beliefs about effect sizes.
   - *Questions:*
     - Prove the e-BH version of Results 2 and 3: the worst-case rule, what the author submits, and the guarantee for every submission. For e-values the worst completion of an unreported value is e = 0, not p = 1.
     - Characterise the author's optimal pre-registered alternatives, and whether the author's incentives align with the editor's (power) objective.
     - Compare the power of e-BH with BY and with the windowed shape as a function of μ, π₁ and N. Where is the crossover?
     - Do mixture e-values close the gap at moderate signals?
   - *Calibration facts:* applying e-BH to p-values transformed by calibrators recovers BH and BY (Wang–Ramdas; BY is e-BH with a step calibrator). So p-value self-consistency rules are special cases rather than competitors, and the only gain comes from native e-values.

2. **Endogenous N: the author chooses how many hypotheses to test.**
   - *Online.* The online version, where N is the author's choice under a budget rule, is developed in the [companion note](../2026-10/online-p-value-publication-game.md), with its own open questions.
   - *Offline, with N observed (sketch).* Under Bonferroni with homogeneous hypotheses, expected publications are about N·π₁·G(α/N). The marginal value of one more hypothesis is G(t) − t·G′(t) with t = α/N, which is ≥ 0 when G is concave.
     - A hypothesis the author believes null is doubly bad: it pays only R·α/(N + 1) and tightens every other threshold. So under FWER, testing extra hypotheses limits itself.
     - In the language of [Bates, Jordan, Sklar & Soloff](https://arxiv.org/abs/2205.06812) (§3.3), testing believed-null hypotheses is unprofitable once α/N ≤ c/R. By their Proposition 4, c/R is exactly the type I level that a profit-capped agent's own likelihood-ratio test would use.
     - Three reward designs to compare:
       - a flat reward R per publication;
       - a reward scaled by the evidence, as in Bates et al., where license functions divided by the cost must be e-values;
       - a reward paid only for findings that replicate, which pays only for true discoveries and removes the payoff from padding.
   - *Offline, with N not registrable (sketch).* For example, exploratory analyses of an existing dataset. Mechanism:
     - The author declares N̂ and the editor applies Holm with α/(N̂ − j + 1).
     - With probability q the editor audits (registry entries, lab notebooks, code repositories, data-access logs). If the audit finds N > N̂, the author pays a penalty P (retraction, ban, loss of the publications).
     - **Incentive condition:** q·P ≥ R × (extra publications from understating). Declaring N/k multiplies the early thresholds by about k.
     - **Complications:**
       - If N̂ is declared after seeing the p-values, the condition must hold realisation by realisation. An author who found p = 10⁻⁴ among 10,000 tests gains a lot by declaring N̂ = 10.
       - Penalties are capped (limited liability), so q must be large.
       - Audits are imperfect and typically find only a lower bound on N.
     - **If the condition fails,** shade the thresholds by the expected understatement. That gives only an average guarantee, as in [McCloskey & Michaillat](https://pascalmichaillat.org/12.pdf) (§3.2), who divide α by the equilibrium expected number of attempts (about α/5 in medical science).
     - **Literature:** this is costly state verification ([Townsend 1979](https://ideas.repec.org/a/eee/jetheo/v21y1979i2p265-293.html); [Ben-Porath, Dekel & Lipman 2014](https://www.aeaweb.org/articles?id=10.1257%2Faer.104.12.3779) study verification without transfers, a loose fit since they allocate a single object).
     - *Question:* the optimal (q, P, shading) design, and how much of the guarantee for each author survives.

3. **Padding-proof FDR.**
   - *Problem:* under FDR rules the author can add near-certain hypotheses ("gravity does not exist"). These raise |R| and N and loosen every threshold α|R|/(N·H_N). FDR ≤ α still holds, but the number of false publications can grow without bound ([Finner & Roters 2001](https://www.researchgate.net/publication/229892584_On_the_False_Discovery_Rate_and_Expected_Type_I_Errors); §2.5).
     - In the game padding is a best response, because padded hypotheses are publications in their own right.
     - Online, alpha-investing rewards padding even more: expected false publications are unbounded under mFDR control, and padding first is subgame perfect ([companion note](../2026-10/online-p-value-publication-game.md), Result 3).
     - Holm is immune: padding is neutral under it (§2.4).
   - *Candidate fixes to analyse:*
     - **Error metrics that count false publications** (V-monotone metrics, §2.3): E[V], or k-FWER with k growing in N. Result 3 already covers these, with Lehmann–Romano step-down (critical values kα/N for i < k, then kα/(N + k − i)) as the k-FWER equilibrium.
     - **FDR-type criteria that discount near-certain rejections,** e.g. weighting rejections by how surprising they were, or counting only hypotheses with registered prior probability below a cap.
     - **Reward schemes:** a per-hypothesis cost c with R ≤ c for trivial hypotheses, payouts withheld for findings that aren't novel (hard: the editor can't verify novelty), or rewards only for replicated findings.
   - *Questions:*
     - Is there a criterion that is as powerful as FDR when there is no padding, but under which padding is not a best response?
     - For E[V] control, which procedure is the offline optimum under arbitrary dependence, so that Result 2.3 transfers it to the game?

4. **Authors with goals other than publication count.**
   - *Setting:* §2 assumes the author maximises the number of publications, then minimises submissions. Real authors may prefer particular results: their own pet hypothesis, results with a given sign, or results with larger effects.
   - *What survives:* the guarantees in Result 3.1 (metrics that count false rejections) and Result 3.2 (BY) hold for *every* submission S. So the editor's error control survives any author preferences.
   - *What changes:*
     - **What gets published and how much:** an author who prefers some results may submit a strict subset of the worst-case rule's rejection set.
     - **Validity of equilibrium-only rules:** under independence, BH at level α controls FDR only at the publication-maximising best response. For arbitrary self-consistent subsets the bound degrades to α(1 + log(1/α)) (Su 2018, as reported by Wang–Ramdas).
   - *Questions:*
     - Model author preferences, e.g. a weight vector over hypotheses or a utility from specific results.
     - Characterise the author's best response under Holm and under BY, and the distribution of what gets published.
     - Can a non-publication-maximising author make the editor's *power* objective worse than under the publication-maximising benchmark, and by how much?
     - Do we ever need guarantees for every submission beyond Result 3? For example, FDR rules that aren't self-consistent in the Blanchard–Roquain sense.

5. **Signal scaling beyond the two-group model.** Replace the Donoho–Jin null/alternative mixture with a Gaussian prior on effect sizes and sign-error criteria. This is developed in a [companion note](../2026-10/strategic-z-value-publication-game.md): publication rates of order N^s, with s the share of z's variance that is signal, and a Bayesian editor who needs neither N nor a full report.

### 4.3 Unresolved questions

- How should the editor learn N in fields without registries, and how much of the guarantee survives audits that are imperfect or only partially enforced?
- Is there a natural error criterion between FWER (immune to padding but conservative) and FDR (powerful but open to padding)? The expected number of false publications and k-FWER with k growing in N are candidates.
- The equilibrium is ex post but the author's hypothesis choice is ex ante. How should selection before the data (which hypotheses to test) interact with the editor's guarantee?
