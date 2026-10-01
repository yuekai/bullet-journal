---
title: Strategic z-value publication game
description: Editor–author publication game without exact nulls; Gaussian prior on effect sizes, sign-error criteria, publication rates of order N^s with s the signal share, and a Bayesian editor that needs neither N nor a full report
date: 2026-10-01
---

This note is a companion to the [basic-game note](../2026-09/strategic-p-value-publication-game.md). There, an editor commits to a publication rule, an author holding N p-values chooses which to submit, and once N is known the game reduces to offline multiple testing (its Results 2–3), with Holm as the FWER equilibrium and BY as the FDR equilibrium.

The basic-game note's large-N analysis used the two-group model of Donoho & Jin: exact nulls plus N^(1−β) signals of size √(2r log N). Under it, Holm publishes about N^(1−β−(1−√r)²) results (sketch), with a phase transition at r = (1 − √(1−β))². Here we drop exact nulls and put a prior on effect sizes, so most effects are small but none is exactly zero.

Statements marked *(computed)* come from our numerical integrals of the formulas below; *(sketch)* marks arguments not yet written as full proofs.

## 1. Setup

### 1.1 The model

- **Effects and data.** Each hypothesis has an effect θᵢ ~ N(0, τ²), and the author observes zᵢ | θᵢ ~ N(θᵢ, 1), independently across i.
- **Signal share.** Let s = τ²/(1 + τ²), the fraction of z's variance that is signal. Then:
  - marginally, zᵢ ~ N(0, σ²) with σ² = 1 + τ²;
  - given zᵢ, θᵢ ~ N(s·zᵢ, s).
- **The game.** As in the basic-game note: the editor commits to a publication rule, the author sees all N z-values and submits a subset, and the editor publishes part of it. The author maximises publications, then minimises submissions. A publication is now a *signed* claim: "θᵢ > 0" or "θᵢ < 0".

### 1.2 What counts as an error

Every point null θᵢ = 0 is false with probability 1, so FWER and FDR against point nulls are vacuous. Two replacements:
- **Sign errors.** Publishing "θᵢ > 0" when θᵢ < 0, or the reverse. This is the Type S error of Gelman & Tuerlinckx. The *local false sign rate* of Stephens, lfsrᵢ = P(sign of θᵢ is wrong | zᵢ), is its Bayesian per-hypothesis version.
- **Interval nulls.** Hᵢ: |θᵢ| ≤ δ for a smallest effect size of interest. This brings back a two-group structure, with null proportion π₀ = P(|θ| ≤ δ) determined by the prior rather than assumed.

We use sign errors. The frequentist criterion is the probability of *any* sign error among the published claims (a directional FWER). The Bayesian criterion bounds each published claim's lfsr.

## 2. Results

### 2.1 Frequentist sign-error control

**Rule.** Publish sign(zᵢ) whenever |zᵢ| > t_N = Φ̄⁻¹(α/2N), where Φ̄ is the standard normal upper tail.

**Validity for every θ.** A sign error on hypothesis i needs zᵢ to land more than t_N on the wrong side of 0. Since zᵢ ~ N(θᵢ, 1), that has probability at most Φ̄(t_N) = α/2N whatever θᵢ is. A union bound over the N hypotheses bounds the probability of any sign error by α/2 ≤ α. No prior is needed, and the bound holds under arbitrary dependence between the zᵢ.

**Strategic results carry over.** The rule is a single-step procedure with a fixed threshold, and the number of sign errors is the metric's only input. So it is a V-monotone metric in the sense of the basic-game note, and its Results 2 and 3 apply: the editor publishes the submitted hypotheses with |zᵢ| > t_N (unreported values treated as 0); the author submits exactly those; and the guarantee holds for every submission.

**Publication rate.** Expected publications are 2N·Φ̄(t_N/σ). Since t_N ≈ √(2 log N), this is about

  N^s / √(log N).

So the Gaussian prior scales the signal with N automatically. There is no phase transition: any τ > 0 gives polynomial growth, with exponent equal to the signal share s. *(Sketch: the exponent follows from Φ̄(x) ≈ φ(x)/x with x = t_N/σ.)*

### 2.2 Why √(2 log N) is still the right threshold

The joint density of "observe z and have the sign wrong" is Φ(−√s·|z|)·φ(z/σ)/σ. Using Φ(−x) ≈ φ(x)/x, its exponent is

  −z²·(s + 1/σ²)/2 = −z²/2, because s + 1/σ² = τ²/σ² + 1/σ² = 1.

So at large |z|, wrong-sign hypotheses have exactly standard-normal tails, the same as exact nulls would. Any rule that bounds the *number* of sign errors must therefore threshold near √(2 log N). This includes a Bayesian rule that bounds the expected number of sign errors: it gains only constant factors and keeps the exponent s.

### 2.3 Link to the two-group model

The Gaussian prior is a superposition of Donoho–Jin sparse signals. The fraction of effects with |θ| > √(2r log N) is about N^(−r/τ²), which corresponds to sparsity β = r/τ². Maximising the Holm exponent 1 − β − (1 − √r)² over r:
- with u = √r, the derivative is −2u/τ² + 2(1 − u), which vanishes at u = τ²/(1 + τ²) = s;
- the value there is 1 − s²/τ² − (1 − s)² = 1 − 1/(1 + τ²) = s.

So the exponent is exactly s, and the published results come from effects around s·√(2 log N), the posterior mean at the threshold. This relies on the two-group exponent, which is itself a sketch.

### 2.4 Numbers

With α = q = 0.05 *(computed; exact numerical integrals, not simulations)*. "Bonferroni" is the rule in §2.1; "expected sign errors" is its expected number of wrong-sign publications averaged over the prior; the last two columns are the Bayesian rule of §2.5.

| τ | s | N | Bonferroni publications | N^s | Expected sign errors | Fraction published, lfsr ≤ q | Average lfsr among published |
|---|---|---|---|---|---|---|---|
| 0.5 | 0.2 | 10³ | 0.3 | 4.0 | 0.0078 | 0.0010 | 0.039 |
| 0.5 | 0.2 | 10⁶ | 1.1 | 16 | 0.0063 | 0.0010 | 0.039 |
| 0.5 | 0.2 | 10¹² | 16 | 251 | 0.0048 | 0.0010 | 0.039 |
| 1 | 0.5 | 10³ | 4.1 | 32 | 0.0043 | 0.100 | 0.025 |
| 1 | 0.5 | 10⁶ | 116 | 1,000 | 0.0034 | 0.100 | 0.025 |
| 1 | 0.5 | 10¹² | 1.0×10⁵ | 10⁶ | 0.0025 | 0.100 | 0.025 |
| 2 | 0.8 | 10³ | 70 | 251 | 0.0022 | 0.411 | 0.012 |
| 2 | 0.8 | 10⁶ | 1.5×10⁴ | 6.3×10⁴ | 0.0017 | 0.411 | 0.012 |
| 2 | 0.8 | 10¹² | 7.6×10⁸ | 4.0×10⁹ | 0.0013 | 0.411 | 0.012 |

- **Bonferroni publications track N^s** up to the 1/√(log N) factor.
- **Bonferroni is far too cautious if the prior is right.** Its expected number of sign errors is 0.001–0.008, against a budget of 0.05, and it shrinks slowly with N. The frequentist worst case (all θ near 0) is far from where the Gaussian prior puts its mass.

### 2.5 A Bayesian editor needs neither N nor a full report

**Rule.** Publish sign(zᵢ) if lfsrᵢ = Φ(−√s·|zᵢ|) ≤ q.

**Publication rate.** The rule publishes when |zᵢ| > z_q/√s, where z_q = Φ̄⁻¹(q). Since zᵢ ~ N(0, σ²) and √s·σ = τ, the fraction published is

  2Φ̄(z_q/τ),

which doesn't depend on N, so publications are Θ(N): 0.10 at τ = 1 and 0.41 at τ = 2 with q = 0.05 (§2.4).

**Cherry-picking doesn't matter.** By Dawid's selection paradox, a posterior already conditions on the data. If the prior is known and the author's selection depends only on the observed z-values, the posterior for θᵢ is the same whether i was chosen before or after looking. So the author's choice of which z-values to submit can't distort the editor's inference, and the editor needs neither N nor a full report. This is the one setting in this line of work where the editor doesn't need N.

**Padding-proof.** Each publication is judged only on its own lfsr, so adding near-certain hypotheses loosens nothing. The alternative, publishing a set whose *average* lfsr is at most q, would reward padding again.

**The price: a Bayes guarantee.** q bounds the expected sign-error share averaged over the prior, not for every θ vector. And the prior has to be right for *this author's* hypotheses:
- **Selection before the data** (which hypotheses to test at all) is not covered by Dawid's argument.
  - An author who tests hypotheses stronger than the prior assumes makes the editor's lfsr conservative, which is harmless.
  - An author who mass-tests near-zero effects makes lfsr too optimistic. A safeguard is for the editor to use a conservative (small) τ.
- **Estimating the prior from the author's own z-values** (empirical or hierarchical Bayes) breaks the argument. Dawid's ignorability requires the editor to condition on all the data that informed the selection, but here the unsubmitted z-values are missing, and they are missing *because* of their values. So an editor who learns the prior from the submitted z-values alone sees a selected sample. Either the prior comes from the field, or the author must disclose all N z-values. Senn's hierarchical analysis of Dawid's paradox (§3) adds that the posterior for a selected effect is sensitive to how the prior is specified.
- **Several analyses of one hypothesis.** If the author reports the best of several analyses, zᵢ is no longer N(θᵢ, 1). One pre-specified analysis per hypothesis is still required.

### 2.6 Exaggeration of published effects

At the Bonferroni threshold, published z-values sit near √(2 log N), but the posterior mean of θ is s·z. So published estimates overstate effects by about a factor of 1/s (the Type M error, or winner's curse). An editor may want to require shrunken estimates alongside the published sign.

### 2.7 Realistic priors are scale mixtures

Under a scale mixture of zero-mean normals with weights wₖ and signal shares sₖ, the Bonferroni publication count is about Σₖ wₖ·N^(sₖ), dominated by the widest component *(sketch)*. Heavier-tailed priors such as Laplace or t would change the exponent and need a separate calculation.

## 3. Related work

The strategic-testing literature (Kasy & Spiess, McCloskey & Michaillat, Bates et al., Hossain et al.) and the multiple-testing results behind the reduction are in §3 of the [basic-game note](../2026-09/strategic-p-value-publication-game.md). The papers below are used only here.

- **[Donoho & Jin (2004), "Higher criticism for detecting sparse heterogeneous mixtures"](https://arxiv.org/abs/math/0410072)** (Ann. Statist.).
  They study detecting a sparse mixture in which a fraction N^(−β) of N observations have mean √(2r log N) and the rest are standard normal. The optimal detection boundary (due to Ingster, and independently Jin) is attained by their Higher Criticism statistic. Their Theorem 1.3 gives the boundary for tests based on the maximum, which also covers Bonferroni and FDR-based detection: ρ_Max(β) = (1 − √(1−β))². This is the two-group model the basic-game note used for its large-N analysis. Above ρ_Max, Holm-in-equilibrium publishes about N^(1−β−(1−√r)²) results (our sketch, not their theorem). §2.3 shows the Gaussian prior is a superposition of their sparse signals, which turns the phase transition into the smooth exponent s.
- **[Gelman & Tuerlinckx (2000), "Type S error rates for classical and Bayesian single and multiple comparison procedures"](https://link.springer.com/article/10.1007/s001800000040)** (Computational Statistics 15:373–390).
  They define the Type S (sign) error: claiming θ₁ > θ₂ with confidence when in fact θ₂ > θ₁. They show that classical procedures can have Type S error rates as high as 50%, while claims based on Bayesian 95% posterior intervals have Type S rates between 0 and 2.5%. Sign errors are our error criterion (§1.2), the natural one once no effect is exactly zero. Their contrast between classical and Bayesian rates matches what §2.4 finds: frequentist sign-error control is very conservative when the prior is right.
- **[Stephens (2017), "False discovery rates: a new deal"](https://academic.oup.com/biostatistics/article/18/2/275/2557030)** (Biostatistics 18:275–294).
  He proposes the local false sign rate, the probability of getting an effect's sign wrong, as a better measure of significance than the local FDR: more generally applicable and more robustly estimated. He estimates it by empirical Bayes under a unimodal prior ("adaptive shrinkage", the ashr package). The lfsr is our Bayesian editor's criterion (§2.5). His empirical Bayes estimation of the prior is exactly what breaks selection ignorability in the game unless the author discloses all z-values.
- **[Dawid (1994), "Selection paradoxes of Bayesian inference"](https://projecteuclid.org/ebooks/institute-of-mathematical-statistics-lecture-notes-monograph-series/Multivariate-analysis-and-its-applications/Chapter/Selection-paradoxes-of-Bayesian-inference/10.1214/lnms/1215463797)** (IMS Lecture Notes–Monograph Series 24:211–220).
  When the quantity to be inferred is chosen after seeing the data, classical inference must adjust for the selection, but Bayesian inference needs no adjustment: the posterior already conditions on the data, so it is the same whether the quantity was chosen in advance or in light of the data. This is why the Bayesian editor of §2.5 is immune to the author's cherry-picking and needs neither N nor a full report, provided the prior is known and the selection depends only on observed data.
- **[Senn (2008), "A note concerning a selection 'paradox' of Dawid's"](https://errorstatistics.com/wp-content/uploads/2013/12/senn-2008-dawid-paradox.pdf)** (The American Statistician 62(3)).
  He recasts Dawid's example, in which treatments are selected for inspection because of extreme observed values, as a hierarchical model with exchangeable treatment effects. This gives an alternative explanation of the paradox. It also reveals what he calls a disturbing dependence of the inference on the prior specification: conjugate non-hierarchical priors and hierarchical priors give quite different posteriors for the selected treatment. In the game, this sharpens the caveat of §2.5. The Bayesian editor's immunity to cherry-picking is only as good as its prior, and an editor that learns a hierarchical prior from the author's submitted z-values works from a selected sample.
- **[van Zwet, Schwab & Senn (2021), "The statistical properties of RCTs and a proposal for shrinkage"](https://www.researchgate.net/publication/354078204_The_statistical_properties_of_RCTs_and_a_proposal_for_shrinkage)** (Statistics in Medicine).
  Using 23,551 study pairs from the Cochrane database, they estimate the joint distribution of the z-value and the signal-to-noise ratio. They fit a mixture of four zero-mean normals to the z-values and obtain the distribution of signal-to-noise ratios by deconvolution, since z equals the signal-to-noise ratio plus independent standard normal noise. They document overoptimistic estimates and under-covering confidence intervals among statistically significant trials, and propose a shrinkage estimator. This is empirical support for the model here: no exact nulls, and a scale-mixture prior (§2.7). Their winner's-curse findings are the Type M exaggeration of §2.6.

## 4. Open directions

1. **Redo the basic-game results with sign errors.** Results 2–3 of the basic-game note under Gaussian and scale-mixture priors, and the online game of the [online-game note](online-p-value-publication-game.md) with sign errors in place of nulls.
2. **Directional Holm.** Is directional Holm (Holm on two-sided p-values, publishing the observed sign) valid for the probability of any sign error under arbitrary dependence? Bonferroni's directional validity is the one-line union bound of §2.1.
3. **Prove the exponents.** Turn the N^s/√(log N) rate (§2.1), the superposition argument (§2.3) and the scale-mixture formula (§2.7) into proofs, and compute the exponent for heavier-tailed priors (Laplace, t).
4. **The Bayesian-editor game.** Here the strategic fight is over priors. Whose prior is it? Can an author profit by testing hypotheses weaker than the prior assumes, and how conservative must τ be to prevent it? What must the author disclose if the editor estimates the prior empirically?
5. **A hybrid rule.** Frequentist sign-error guarantees for "confirmatory" publications, plus lfsr-based "exploratory" publications labelled as such. What does the author submit under each, and does the hybrid invite padding?
6. **Interval nulls.** Analyse the game with Hᵢ: |θᵢ| ≤ δ, where π₀ = P(|θ| ≤ δ) comes from the prior, and compare publication rates with the sign-error version.
