---
name: voice-profile
description: Build or extend a voice profile — a reference file that lets any AI model draft and check text in one specific person's voice for one specific purpose (academic writing, motivation letters, correspondence). Use when asked to "capture my voice", "write a my-voice file", "learn how I write", "create a writing style profile", "add this to my voice file", or when a draft comes back with "this doesn't sound like me". Also use when a person's edits to a draft should be harvested into an existing profile. Covers deriving traits from real material as verbatim evidence, separating what carries over from what gets dropped, marking extrapolations, and the correction-pair loop that makes a profile sharpen with use.
---

# Voice profile

A **voice profile** is a reference file describing how one person writes for one purpose, built
from that person's real text and quoting it as evidence. It is data, not instruction: a drafting
session reads it, the profile itself does nothing.

This skill is the method for producing and maintaining one. It is register-agnostic and
language-agnostic — the profile may be German, English, academic, personal, or professional.

**Authority:** where a profile and this skill disagree about that person, the profile wins. It
holds the evidence; this file only holds the procedure.

## The most important rule

**Everything in a profile is either a verbatim quote or explicitly marked as an extrapolation.
There is no third category.**

The failure this prevents is the one that looks most like success: writing a fluent, plausible
description of how the person writes, assembled from what a good writer in that genre does. It
reads well, the person nods at it, and it steers every future draft toward a generic voice while
claiming their authority. A profile whose claims cannot be traced to a quote is worse than no
profile, because drafts written from it are wrong *confidently*.

So: each trait carries an indented verbatim quote, typos included. Anything that goes beyond
what the quotes support is labelled *extrapolation* in the line where it appears.

**The second rule, close behind: source register does not transfer.** Material is almost always
informal — chats, messages, notes — because that is what exists in volume. What transfers from
informal material is **thinking habits**: how they concede, weigh, quantify, sequence context. The
*surface* — emoji, lowercase, fragments, intensifiers — does not transfer to any target register
and must be listed as dropped, explicitly, or the profile becomes "their chat voice in a suit".

## 1. Decide the target register first

Before reading any material, settle what the profile is *for*, and write that decision into
section 1 of the file as a table: which formats it governs, what the grammatical subject is,
what the tone is, and how self-reference works.

If profiles for other registers already exist for this person, the table lists them all
side by side, including the raw source register as its own column. Naming the neighbours is what
keeps a reader from applying the wrong one — and the table is where the reader learns that the
raw register is a *source*, not an option.

Where the target register has an external rulebook (a style guide, a university's requirements,
a programme's brief), name it here and say plainly that it outranks the person's habits. Note any
place where their natural habit *collides* with that rulebook — that collision is the highest-value
paragraph in the whole file.

## 2. Gather the material

Take what exists rather than commissioning something new; text written to be read by a real
person is worth more than text written for the profile.

Aim for roughly 1,000 words minimum, from at least two occasions. Below that, traits cannot be
told apart from accidents. Record in the file, near the top: how many words, what kind of text,
which time periods, and who the audience was. That paragraph is what lets a later reader judge
how far to trust the rest.

Details on sourcing and what each material type does and does not support:
`references/intake.md`.

## 3. Build the file

The section skeleton — carries-over, drops, mechanics, checklist, limits — is in
`references/file-structure.md`. Follow it; the ordering is doing work.

Two things while writing:

- **Quantify.** "Four instances of *allerdings* in 1,100 words" is usable; "tends to qualify" is
  not. Counts also make the next revision measurable.
- **Say what each trait becomes.** A trait is not a description, it is an instruction: give the
  raw quote, then the same content rendered in the target register. That pair is what a drafting
  session actually copies.

## 4. The correction-pair loop

This is the part that makes a profile improve rather than ossify, and the part most often skipped.

Every edit the person makes to a draft is evidence — better evidence than the source material,
because it is their target register, not an inference about it. Record each as an
**original/final pair**: what was drafted, what they changed it to, and the one-line rule it
implies.

Three rules govern the loop:

1. **Record in the session the correction happens**, not after the document ships. A correction
   not written down is lost, and the next draft repeats the mistake it already paid for.
2. **Read the pairs before drafting, not after.** Drafting first and reconciling afterwards costs
   a whole revision round. This is the single most expensive ordering error in the method.
3. **At roughly five pairs, the pairs become the primary reference** and the a-priori sections
   drop to secondary — they apply only where the pairs are silent. Write that switch into the
   file as a dated status note, and list the known contradictions by name. Real behaviour on a
   real document beats an inference from chat material every time.

Also record the interventions that are **not** style rules — a fact correction, a scope change, a
one-off. Left unmarked, they get generalised into rules the person never held.

## 5. Privacy

A profile quotes private material verbatim, often including third parties who never agreed to it.

Default: **local only.** Put a lock notice at the top of the file, exclude it via `.gitignore`,
and keep it out of any reachable remote. Before quoting, strip anything about a third party's
private life, and drop material the person would not want re-read in a work context — the
profile needs their *sentence structure*, not their disclosures.

This applies to this skill too: worked examples are referenced by path, never pasted in.

## 6. Extending this method

When building a profile teaches something the method did not know — a material type that behaved
unexpectedly, a section that turned out useless, a failure worth naming — append it to
`references/lessons.md` in the same session, as a dated entry with the concrete case that
produced it.

Appending to the log is automatic and needs no permission. **Promoting a log entry into a rule in
this `SKILL.md` needs a yes**, because a rule here changes every future profile, and because one
case is a coincidence. Two entries pointing the same way are a pattern worth proposing.

`SKILL.md` stays under ~2,000 words; the log grows instead.

## Boundaries

- **Do not write the profile from an impression of the person.** No material, no profile — say so
  and ask for text.
- **Do not invent quotes**, tidy up typos inside quotes, or merge two utterances into one.
- **Do not send anything written from a profile.** Motivation letters, applications and academic
  submissions are the person's own declaration; the draft is theirs to check and theirs to send.
- **Do not delete a trait because the current draft contradicts it.** Record the contradiction as
  a pair and let the threshold in section 4 resolve it.

## Checklist

- [ ] Target register decided and tabled *before* the material was read?
- [ ] Data basis stated — word count, text type, periods, audience?
- [ ] Every trait carries a verbatim quote; everything beyond them marked *extrapolation*?
- [ ] Source-register surface features listed as dropped, not carried over?
- [ ] Each carried trait shown as a raw → target-register pair?
- [ ] Counts where counts were possible?
- [ ] A limits section saying what the profile does *not* yet cover, and what would close it?
- [ ] Lock notice and `.gitignore` entry if private material is quoted?
- [ ] Anything learned appended to `references/lessons.md`?
