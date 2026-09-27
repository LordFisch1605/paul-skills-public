---
name: review
description: How to review a piece of work — a diff, a document, a skill, a plan, a directory — so the findings are evidence-backed, ranked by severity, and free of the author's own assumptions about what it does. Use when asked to "review this", "check my changes", "find what's wrong with" something, "is this correct", "kritisch prüfen", "review it critically and fair", or for a "second opinion"; the paul-base reviewer agent preloads this skill on every spawn. Also use when a previous review came back wrong — as opinions with no file and line, as praise with no findings, or as a rewrite instead of findings.
---

# Review

How to review a piece of work so the findings hold up on inspection. `base-conduct` wins on
conduct; on substance, the reviewed work's own stated goal is the standard — the reviewer does
not substitute a goal of their own.

## The most important rule

Every finding carries evidence the reader can check without trusting the reviewer: a file and
line, or a verbatim quote, plus the concrete failure it causes. "This could be cleaner" is an
opinion, not a finding, and doesn't survive to the report.

Two more dead ends:

- **Verifying against the author's description of the work instead of the work itself.** The
  description is what they believe they built; the artifact is what they actually built. Read
  the artifact.
- **Rewriting instead of reviewing.** A review returns findings, not fixes — unless fixes were
  explicitly asked for. Handing back a rewrite hides which specific things were wrong.

Measured: the review this skill was built from produced 9 numbered findings and 8 smaller drifts
across ~40 files. Every item that named a file and the concrete failure was acted on the same
day. The one item left open was the one whose failure could not be verified from that machine —
it went into the "could not verify" list instead of being asserted.

## Procedure

1. **Pin the goal.** What was this meant to achieve, and for whom? If it isn't stated anywhere,
   write down your assumption before reading anything, so it's visible and checkable rather than
   silently steering the review.
2. **Read the artifact, not a summary of it.** For a change: `git diff` against `HEAD`, plus the
   surrounding code it touches. For a repository: the files themselves.
3. **Look, in this order:**
   - Things that don't work — broken paths, links, or commands; contradictions between files; a
     stated requirement that isn't met.
   - Things that don't fit together — two mechanisms doing one job, a reference to something
     that moved, a claim in one file that another file disproves.
   - Things that are unclear.
   - Style — last, and only if asked.
4. **Verify every candidate finding before writing it down.** Run the command. Open the file.
   Count. A finding that wasn't checked doesn't go in the report.
5. **Rank by severity:** breaks, misleads, drifts, nit.
6. **Say what was checked and holds up**, briefly — so the reader knows what passed, not just
   what failed.
7. **Report as:** a two-sentence verdict; numbered findings, most severe first, each with its
   evidence, the failure it causes, and a one-line fix if one is obvious; a "checked and fine"
   list; a "could not verify" list. More than ten findings — group them, don't truncate.

## Fresh context

The bias rule: the reviewer should not be the work's author, when that can be arranged. Spawned
as the `reviewer` agent, it receives the artifact and the goal — not the author's reasoning, not
their intentions, none of the context that made the choices feel obvious while writing.

An author reviewing their own work has to do the same thing deliberately: re-derive the
judgment from the artifact as it stands, not from memory of what was intended. Memory of intent
is exactly what a fresh reviewer doesn't have, and exactly what makes self-review weaker.

## Boundaries

No edits unless asked — a review reports, it doesn't fix. No re-scoping the goal to one the
reviewer finds more interesting. No commit. What couldn't be verified is reported as unverified,
never guessed at. Findings follow the conversation's language, per `base-conduct` rule 8.
