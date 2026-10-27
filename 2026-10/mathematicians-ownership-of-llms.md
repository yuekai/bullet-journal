---
title: Mathematicians' ownership of LLMs
description: Why physicists feel they own the LHC but mathematicians don't feel they own LLMs, and what mathematical ownership could look like
date: 2026-10-27
---

A thought being chewed on, not a plan.

## The observation

Physicists own their tools without building them: no ATLAS physicist built the LHC, yet they feel it is theirs. Mathematicians don't feel that way about LLMs, which look like the main tool for mathematics going forward.

## What "ownership" consists of for physicists

Not understanding the hardware (most couldn't explain the cryogenics). Three things instead:

1. **Derived from their own theory.** The instrument's behavior is in principle explicable in terms they already own.
2. **They own the error model.** They can say "this measurement has systematic X of size Y" and defend it.
3. **Institutional ownership.** The community asked for it, designed it over 20 years, and runs the collaborations. A detector is a physicist's the way a telescope is an astronomer's.

## LLMs fail all three for mathematicians

- Not derived from mathematics in any usable sense: the optimization is mathematical, but the behavior that matters (proof-finding) has no theory.
- No error model: nobody, builders included, can say when it will confidently produce a wrong lemma.
- Institutionally, mathematicians didn't ask for it; they are customers of labs with different incentives, and the tool changes under them every six months.

## Precedents: mathematicians have built ownership before

- Appel–Haken (1976) produced the same anxiety: a proof nobody could own. The resolution took decades: Hales' Kepler proof → Flyspeck → Lean. The community's answer to "we can't understand the tool" was "then we build the verifier and own that."
- Computer algebra: Sage was explicitly William Stein's "stop renting Magma" project.

## Likely shape of mathematical ownership: own the interface, not the model

Physicists don't understand their detector electronics; they understand the statistical inference layer on top. The mathematical analogues:

- **The verifier.** Lean / formal proof as the trust boundary that turns an untrusted generator into a trusted result.
- **The evaluation.** FrontierMath and similar benchmarks: already happening, arguably the first real act of ownership.
- **A theory of the tool.** A working empirical understanding of when and how it fails on mathematical problems: the analogue of knowing your systematics.

## The disanalogy that may persist

LHC ownership is partly that physicists can reason about it from first principles. If LLM behavior stays theory-less, mathematical ownership will look like an experimentalist's craft knowledge rather than a theorist's understanding, a kind of ownership mathematicians have historically been uncomfortable with. That discomfort may be the real content of the feeling.

## Open

- Whether a usable theory of LLM proof-finding behavior ever arrives, or craft knowledge is the ceiling.
- Whether verifier + evaluation ownership is enough to make the tool feel like the community's, given it stays economically owned by labs.
