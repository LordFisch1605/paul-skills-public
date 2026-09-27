# Choosing what to draw

The scripts cannot get this wrong for you. Layout and line numbers are mechanical; deciding
which flow is worth a picture, and which six of its forty steps matter, is the whole job.

## Flow mode: picking the flow

A flow is worth drawing when **the order is the thing you would otherwise have to hold in your
head**. Good candidates, roughly in order of how often they are the right answer:

- The main loop — `step()`, a tick, a request/response cycle, a render pass.
- What one button does, end to end, from the handler to the thing that persists.
- Startup: what is built, in what order, before anything can run.
- The path a piece of data takes from input to storage, or from storage to screen.

Bad candidates: anything with no real ordering (a utility module), anything that is one call
deep (prose is faster), and "the whole application" (that is several flows, drawn separately).

When the request is vague — "draw the project" — pick the flow that the project exists to run,
say which one you picked and why, and offer the others. Do not draw three.

## Flow mode: picking the steps

Start from the actual call chain, then **collapse**. The chain from a click to a save might be
thirty calls; the picture gets four to eight. Collapse by asking what changes state:

- Several calls that together do one describable thing are **one step**
  (`_charge_and_fire` twice plus `_regen_shields` twice plus the tick counter = "physics").
- A call that only forwards to another is **not a step** — draw what it forwards to.
- A guard that can end the flow early is **a gate**, not a step. Gates belong in the zoom.
- Anything the reader would not be surprised by earns its place only if the order matters.

**Write `in` and `out` for every step.** If you cannot say what goes in and what comes out,
the step is either too big or not really a step. This is the field that makes the picture
teach something, and it is the one that gets skipped when the source is unfamiliar.

## Flow mode: the zoom

At most one step is opened, into at most three gates. Use it when a single step contains the
rules that actually decide the outcome — a shot resolving against evasion then shields then
hull, a request passing auth then validation then the handler.

Give a gate an `exit` when it can end things early, and make the exit text say what the caller
gets (`dodged - 0 dmg`), not that it returned. A gate with no early exit gets a `note` instead.

If two steps both deserve a zoom, that is two pictures.

## Class mode: which methods

Include **every** method, in file order. This is a reference, not an essay — the value is that
nothing is missing, and the list is cheap. Do not filter to "the interesting ones"; the reader
came because they do not yet know which ones are interesting.

Set `openOn` to the method that explains the class. Usually the one with the most call edges,
which is a decent proxy for "the one that orchestrates". Never leave it on `__init__`.

## Notes: the one sentence per thing

The note is the only place judgement shows. It earns its space when it says something the
signature does not.

| Write this | Not this |
|---|---|
| An illegal index is silently turned into a noop — the mask is meant to prevent it. | Executes one step. |
| `reveal_weapons=False` would blank the list, but both call sites pass `True`. | Builds the observation for one ship. |
| Charge advances at 1.15× when the station is manned. | Charges weapons and fires them. |
| Not exported, and nothing in the app calls it. | Helper function. |

Rules that keep notes useful:

- Restating the name is worse than no note. Leave it empty instead.
- A docstring is a starting point, not a note. It describes intent; the note should describe
  what the code does, especially where those differ.
- Dead code, dormant flags and silent fallbacks are the highest-value notes there are. Say so
  plainly when you find one.
- One sentence. If it needs two, it needs a zoom or its own picture.

## Facts chips

Three to six, and every one a number or a name you can point at in the source or in a run.
`32 actions`, `42-float obs vector`, `13 methods`. Never `well structured`, never `fast`.

Prefer a number you produced by **running** the code over one you counted by reading it. A
three-line script that imports the module and prints two lengths is worth more than a careful
count, and it takes less time.

## What to say when handing it over

Name the file path, what question the picture answers, which facts were machine-extracted and
which were read, and anything you noticed but did not draw. If you picked one flow out of
several, say which ones you did not draw — that is the reader's cue to ask for another.
