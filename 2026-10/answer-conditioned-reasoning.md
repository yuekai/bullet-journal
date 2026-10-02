---
title: "Answer-Conditioned Reasoning: Steering a Model Toward Its Own Posterior"
description: Fine-tuning a model toward its answer-conditioned posterior over reasoning by regressing log-ratios onto known rewards, so hinted trajectories can be used off-policy without imitating hint artifacts
date: 2026-10-02
---

## Motivation

When a model rarely reaches a known correct answer, the reasoning paths that do reach it are exactly the training signal we want, but plain sampling almost never finds them. Two cheap fixes each fall short. Rejection sampling is exact but needs about 1/p(a | q) samples per success, which is hopeless on hard questions. Generating with the answer as a hint finds such paths quickly, but imitating them teaches the model to rationalize: to state the answer early and justify it backward.

The goal is a principled middle ground: use the hint, or any other proposal, to *find* answer-reaching reasoning, while training toward a target that is defined by the model itself and the answer alone.

## The target

The answer-conditioned posterior is exactly the optimal policy of a KL-regularized RL problem with reward log R and β = 1. Notation: q is the question, c the chain-of-thought, a the known correct answer, π_ref the original model, and R(c) = π_ref(a | q, c) the probability that the model answers a after reasoning c (computed by force-decoding the answer tokens). By Bayes' rule:

$$
\pi_{\text{post}}(c \mid q) = \frac{\pi_{\text{ref}}(c \mid q)\, R(c)}{p(a \mid q)}, \qquad p(a \mid q) = \sum_c \pi_{\text{ref}}(c \mid q)\, R(c)
$$

The KL-regularized objective, maximize E_π[r] − β · KL(π ‖ π_ref), has the closed-form optimum:

$$
\pi^*(c \mid q) = \frac{\pi_{\text{ref}}(c \mid q)\, \exp\big(r(c)/\beta\big)}{Z(q)}
$$

Setting r(c) = log R(c) and β = 1 gives exp(r/β) = R(c) and Z(q) = p(a | q), so π* = π_post. A general β gives a tempered posterior, π_β ∝ π_ref · R^(1/β): β > 1 moves only partway, β < 1 over-sharpens toward the answer.

The KL penalty plays the role of a fluency constraint automatically. Reasoning the model would rarely write gets little posterior mass even if it reaches the answer.

## Objective: regressing log-ratios onto known rewards

Because the target's log-ratio to the reference is computable for every CoT, we regress the model's log-ratio onto it directly; no samples from π_post are needed. Taking logs of the posterior:

$$
\log \pi_{\text{post}}(c \mid q) - \log \pi_{\text{ref}}(c \mid q) = \log R(c) - \log p(a \mid q)
$$

The constant log p(a | q) is expensive to estimate but cancels in differences. With h_θ(c) = log π_θ(c | q) − log π_ref(c | q), the pairwise loss over CoT pairs drawn from any distribution μ is:

$$
L(\theta) = \mathbb{E}_{q,\,(c_1, c_2) \sim \mu}\Big[\big(h_\theta(c_1) - h_\theta(c_2) - [\log R(c_1) - \log R(c_2)]\big)^2\Big]
$$

**Off-policy validity.** The loss is zero if and only if h_θ(c) = log R(c) + const on the support of μ, i.e. π_θ ∝ π_ref · R there. This holds for any μ, so pairs can mix hinted samples, guided samples and the model's own samples. The proposal affects coverage and speed, never the optimum.

**Gradient.** With residual δ = h_θ(c₁) − h_θ(c₂) − [log R(c₁) − log R(c₂)]:

$$
\nabla_\theta L = 2\delta\,\big[\nabla_\theta \log \pi_\theta(c_1 \mid q) - \nabla_\theta \log \pi_\theta(c_2 \mid q)\big]
$$

For a correct hinted CoT paired with a wrong self-sample, the update raises the first and lowers the second, as in DPO. Unlike DPO, it stops once the gap reaches its calibrated size, so it does not reward pushing both likelihoods down. Pairs of two correct CoTs also carry signal: they set relative weights within the correct set, the ∝ π_ref part of the posterior that binary preferences ignore.

## Proposal distributions

The loss is valid for any pair distribution μ, so the proposal only has to put answer-reaching reasoning in the data; correcting for its biases is the loss's job. Good proposals reach the answer often, stay close to what the model would write unprompted, and ideally have computable probabilities, which unlock the importance-weight diagnostics below. Two hinted proposals follow. In both, pair hinted samples with the model's own unhinted samples: hinted samples mostly share high R, so hinted-versus-hinted pairs carry little signal, and unhinted samples supply the wrong CoTs the loss pushes down.

### Reference model with the answer in the prompt

Sampling from the reference model with the answer in the prompt is a well-aimed proposal whose probabilities are exactly computable, which gives importance weights for free. Write q_h for the hinted prompt and g(c) = π_ref(c | q_h). For each hinted sample:

$$
\log w(c) = \log \pi_{\text{ref}}(c \mid q) + \log R(c) - \log \pi_{\text{ref}}(c \mid q_h)
$$

Since E_g[w] = p(a | q), the posterior is the hinted distribution reweighted: π_post = g · w / E_g[w]. Three uses follow.

- **Hint quality.** If the hint were exact conditioning, w would be constant. The spread of log w, or the effective sample size (Σw)² / Σw², measures how far the hint is from true conditioning.
- **Leakage detection.** A CoT that states the answer early is likely with the hint and unlikely without it, so its log w is low. Sorting by log w surfaces rationalizations without a hand-written filter.
- **Estimating p(a | q).** The mean of w is an unbiased estimate of the normalizer. It allows a pointwise version of the loss and indicates how hard each question is for the model.

The weakness is coverage. Whole hinted CoTs are drawn far from the plain model wherever the hint changes its behavior, and reasoning that genuinely discovers the answer, which hinted samples rarely contain, is underrepresented; the regression only constrains the model on the data's support.

### MCMC projection sampling

Karan, Chen and Du (2026) refine hinted samples with Metropolis–Hastings so that they move toward the plain model while staying correct. The chain targets p_C ∝ π_ref(c | q) · 1(c ∈ C), the KL projection of the reference model onto traces that satisfy a constraint C; for math, C is "reaches the correct final answer," so p_C is the answer-conditioned posterior with a hard 0/1 likelihood in place of R. Each step:

1. Pick a position t uniformly and keep the prefix c_{<t}.
2. Regenerate the rest with the privileged prompt (question, expert solution and the prefix, with an instruction to continue in the model's own words), giving c′. Call this kernel κ.
3. Reject c′ outright if it fails C; otherwise accept with probability min{1, π_ref(c′ | q) κ(c | c′) / π_ref(c | q) κ(c′ | c)}.

They start from the expert trace and run about 10 steps per trace, then use the final states for SFT.

As a proposal for this method, the chain has three attractive properties.

- **Local moves.** Each step changes only a suffix, so the chain explores near traces that already pass the check, rather than drawing whole CoTs from the hinted distribution. This should cover plain-model-like answer-reaching reasoning better than hinted sampling.
- **Partial correction for free.** The acceptance ratio compares likelihood under the plain prompt with likelihood under the hinted kernel, the same comparison that log w makes, so rationalizing suffixes tend to be rejected before training starts.
- **Richer constraints.** C can be any checkable property, such as an LLM grader's judgment that a free-form answer matches the expert's. That sidesteps the surface-form problem with R for free-form answers, though R itself still needs an answer string to force-decode.

Two caveats. The marginal distribution of a chain state after a few steps is not computable, so the importance-weight diagnostics are unavailable for chain states; the regression does not need them. And a short chain has not mixed: SFT on its states lands between the hinted distribution and p_C, while using the states as μ in this loss still converges to π_ref · R on their support.

## Comparison with SFT on hinted trajectories

SFT converges to the hinted distribution; the method converges to the posterior. The two coincide only when the hint is exact Bayesian conditioning, and the gap between them has a specific, harmful direction.

**1. Different fixed points.** SFT minimizes −E_g log π_θ(c | q) = KL(g ‖ π_θ) + const, so π_θ → g. (With correctness filtering, replace g by g restricted to correct CoTs.) Using π_post = g · w / E_g[w]:

$$
\mathrm{KL}(\pi_{\text{post}} \,\|\, g) = \mathbb{E}_{\text{post}}[\log w] - \log \mathbb{E}_g[w] \;\ge\; 0
$$

This is zero if and only if w is constant on the support of g, i.e. the hinted prompt is exact conditioning. The method's fixed point is π_post regardless of hint quality.

**2. SFT is biased toward rationalization.** Relative to the posterior, SFT overweights each CoT by E_g[w] / w(c). Decomposing:

$$
\log w(c) = \big[\log \pi_{\text{ref}}(c \mid q) - \log \pi_{\text{ref}}(c \mid q_h)\big] + \log R(c)
$$

The bracket is very negative for CoTs much likelier with the hint than without: early answer statements, backward reasoning, unjustified leaps. SFT overweights these exponentially in that gap. It also ignores R: after filtering, a CoT with R = 0.3 counts the same as one with R = 0.99.

**3. Bounded drift.** Since R ≤ 1:

$$
\mathrm{KL}(\pi_{\text{post}} \,\|\, \pi_{\text{ref}}) = \mathbb{E}_{\text{post}}[\log R] - \log p(a \mid q) \;\le\; -\log p(a \mid q)
$$

Conditioning moves the model at most −log p(a | q) nats per question, about 6.9 nats for a 1-in-1,000 question. SFT has no such bound: KL(g ‖ π_ref(· | q)) sums the hint-induced log-ratio over every token and can reach hundreds or thousands of nats for long CoTs.

**4. SFT is blind to the model's own mistakes.** The SFT loss depends on π_θ only on the support of g; mass elsewhere matters only through normalization. A model concentrating leftover mass on one confident wrong pattern gets the same loss as one spreading it thinly. The method's pairs include on-policy samples, so the model's own high-probability wrong CoTs are pushed down in proportion to their residual.

**5. Compounding error over long horizons.** SFT trains on hinted prefixes but runs on its own. For behavior cloning with per-step error ε, error over T steps can grow as O(T²ε), versus O(Tε) when training on the learner's own trajectories. Pairing with the model's own samples is a partial correction, iterative training (see open questions) a fuller one, and with CoTs of thousands of tokens the gap is large.

**When SFT suffices.** If w is nearly constant, the KL in point 1 is near zero and SFT is the cheaper equivalent. Measuring the spread of per-token log w on hinted trajectories answers this before committing to the method.

## Practical considerations

Most failures in practice come from log-probabilities that don't mean what the math assumes.

- **Computing R.** Cut the CoT before the model's own answer, append the reference answer in canonical form, and sum those tokens' log-probabilities under the plain prompt. Canonicalize answers, since R measures one surface form, not all equivalent ones.
- **Clipping.** log R for wrong CoTs can be −60 or lower. Clip from below, for example at −20, to keep the regression well-conditioned; this slightly overweights clearly wrong CoTs relative to the exact posterior.
- **Sampling.** Sample at temperature 1 without top-p or top-k, or compute every probability under the same truncated distribution. Otherwise log-ratios and importance weights are wrong.
- **Log-prob consistency.** Check that the inference engine and the training code return matching log-probabilities for the same sequence. Mismatches silently corrupt every log-ratio.
- **Long CoTs.** Sequence log-probabilities grow with length, so importance weights degenerate and regression targets get noisy for very long reasoning. Cap the reasoning budget, and prefer per-token summaries of log w for diagnostics.
- **Cost.** Everything except the trained model's log-probabilities can be computed once offline, so each training step costs about the same as DPO.
- **Sanity check.** Regress the learned log-ratio h_θ(c) on log R(c) over held-out samples. The slope should be 1 and the intercept −log p(a | q).

## Limitations and open questions

The posterior can only reweight what the reference model could already generate; it cannot add knowledge.

- **No new content.** SFT's extra drift is mostly rationalization, but it can also carry genuine information from the hint. When answers depend on facts the model lacks, the method discards that. A tempered target with β < 1 extends past the posterior along the direction R points, but whether that helps is an empirical question.
- **Lucky reasoning.** When p(a | q) is tiny, posterior mass may sit on CoTs that reach the answer by chance or by flawed steps. R scores the answer, not the validity of the steps.
- **Coverage.** Off-policy validity holds on the data's support only. How well the fitted model generalizes to unseen answer-reaching reasoning is not guaranteed.
- **Answer surface forms.** R under one canonical string underestimates the probability of the answer. Summing over equivalent forms, or a learned verifier, would be more faithful.
- **Open: iterative training.** The one-shot loss can be split into T rounds with REBEL (Gao et al., 2024). Round t uses the current model π_t as the reference, fresh samples from π_t, and step size η; its minimizer is the mirror-descent step π_{t+1} ∝ π_t · R^η, so π_T ∝ π_ref · R^{ηT} and ηT = 1 recovers the posterior (for example 4 rounds at η = 0.25). Running every round at η = 1 gives R^T instead, which conditions on the same answer T times and over-sharpens. R must always be scored by the original π_ref, never by π_t. To test: whether small per-round moves are easier to fit, and whether fresh samples cover the regions the model moves into better than samples from π_ref.
- **Open:** whether squared loss is the best regression loss here, how to pick β per question, and whether step-level pairs sharing a prefix sharpen credit assignment as they do for step-level DPO.

## References

- Karan, Chen and Du, 2026. [Finetuning with Sampling: SFT Learns Better Than You Think](https://arxiv.org/abs/2610.02140). [Project page](https://aakaran.github.io/finetuning_with_sampling/).
- Gao et al., 2024. [REBEL: Reinforcement Learning via Regressing Relative Rewards](https://arxiv.org/abs/2404.16767). NeurIPS 2024.
- Rafailov et al., 2023. Direct Preference Optimization: Your Language Model is Secretly a Reward Model. NeurIPS 2023.
- Zelikman et al., 2022. STaR: Bootstrapping Reasoning With Reasoning. NeurIPS 2022.
- Pang et al., 2024. Iterative Reasoning Preference Optimization.
- Hoffman et al., 2023. Training Chain-of-Thought via Latent-Variable Inference (TRICE). NeurIPS 2023.
- Zhao et al., 2024. Probabilistic Inference in Language Models via Twisted Sequential Monte Carlo. ICML 2024.
- Ross, Gordon and Bagnell, 2011. A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning (DAgger). AISTATS 2011.

Citations other than REBEL and Karan et al. are from memory and unlinked; verify details before external use.
