---
title: Strategic p-value publication game
description: Editor–author game over which p-values to publish under FWER or FDR control; equilibria, literature, and large-N variants
date: 2026-09-29
---

## The game

- An editor commits to a publication rule. Then an author, who holds a large collection of N p-values, chooses which ones to submit.
- Both want as many publications as possible. The author also wants as few submissions as possible, and the editor must keep an error rate controlled on what gets published.
- Main lesson: the editor must condition on N, the total number of tests the author ran. Rules based on the submitted count can be gamed by cherry-picking. For example, with Bonferroni at α/n the author submits only the smallest p-value, and FWER goes to 1 as N grows. If N is unknown and can be arbitrarily large, the only rule that controls FWER is to publish nothing.

## FWER: Holm is the equilibrium

- Editor's rule: step-down Holm thresholds α/(N−j+1) applied to the sorted submitted p-values, which is the same as treating unreported p-values as 1.
- This controls FWER for any submission. Before the first false rejection only non-nulls have been rejected, so the threshold at that step is at most α/N₀, and a union bound finishes the proof.
- Author's best response: submit exactly the set Holm would reject on the full collection. No subset does better, because order statistics of a subset are no smaller than those of the full set.
- Holm can't be improved among procedures where smaller p-values only add rejections, valid under arbitrary dependence ([Gordon 2011](https://doi.org/10.1016/j.stamet.2010.08.003)). This is not a claim that Holm is uniformly best.

## Novelty and related work

- The result is probably not new. It follows from [Kasy & Spiess](https://arxiv.org/abs/2208.09638): an analyst can hide results but not lie; a rule can be implemented only if reporting more never hurts the analyst; the optimal rule pre-registers a full-data test and treats unreported statistics as worst case.
- Kasy–Spiess cover only a single joint decision. They leave multiple decisions to future work, so extending their framework to multiple hypotheses under FWER/FDR is an open direction.
- Kasy–Spiess is about selective reporting after the data are in. Bates, Jordan, Sklar & Soloff and [Hossain et al., arXiv 2508.03289](https://arxiv.org/abs/2508.03289) are about deciding whether to run a trial and how large to make it before the data: adverse selection, not cherry-picking.
- [McCloskey & Michaillat](https://arxiv.org/abs/2005.04141) derive critical values robust to p-hacking for a single test (a Bonferroni-type correction). [Viviano, Wüthrich & Niehaus](https://arxiv.org/abs/2104.13367) derive multiple-testing corrections from research costs.

## Making the large-N limit allow publications

- Change the error criterion:
  - FDR, via self-consistent sets or e-BH.
  - k-FWER: Lehmann–Romano thresholds of order kα/N.
  - An equilibrium-only guarantee instead of one that holds for every author strategy.
- Remove selection after the data:
  - Pre-registered weights with weighted Holm. The author has an incentive to put weight on hypotheses they believe are true.
  - Registered reports.
  - A two-stage design where screened hypotheses are retested on fresh data ([Bogomolov & Heller 2013](https://www.tandfonline.com/doi/abs/10.1080/01621459.2013.829002)).
  - Online testing: alpha-investing, LORD.
- Make N the author's choice: a per-hypothesis cost, or audits of the reported count (costly verification, [Ben-Porath, Dekel & Lipman 2014](https://www.aeaweb.org/articles?id=10.1257%2Faer.104.12.3779), a loose fit).
- Scale the signal with N, as in [Donoho–Jin](https://arxiv.org/abs/math/0410072): signals of size √(2r log N) at sparsity N^(−β). Holm-in-equilibrium publishes about N^(1−β−(1−√r)²) results, which grows iff r > (1−√(1−β))².

## FDR version

- Self-consistency: every published p_i ≤ c·β(|R|) for a nondecreasing shape function β.
  - Self-consistent sets are closed under unions, because the threshold depends only on |R| and doesn't decrease as |R| grows. So each collection has a unique largest self-consistent set, which is exactly the step-up rejection set.
  - Bonferroni on the submitted count, α/|R|, fails union-closure, which is why it invites cherry-picking.
- Equilibrium: the editor publishes the largest self-consistent subset of the submission, with thresholds fixed by N. The author submits exactly the step-up set: BY when β(r) = r/H_N, BH when β(r) = r.
- Guarantees ([Blanchard & Roquain 2008](https://arxiv.org/abs/0802.1406), Props 2.7 and 3.7; [Wang & Ramdas 2022](https://sas.uwaterloo.ca/~wang/papers/2021Wang-Ramdas-JRSSB.pdf)):

  | Dependence | Equilibrium-only guarantee | Guarantee for every author strategy |
  |---|---|---|
  | PRDS / independence | BH at α | BH at α′, where α′(1+log(1/α′)) = α ([Su 2018](https://arxiv.org/abs/1812.08965)) |
  | Arbitrary | BY | BY (Blanchard–Roquain 3.7 holds for any R) |

  - BY's constants can't be enlarged under arbitrary dependence ([Guo & Rao 2008](https://www.sciencedirect.com/science/article/abs/pii/S0378375808000165)). So the log N factor is the price of arbitrary dependence, not of strategic authors.
- Publication rates with a fixed fraction of non-nulls:
  - BH publishes Θ(N).
  - BY publishes only N^(1−o(1)), because its threshold goes to 0 like the solution of G(t)/t ≈ log N/(απ₁), where G is the non-null p-value CDF.
  - Fix: a Blanchard–Roquain shape function with ν ∝ 1/k on [cN, N]. The penalty becomes log(1/c) instead of log N, publications are Θ(N), and the rule stays valid for every strategy under arbitrary dependence. The risk is a cliff: if fewer than about cN findings exist, almost nothing publishes.
- e-BH: publish R if every e_i ≥ N/(α|R|). This is valid for every strategy under arbitrary dependence with no log factor.
  - With e-values converted from p-values, e-BH includes the self-consistency rules rather than beating them (Wang–Ramdas Remark 4; BY is e-BH with a step calibrator).
  - Native likelihood-ratio e-values give publication rates that don't depend on N, but they lose power at moderate signal strengths.
  - The e-value must be pre-registered, which fits naturally with pre-analysis plans.
- Numerical example: large-N population fixed-point calculations with α = 0.1, π₁ = 0.1 and Gaussian signals, in terms of the fraction of hypotheses published. At μ = 3.5, BH gives 0.096 and BY falls from 0.065 (N = 10³) to 0.047 (N = 10¹²). The windowed shape gives 0.067 and likelihood-ratio e-BH gives 0.062, both independent of N. At μ = 2.5, likelihood-ratio e-BH publishes nothing.

## Caveats and open questions

- All guarantees need three things: N fixed in advance and covering every test run; each p-value valid on its own, with one pre-specified analysis per hypothesis; and the family not chosen after seeing results.
- Padding ([Finner & Roters 2001](https://www.researchgate.net/publication/229892584_On_the_False_Discovery_Rate_and_Expected_Type_I_Errors)): the author can add near-certain hypotheses. This raises |R| and N and loosens the thresholds. FDR ≤ α still holds, but the number of false publications can grow without bound, and padding is a best response.
  - Counters: a cost per hypothesis tested, not counting trivial hypotheses as publications, or controlling k-FWER or the expected number of false publications instead.
- Still unproven sketches:
  - The equilibrium argument with union-closure.
  - Whether pre-registered weights reveal the author's beliefs truthfully.
  - The publication-rate exponent for Holm under Donoho–Jin scaling.
- Promising directions:
  1. Extend Kasy–Spiess to multiple decisions (weighted Holm with pre-registered weights).
  2. Self-consistent e-BH.
  3. Let the author choose N at a cost.
