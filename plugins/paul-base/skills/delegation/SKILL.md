---
name: delegation
description: How the main model decides whether to hand work to a paul-base subagent instead of doing it in-session — which of the four agents (extractor, implementer, reviewer, researcher) fits the shape of the work, which model tier each runs on and why, how to split a job across parallel agents so they cannot collide, what a delegation spec must contain, and how to verify what comes back rather than trust it. Use when asked to "use sonnet agents", "save tokens", "delegate this", "have an agent do it", "split this up", "let agents implement it", "use a workflow", "fan out", "orchestrate this", or "ultracode" — and above all whenever the main model is itself about to spawn a subagent or a workflow, whether or not the user asked for it — and when something has gone wrong with a delegated task — a subagent's result looks wrong, an agent guessed instead of returning a question, two agents edited the same file, or a review came back as opinions.
---

# Delegation

Deciding when to hand work to a `paul-base` subagent instead of doing it in this session, and
how much to trust what comes back. `base-conduct` wins where the two disagree; the four agents
in this plugin's `agents/` folder — extractor, implementer, reviewer, researcher — are the
standard workers. This applies whenever agents get spawned: when the user asks, when the main model
decides on its own, and through the `Workflow` tool as much as the `Agent` tool.

## The most important rule

A subagent's report is a claim, not a verification. Before the main model tells the user anything
is done, it reads the diff or re-runs the checks itself.

The dead end that looks like verification and isn't: an implementer returning "all verified."
In the session this skill was built from, three Sonnet implementer agents applied a 21-file
change from written specs — every agent reported success — and the main model found two real
gaps only by reading the full diff, not by trusting the reports.

The second dead end: delegating work that's too small. A spawn starts cold — no memory of this
conversation — and reads roughly 1,100 words of `base-conduct` before it does anything. If the
delegation spec would take longer to write than the task takes to do, do the task.

## When to delegate, and to whom

| Shape of the work | Who | Why |
|---|---|---|
| Reading more than ~3 files or ~20 KB whose contents you won't need verbatim later | extractor | Keeps the bulk out of the main context — three extractor agents split a 116 KB repo between them, spent ~90,000 tokens each, and returned fact sheets under 2,000 words |
| Mechanical edits from a spec you can write completely | implementer, one per disjoint file set | Parallel and cheap — correctness is checkable against the spec, not judged |
| Reviewing work the main model wrote, or a change too big to hold in context | reviewer | Fresh context carries none of the author's assumptions |
| A factual question whose answer is on the web and needs sources | researcher | The main model would otherwise browse in its own context |
| Decisions, anything touching what the user meant, small edits, the final verification, anything with an ambiguity not resolved before spawning | the main model itself | These are exactly what a cold agent gets wrong |

Sequence for a multi-step job, in one line: extract, decide with the user (`AskUserQuestion`,
recommended option first), implement in parallel, verify, review if the change is large or the
main model wrote it.

## Which model, and why

Prices and scores as of 23.09.2026; re-check them when a new generation ships.

| Agent | Model | Why |
|---|---|---|
| extractor, implementer, researcher | Sonnet 5 | $2/$10 per Mtok — one fifth of Fable 5.1's $10/$50, half of Opus 5.5's $4/$20; scores 38 on the Artificial Analysis Intelligence Index against Opus 4.8's 42, and Anthropic's own launch post says it matches Opus 4.8 on some tasks at high effort; right whenever the task is checkable against a spec, a checklist, or a test |
| reviewer | Opus 5.5 | $4/$20 per Mtok, a fifth cheaper than Opus 5's $5/$25; scores 58 on the Intelligence Index, seven points above Opus 5; judgment with no one to ask; the independence comes from fresh context, not from being a different model than the session |

Three rules that don't fit the table:

- **Haiku is not used.** Haiku 4.5, the newest and only current Haiku, has a February 2025
  knowledge cutoff, a 200K context window, no effort control, and a retirement floor of 15
  October 2026 — and there is no Haiku 5. It becomes a candidate for pure mechanical extraction
  only if a Haiku 5 ships.
- **Inherit the session model only when independence at full capability is the point**, never
  for cost. An agent that inherits the session model costs the same as not delegating.
- **Judge cost per completed task, not per token.** A Sonnet run that needs a redo costs more
  than an Opus run that doesn't. Effort levels live in the agent definitions — medium for the
  three Sonnet agents, high for the reviewer — and are overridden per spawn only with a stated
  reason.

## Through the `Workflow` tool

The tables above are written for the `Agent` tool. The `Workflow` tool spawns agents too, and
omitting `model` there makes every agent inherit the session model. That default is wrong here:
it silently puts extractor work on the session's model and costs the saving this skill exists to
make.

The measured failure, 17.09.2026: seventeen workflow agents ran with no `agentType` at all. Four
were pure extractor work — reading a repo's conventions, a minified bundle, a skill inventory —
and ran on Opus at $5/$25 instead of Sonnet at $2/$10. Nine were reviewers that never loaded
`paul-base:review`. Nothing warned; the workflow simply inherited the session model throughout.

State the choice on every `agent()` call:

| This skill says | The workflow call |
|---|---|
| extractor | `{agentType: 'paul-base:extractor', model: 'sonnet', effort: 'medium'}` |
| implementer | `{agentType: 'paul-base:implementer', model: 'sonnet', effort: 'medium'}` |
| researcher | `{agentType: 'paul-base:researcher', model: 'sonnet', effort: 'medium'}` |
| reviewer | `{agentType: 'paul-base:reviewer', model: 'opus', effort: 'high'}` |

`agentType` is the part that matters most. Without it the agent is a generic worker: it loads
none of the agent definition, and `paul-base:reviewer` in particular loses the `paul-base:review`
skill that its definition preloads — so the review comes back as improvised opinion, which is the
exact failure the reviewer exists to prevent. Passing `model` and `effort` as well costs nothing
and makes the tier readable in the script — `agentType` alone already carries the tier from the
agent definition, so `model` and `effort` are restated for readability, not as the per-spawn
override the rule above discourages.

## The spec

Every delegation prompt states, in order:

1. The goal, in one sentence.
2. The exact files the agent owns — and that nothing else may be touched.
3. What to produce: format, and a length cap.
4. The verification the agent must run itself and include in the result.
5. Return, don't guess — an unresolved ambiguity comes back *as* the result, because the agent
   has no way to ask the user anything.
6. The prohibitions: no commit, no push, nothing outside the file list, nothing outside this
   machine.

For parallel work, partition by file ownership — one agent per shared file such as a manifest,
never two. Tell each agent that others are running concurrently, so it ignores their entries in
`git status`. Give agents the facts they need instead of telling them to go discover those
facts — a fact stated in the spec is one they can't get wrong.

## Verifying what comes back

After implementers: check that `git status` shows exactly the expected files, then read the
full diff — not the agents' reports. Run the checks yourself: word counts, JSON validity, a
grep for a phrase that should be gone. Fix small gaps directly rather than re-spawning;
re-spawn only when the rework is substantial enough that a patch would be messier than a redo.

After an extractor: spot-check two or three of its claims against the source files directly.

After a researcher: check the dates on what it cites, and check whether each source is primary
or is a summary restating a vendor's own claim.

## Boundaries

Subagents cannot ask the user anything — every `AskUserQuestion` belongs to the main model, before
or after delegating, never inside an agent. Subagents never commit or push. `base-conduct`
rule 5 (blast radius) applies to them exactly as it does to the main model: nothing beyond this
machine changes without explicit permission. The main model reports faithfully which agent did
what and what it, itself, verified — it never presents an agent's claim as its own
verification.
