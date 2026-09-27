---
name: work-directory-setup
description: How to set up a work directory — a study folder, a code repository, a shared team project — so its structure takes the next item without restructuring and agents find the context they need without loading all of it. Covers container folders with one folder per item, the agent entry file (CLAUDE.md, or AGENTS.md for mixed-tool teams) with a "Read it when" table that doubles as a filing table, where status lives for one person versus a team, and what stays personal. Use when asked for a "directory structure", "folder structure", "future-proof structure", "neuen Arbeitsordner anlegen", "Ordnerstruktur", "wie soll ich das ablegen", "wo gehört das hin", "write a CLAUDE.md", "AGENTS.md", "context files for agents", "Kontextdateien für Agenten", "STAND.md", or when starting a new project, paper or repo. Also use when the structure has failed — "we have to restructure again", "the second one has no home", "wo lag das nochmal", "the agent doesn't find it", "every session starts from zero", "CLAUDE.md is too long", or a fact that exists somewhere but was not found.
---

# Work directory setup

How to lay out a work directory and its agent context so new work has an obvious home and a
session with no history can resume from the files alone. `base-conduct` wins on conduct; a
folder's own entry file (`CLAUDE.md` / `AGENTS.md`) wins for that folder over this skill.

## The most important rule

**A fact is filed where the next reader will look for it, not where it was first needed.** Filing
it in the item that happened to need it is a silent loss: nothing looks broken, and the next item
never finds it. In a study folder, a course's accreditation model and the reading notes on a
source both sat inside an item folder for a session before being moved to the reference files
that the next paper reads.

The mechanism that prevents it is the **"Read it when" table** in the entry file (below). The same
table answers "where do I write this?". A new kind of file that is not added to the table is a file
no future session will read.

More dead ends, each observed:

- **A flat layout for things that recur.** A study folder had an item folder at the top level
  until a second item of that kind and a second project were in sight. Once they were, everything
  moved into containers, and protocol files still name the old paths. Build the container the first
  time an item of a recurring kind appears, not the second time.
- **A second copy of the context.** A study folder kept files both in git and in the Claude app's
  project knowledge. The copy drifted, and a stale copy that looks authoritative is worse than
  none. There is one source of truth, the working tree. Any deliberate exception is named with
  its trigger for updating it.
- **Carrying a structure over by analogy.** A study folder numbers its course folders (`01-`, `02-`)
  because semester order matters there. In a game project the games have no order, so numbering
  them only adds noise. Check that the reason exists before copying the form.
- **Moving a file that a tool generates at a fixed path.** In a Unity multiplayer project, Netcode
  for GameObjects recreates `Assets/DefaultNetworkPrefabs.asset` at its configured path if the file
  is moved away (`NetworkPrefabProcessor.GetOrCreateNetworkPrefabs`), which leaves two prefab lists.
  Before moving anything generated, find the generator's path setting.
- **Empty containers vanish.** Git does not track empty folders. A container that should exist from
  the start holds a placeholder: a `README.md` with the item's key facts (as in a study folder's
  `04-Kurse/`), or a `.gitkeep` where a README would get in the way. Unity, for example, imports
  every `.md` inside `Assets/` but ignores dotfiles.

## Before building anything

Establish these facts first, by reading or by asking (`base-conduct` rule 1):

| Question | Why it matters |
|---|---|
| Who works here: one person or a team? | Decides where status lives and which rules may be written into shared files |
| Which agent tools do they use? | Claude Code only: `CLAUDE.md`. Mixed: `AGENTS.md`, plus a `CLAUDE.md` that only contains `@AGENTS.md` |
| Which kinds of item will recur? | Each recurring kind gets a container |
| Does order matter between items? | Only then number them |
| What does the tooling own? | Generated files, required folder names, directories a tool imports |
| Is there an existing layout? | Restructuring an existing folder is a migration, so ask before moving anything |

## Layout

1. **One container per recurring kind of item, one folder per item inside it.** For example
   `02-<Kind>/01-<Kind>-1/`, or `Assets/_Project/Games/<Game>/`. Each new item goes into its
   container and, if numbered, continues the numbering.
2. **One place for rules that hold across all items.** In a study folder that is `00-Referenz/`.
   In a code repo it is a `Docs/` folder, or a `Core/` folder for shared code.
3. **Create the containers now; create a subfolder when its first file arrives.** A study folder
   created all ten course folders in one go, so the numbering was settled once. It creates
   `recherche/` and `_rohdaten/` inside a paper folder only when their first file exists.
4. **A fixed vocabulary of subfolder names**, identical in every item, so anyone knows where to look
   without being told.
5. **Own work in one wrapper, apart from what tools and imports drop in.** Everything outside the
   wrapper is not edited.
6. **A file keeps one name forever.** No `_v2`, `_final`, `_new` or dates in names; the versions
   live in git.

## The entry file

Keep it short. It loads in every session and costs context whether or not it is relevant. The
long material goes into files that the table points to.

| Section | Holds |
|---|---|
| What this is | Purpose, stack or programme, language of produced text, a **Status:** date |
| Rules for every change | The handful of rules that hold in every task. One line each |
| Read it when | Table: file → the situation in which to read it. Also the filing table |
| Where new things go | New item → its container; new fact → the file listed for it; new kind of file → a new row |
| Status | Where the current state lives and when it is updated |

Rows for per-item files use a placeholder: `<Arbeit>/Literatur.md` or `Docs/Games/<Game>.md`. That
row is the rule for every future item, not only the existing ones.

`README.md` is for humans (setup, structure) and the entry file is for agents. Neither restates the
other; each points to the other.

A **per-folder entry file** exists only where that folder has rules the root does not. It starts
with what to read first and states that it overrides the root file for its own folder. Claude Code
loads a nested `CLAUDE.md` when it works on files in that subtree.

## Status: one person versus a team

| | One person | Team |
|---|---|---|
| Where | `STAND.md` in the item folder, the start-here file | A dated `## Status` section at the end of each part's doc, updated by whoever owns that part |
| Updated | At the end of every session, and committed | In the same commit as the change it describes |
| Why | One writer, so one file is the fastest to resume from | One file that everyone rewrites every session would become a constant merge conflict |

The team column is a design decision (a Unity multiplayer project, 27.09.2026), not yet an observed
result. If it fails, record how here.

## Shared versus personal

In a team repo, the entry file is read by **every** member's agents. It holds team rules only. The
following stay in each person's user-level config, which for the user is paul-base:

- who commits and who pushes
- the session-closing ritual ("Was du tun musst")
- conversation language and personal review habits

Before copying a rule from a single-person folder such as a study folder into a shared one, ask
whether it binds the whole team or only its author.

## Moving existing files

Only after an explicit yes, because this is a migration.

- Moves go in their own commit, containing renames only. Content edits go in a separate commit, so
  git can still follow each file's history.
- Move with the tool that owns the file's identity. In Unity that is the Editor, or `git mv` of the
  asset together with its `.meta`.
- Merge or finish open branches that touch the moved files first.
- Verify with the tool itself: build or compile. Then check that no reference points at an old path.

## Verify the setup

- Every file named in the "Read it when" table exists, apart from placeholder rows for future items.
- Every doc in the reference folder appears in the table.
- Every container exists in git (it holds a placeholder while empty).
- `git status` is clean once the setup is committed.

## Boundaries

- Do not restructure an existing folder, and do not move or delete a file, without an explicit yes.
- Create containers, the entry file, `README.md` and the reference docs, and nothing speculative
  beyond them. Empty template files for future items are not created. Their row in the table is
  enough.
- Never write personal workflow rules into a file that other people's agents read.
- The folder's own entry file wins over this skill for that folder. `base-conduct` wins on conduct.
