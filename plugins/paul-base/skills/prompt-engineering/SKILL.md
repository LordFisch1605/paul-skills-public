---
name: prompt-engineering
description: Write or fix a prompt, system prompt, or set of instructions that will be sent to a language model — for an agent, a one-off task, or a reusable template. Use when asked to "write a prompt", "write a system prompt", "verbessere diesen Prompt", "das Modell macht nicht was ich will", "why does the model ignore this instruction", "schreib mir Instructions für ein GPT", or when a model's output is vague, off-format, wrong-toned, or fabricated and the fix is in the wording. Applies the 21 prompt-engineering principles in references/principles.md as a working method, not just a reading list.
---

# Prompt engineering

The method for writing and repairing prompts sent to a language model. The full catalogue of
21 principles — the rule, why it works, and a before → after for each — lives in
[`references/principles.md`](references/principles.md), grouped as **A** writing one prompt,
**B** shaping output, **C** reasoning and grounding, **D** the process around it.

**Authority:** where this file and `principles.md` disagree, `principles.md` wins — it holds
the reasoning; this file only holds how to apply it.

## The most important rule

**Reach for the clever technique last, not first.** The failure that looks like it needs
few-shot examples, chain-of-thought, or a longer prompt is almost always plain ambiguity —
an undefined term, a missing boundary between instruction and data, an unstated format. Adding
machinery on top of an unclear task buries the real defect and burns tokens.

So the order is fixed:

1. **State the task clearly** and try it **zero-shot** first (§2, §5). Reread it as if new to
   the task — every gap you'd fill from memory, the model fills its own way.
2. **Separate standing instructions from the input**, wrapping variable data in XML tags (§1,
   §4). This is also the front line against prompt injection (§21).
3. **Only then** add examples, step-by-step reasoning, or self-consistency — and only for the
   specific weakness that survived steps 1–2.

Most weak prompts are fixed at step 1 or 2. A prompt that is still wrong *after* clarity and
clean separation is the one that has earned an advanced technique.

## Building a prompt

For a non-trivial prompt, assemble it from the skeleton in §18 — skipping elements the task
doesn't need, but in this order:

| # | Element | Principle |
|---|---|---|
| 1 | Role / task context | §3 |
| 2 | Tone | §7 |
| 3 | Detailed rules, including what to **avoid** | §7, §8 |
| 4 | Examples in `<example>` tags — only if the pattern is hard to describe | §5 |
| 5 | Input data in XML tags | §4 |
| 6 | The immediate task, restated **near the end** | §2 |
| 7 | "Think step by step first" — for anything needing reasoning | §13 |
| 8 | Output-format spec + constraints (length, counts, allowed values) | §6, §7 |
| 9 | Prefill the start of the answer, to force the shape hard | §6 |

The request comes after the data it refers to (step 6). Steps 7–9 are for
reasoning and machine-parseable output; drop them for a simple ask.

## Fixing a prompt that misbehaves

Match the symptom to the principle rather than rewriting blindly:

| Symptom | Reach for |
|---|---|
| Vague, generic, rambling | Clearer task + constraints (§2, §7); resolve ambiguous terms (§9) |
| Wrong or chatty format | Format spec + prefill (§6) |
| Drifts into an unwanted framing | Negative prompting — name what to exclude (§8) |
| Misreads tricky / multi-step input | Write out the reasoning before the answer (§13) |
| Makes up facts | Give it an out ("say I don't know"), quote-then-answer, ground in retrieved docs, lower temperature (§15, §17) |
| Obeys instructions hidden in user text | Isolate input in tags, reinforce the role, refuse overrides (§4, §21) |
| Big job done unevenly, drops parts | Chain into single-purpose steps (§16) |

## The process

A first prompt is a draft (§19). Generate output, name the specific weakness, revise, repeat —
and where the choice is between phrasings, test them against the same task on fixed criteria
rather than going by feel. Define what "good" means *before* judging (§20). This is §4 of
base-conduct — goal-driven execution — applied to prompts: the success criterion is checkable
output, not "reads better".

## Boundaries

- **This skill writes prompts; it does not decide what the model is *for*.** The purpose and the
  audience are the user's call.
- **Don't paste a real prompt's private or work content into `references/`.** Worked examples
  stay in the catalogue; live prompts are referenced, not copied in.
- **Don't smuggle advanced techniques past step 1.** If a prompt is unclear, say so and fix the
  clarity — do not paper over it with examples.

## Checklist

Before sending a non-trivial prompt (condensed from §Quick checklist in `principles.md`):

- [ ] Task stated explicitly — a stranger following it literally produces what you want, no
      undefined terms? (§2, §9)
- [ ] Standing instructions (role, rules, tone) separated from the input, data in tags? (§1, §4)
- [ ] Tried zero-shot first; added an example only where the pattern is hard to describe? (§5)
- [ ] Output format and constraints specified; prefilled if it must be exact; named what to
      avoid? (§6, §7, §8)
- [ ] For reasoning: asked it to think first, sampled more than once if high-stakes? (§13, §14)
- [ ] Gave it an out and required grounding/quotes for factual claims? (§15, §17)
- [ ] Big job broken into steps? (§16, §18)
- [ ] If it takes untrusted input, is that input isolated and the role reinforced? (§21)
