---
title: Open vs closed LLM ecosystem model
description: Setup for a model of competition between closed LLMs and one open LLM, with users and models as vectors in task space, fixed prices, private learning for closed models and public learning from open-model usage; the questions a solved model should answer, and how the setup relates to LLM-era and open-source economic models
date: 2026-10-02
---

A model of the open-weight LLM ecosystem in which the agents are organizations rather than individual programmers. Users and models both live in a task space; closed models learn privately from their own users, while usage of the open model improves every model. This note records the setup, the questions a solved model should answer, and how both compare to existing work. Nothing has been solved yet.

## 1. Setup

### 1.1 Primitives

- **Tasks.** There are d task types, such as coding, writing and math. Everything lives in the nonnegative orthant of ℝᵈ.
- **Users.** A continuum of users, each with a usage profile x ∈ ℝᵈ₊. Write x = r·θ with r ≥ 0 the intensity of AI use and θ in the unit simplex the task mix. Users are distributed by a measure μ on ℝᵈ₊ with finite first moment, since the learning rules integrate x.
- **Models.** One open model, indexed 0, and n closed models, indexed 1..n. Model j has an ability profile aⱼ ∈ ℝᵈ₊, one component per task, and charges a fixed per-user price pⱼ ≥ 0. A fixed price is a subscription: at a given price a heavy user yields the same revenue as a light one but contributes more learning.
- **Choice.** User x gets utility uⱼ(x) = x·aⱼ − pⱼ from model j and picks the argmax. *Assumption:* there is an outside option with utility 0, so users with x·aⱼ < pⱼ for every j use nothing. If p₀ = 0 the open model is the outside option and every user uses something. p₀ is a parameter with default 0.

### 1.2 Demand regions

Let Dⱼ be the set of users choosing j. Utility differences are linear in x, so Dⱼ is an intersection of half-spaces, hence a convex polyhedron. Two consequences:
- **Vertical sorting within a direction.** For fixed θ, users choose among lines in r with slope θ·aⱼ and intercept −pⱼ. The upper envelope sorts users by intensity: higher r goes to higher quality in that direction at a higher price. A model with lower slope and higher price than another gets no users of that direction. This is Mussa–Rosen vertical differentiation, direction by direction.
- **Horizontal sorting across directions.** Across task mixes the models compete spatially in task space. The free open model captures a convex neighborhood of the origin plus any directions where closed models have little edge.

### 1.3 Usage

The task-weighted usage of model j is the vector Uⱼ = ∫_{Dⱼ} x dμ(x); component Uⱼₖ is how much task-k work flows through model j. The user mass is Nⱼ = μ(Dⱼ).

### 1.4 Learning

Let h be a learning function applied componentwise.
- **Private learning (closed models).** Closed j improves in the directions its own users push it: daⱼ/dt includes h(Uⱼ).
- **Public learning (open model).** Open usage improves everyone: da₀/dt = h(U₀), and each closed j also receives s·h(U₀), with s ∈ [0, 1] the spillover rate.

```
da₀/dt = h(U₀)
daⱼ/dt = h(Uⱼ) + s · h(U₀)     for j = 1..n
```

- *Assumption:* closed usage does not spill to the open model.
- *Assumption on s:* s = 1 says closed models absorb open improvements fully, through released fine-tunes, datasets, distillation and recipes; s < 1 says absorption is costly or partial. Keep s free: it is the parameter the LLM-era literature argues about (see §3).
- *Boundedness:* utility is linear in a, so unbounded growth has no scale. Take abilities in [0, 1]ᵈ with logistic learning, hₖ(U, a) = γ·Uₖ·(1 − aₖ). Depreciation or a concave h are alternatives.

### 1.5 Timing and objectives

Users are a continuum with no congestion, so they are nonstrategic: given current abilities and prices they sort. The only game is among closed firms over prices.
- **Closed firm j** earns pⱼ·Nⱼ per unit time, with zero marginal cost. Static version: each firm sets pⱼ to maximize current profit given a and the others' prices. Dynamic version: firms discount at ρ and value usage as investment in aⱼ, so penetration pricing appears. Solve the static, myopic version first.
- **Open provider.** Exogenous for now: price p₀ and no objective. Who provides the open model and why is the discrete-public-good question of §3.3.

### 1.6 Smallest instance

Two tasks, one closed model, one open model at price zero. The closed firm's demand region is the set of users above the threshold curve r ≥ p₁ / (θ·(a₁ − a₀)) in the intensity–direction plane, the pricing problem is one-dimensional, and the dynamics are a 2×2 system whose phase portrait can be drawn.

## 2. Questions the solved model should answer

- **Do closed firms cede the low end?** Users a closed firm prices out go to the open model, whose learning spills back at rate s. Raising price trades exclusive learning for shared learning. Conjecture: equilibrium closed prices rise with s.
- **Where do abilities converge and where do they diverge?** Public learning concentrates in the directions of U₀, which are low-intensity users across all task mixes. Private learning specializes closed models toward their heavy users. Conjecture: abilities converge on common tasks and diverge on the tasks heavy users care about.
- **Does the open model survive?** With s = 1 the closed models match every open improvement and add their own, so the ability gap never closes. Does the open model's demand region shrink to a point or stabilize? This is the Athey–Ellison steady-state-vs-collapse question in this setting.
- **How does the open model's user base shape the ecosystem?** Because public learning is directed by U₀, the open model's users decide which tasks every model improves at. Which task mixes end up over- or under-served relative to a planner's choice?
- **Welfare.** Consumer surplus is ∫ maxⱼ uⱼ(x) dμ. How does it move with s, with p₀, and with the number of closed firms? Does the open model raise welfare mainly by serving low-intensity users or mainly by improving closed models?
- **Dynamic pricing.** Under forward-looking firms, how much penetration pricing does the private-learning motive generate, and does it crowd the open model out of task directions it would otherwise own?

## 3. Related work

### 3.1 LLM-era economic models

- **Jamison and Yu (2026), [Competing for the Future of AI](https://bear.warrington.ufl.edu/centers/purc/docs/papers/2605-Economic-Incentives-of-Open-Source-Foundation-Models.pdf).** A two-stage structural model estimated on Hugging Face data: model owners choose a degree of openness, downstream developers choose which model to adopt. Short-run returns cover under half of openness costs; knowledge spillovers from downstream developers, which raise next-generation quality, rationalize the rest. *Comparison:* their spillover runs from downstream developers back to the model owner; ours runs from open-model users to every model. Their openness is a scalar index with data disclosure as one of six dimensions, estimated on five commercial owners; ours is a binary type with a learning asymmetry instead of an openness choice.
- **Xu, Wang, Chen and Xie (2025), [The Economics of AI Foundation Models](https://arxiv.org/abs/2510.15200).** Two-period game: an incumbent chooses an openness scalar that lowers a deployer's fine-tuning cost, an entrant learns from it, and a data flywheel lowers the incumbent's future cost. Openness is non-monotone in flywheel strength; transparency mandates can backfire. *Comparison:* their learning is a cost reduction keyed to adoption; ours is a vector of abilities keyed to task-weighted usage, so learning has a direction. They have one incumbent and one entrant; we have several closed firms and an open model of fixed type.
- **Qiu, Laufer, Kleinberg and Heidari (2025), [Modeling the Economic Impacts of AI Openness Regulation](https://arxiv.org/abs/2507.14193).** A generalist, a specialist fine-tuner and a regulator who sets an openness threshold. *Comparison:* no user population and no learning dynamics; their object is the regulator's definition.
- **Commey (2026), [Who Does Withholding Delay?](https://arxiv.org/abs/2607.22957)** Release tiers against adversaries who can substitute. Safety side only.
- **Nagle and Yue (2025), [The Latent Role of Open Models in the AI Economy](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5767103).** Empirical: on OpenRouter data closed models hold most tokens despite being several times more expensive, and frontier open models reach parity within months. *Comparison:* a stylized fact for our demand side. Our model gives price-only sorting; their persistence of closed-model share suggests switching costs or brand terms we omit.
- **Linåker, Osborne, Ding and Burtenshaw (2025), [A Cartography of Open Collaboration in Open Source AI](https://arxiv.org/abs/2509.25397).** Qualitative study of 14 open LLM projects. Corporate projects cite ecosystem building; research institutes cite open science; grassroots projects cite access and language representation. Curated datasets are what organizations are reluctant to share. *Comparison:* the motivation taxonomy for endogenizing the open provider, and evidence that excludable value sits in data rather than weights.

None of the formal models above has a user population in a task space, directional learning, or a single open model whose usage improves rivals. None treats models that release training data as a distinct type: every one collapses openness to a scalar, and no sample contains a fully open producer.

### 3.2 Models of open source ecosystems

- **Lerner and Tirole (2002), [Some Simple Economics of Open Source](https://onlinelibrary.wiley.com/doi/10.1111/1467-6451.00174).** Contributions as signals of skill paid off later through jobs and reputation. *Comparison:* our agents are firms, so the analog is talent attraction and standard-setting, neither of which is in the setup yet.
- **Johnson (2002), [Open Source Software: Private Provision of a Public Good](https://onlinelibrary.wiley.com/doi/10.1111/j.1430-9134.2002.00637.x).** User-programmers decide whether to build an enhancement that becomes a public good. *Comparison:* in our setting users do not build; they generate learning by using. The public good is the open model's ability vector, provided by usage rather than effort.
- **Bessen (2005), [Open Source Software: Free Provision of Complex Public Goods](https://www.researchoninnovation.org/opensrc.pdf).** Complex goods cannot be served by standard products, so users customize and share. *Comparison:* our task space is the analog of product complexity; heterogeneity in θ is why no single model serves everyone.
- **von Hippel and von Krogh (2003), [Private-Collective Innovation](https://pubsonline.informs.org/doi/10.1287/orsc.14.2.209.14992)** and **Henkel (2006), [Selective revealing](https://ideas.repec.org/a/eee/respol/v35y2006i7p953-969.html).** Firms reveal when private benefits of revealing exceed the loss. *Comparison:* the open provider's objective, once endogenized. Releasing weights but not data is selective revealing with the know-how retained.
- **Athey and Ellison (2014), [Dynamics of Open Source Movements](https://onlinelibrary.wiley.com/doi/abs/10.1111/jems.12053).** Reciprocal altruism drives a project to a steady-state size, but a need for user support makes zero quality absorbing. *Comparison:* our open-model survival question is the same question with usage-driven learning replacing contribution.
- **Benkler (2002), [Coase's Penguin](https://arxiv.org/pdf/cs/0109077).** Peer production wins when tasks are modular and granular. *Comparison:* does not apply to the base-model layer, which is lumpy; it applies to the derivative layer of fine-tunes and distillations that our spillover rate s abstracts.
- **Casadesus-Masanell and Ghemawat (2006), [Dynamic Mixed Duopoly](https://www.hbs.edu/faculty/Pages/item.aspx?num=21129).** A profit maximizer against a zero-price rival with demand-side learning. *Comparison:* the closest ancestor. Our additions: a vector of abilities with directional learning, horizontal differentiation in task space, and learning that spills from the free rival to the priced one.
- **Economides and Katsamakas (2006), [Two-Sided Competition of Proprietary vs. Open Source Platforms](https://pubsonline.informs.org/doi/10.1287/mnsc.1060.0549).** Platform pricing toward users and complementors. *Comparison:* we have no complementor side; downstream developers would be a natural extension.
- **Mustonen (2003), [Copyleft](https://research.aalto.fi/en/publications/copyleft-the-economics-of-linux-and-other-open-source-software)** and **Lerner and Tirole (2005), [The Scope of Open Source Licensing](https://www.nber.org/papers/w9363).** License restrictiveness as a strategic variable. *Comparison:* license terms would enter through s, since restrictive terms limit what rivals can absorb.
- **Bliss and Nalebuff (1984), Dragon-slaying and ballroom dancing, J. Public Econ. 25.** Private supply of a discrete public good as a war of attrition. *Comparison:* the natural frame for who provides the open model, which the setup leaves exogenous.

### 3.3 What the setup leaves out

- The open provider's identity and objective: a complement-seller commoditizing the model layer, a nonprofit, or a state. This is the discrete-public-good game among heterogeneous firms that none of the LLM-era models studies.
- Models that release training data, whose spillover is larger because the recipe becomes non-excludable. A third type with a higher s to rivals, funded externally, would capture them.
- Switching costs, brand and information frictions on the demand side, which Nagle and Yue suggest are large.
- A downstream developer layer, which is where Jamison–Yu locate the spillover.
