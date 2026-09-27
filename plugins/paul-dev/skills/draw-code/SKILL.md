---
name: draw-code
description: Turn code the user did not write line by line into a picture they can learn from — either a storyboard of one execution path ("what does this actually do") or a browsable method reference for one class or file ("how does this thing work"). Two separate modes, run on demand, never automatically. Use when asked to "draw this", "draw the project", "zeichne mir das", "zeichne den Ablauf", "mal mir ein Schaubild", "show me what this does", "was macht diese Datei", "was macht dieses Projekt eigentlich", "what happens when I click X", "what happens when step() is called", "was passiert wenn ich X aufrufe", "explain this codebase visually", "erklär mir das mit einem Schaubild", "visualise this class", "Methodenübersicht", "Ablaufdiagramm", "I built this with AI and do not understand it", "ich verstehe den Code nicht den die KI geschrieben hat", "ich blick da nicht durch". Only for source code that is on disk and can be read. Not for architecture decision records, not for dependency or module graphs (that is a Mermaid flowchart), and not for explaining code in prose or briefing someone in writing — those are `coding` and plain conversation.
---

# Draw code

Two pictures, each answering a different question. Pick one — they are not halves of a set.

| Ask | Mode | What comes out |
|---|---|---|
| "What does this *do*?" | `flow` | A storyboard of one execution path: numbered steps, what goes in and out of each, optionally one step opened up |
| "How does this class *work*?" | `class` | A method reference: signature, line range, call edges, one note per method |

Never run both because both exist. A flow picture answers nothing about a single class, and a
method reference answers nothing about what the project does. Ask which one is wanted if the
request does not say.

## The dead ends

**Do not draw a dependency graph.** Boxes joined by import arrows was tried and rejected: it
carries almost no information a file listing does not already give, and the interesting facts —
how many actions are legal, that a flag is wired up but switched off — have nowhere to live on
it. If a module map is genuinely wanted, a Mermaid `flowchart` in the repo costs nothing and is
honest about being just a graph.

**Do not generate images.** Claude cannot. Every picture here is SVG and HTML the renderer
writes, which is also why the output is diffable and editable rather than a PNG nobody can amend.

**Do not hand-place coordinates.** `scripts/render.py` computes the layout from the data.
Writing SVG by hand looks fine on the first diagram and collides on the third.

**Do not write line numbers or call edges from memory.** They will be wrong, and they are
exactly what the reader trusts. Run the extractor. Where no parser exists, say so on the page —
the renderer has a banner for it and prints it automatically from `provenance`.

## How to run it

1. **Pick the mode** from what was asked. One flow, or one class, per run.
2. **Get the facts.**
   - Python → `python "<skill base directory>/scripts/extract_py.py" <file.py> [--class Name] --out raw.json`.
     Line ranges and signatures come off the syntax tree and cannot be wrong. **Call edges are
     narrower than they look**: it sees calls to `self.x()` and to functions defined in the same
     file, and misses calls through another object (`self.rng.randint()`), through `super()`,
     through a variable holding a function, and anything inherited. Say so if it matters.
   - Anything else (TypeScript, Svelte, Java) → read the file and write the facts yourself,
     then set `"provenance": "read"`. Verify every line number you state by grepping for the
     symbol; do not trust a number you did not just look at.
3. **Write the spec** — a JSON file. Shapes are in `references/spec.md`; which flow, which steps
   and what each note earns are judgement, covered in `references/choosing.md` for both modes.
4. **Render**: `python "<skill base directory>/scripts/render.py" spec.json --out <project>/docs/<name>.html`
5. **Look at it once** before handing it over, and say what you checked.

Both scripts are standard-library Python. No install, no node, no network. `<skill base
directory>` is the folder this SKILL.md sits in — an installed plugin lives under
`~/.claude/plugins/cache/`, not in the project, so a relative `scripts/…` path will not resolve.

In class mode on a Python source, `render.py` re-runs the extractor and compares the line ranges
the spec claims. A spec that says `"parsed"` but disagrees with the file gets a warning on stderr
and a banner on the page saying so. Do not paper over that — rebuild the spec.

## Where the output goes

Into the project being drawn, as `docs/<what-it-shows>.html` unless the user names somewhere else —
so it versions with the code it describes. Name it after the question it answers
(`what-happens-on-generate.html`, not `diagram-1.html`).

Publishing it as a shareable Artifact is an **extra, on request only**. Do not publish because
the page looks good; a page about private code becomes a link when you publish it.

## What makes a picture worth keeping

- **One picture, one question.** A storyboard that also tries to be a class reference is neither.
- **Three to eight steps, four to six is the sweet spot.** More than eight and nobody reads it;
  fewer than three and prose was the better answer.
- **State what goes in and what comes out at every step.** This is the whole reason the
  storyboard beats a call graph, and it is the part that gets skipped.
- **Say the thing a reader could not guess.** "An illegal index is silently turned into a noop"
  earns its line. "Applies the action" does not.
- **Real identifiers and real numbers**, quoted from the source. `32 actions, 28 legal at t=0`
  is worth more than the entire rest of a box.
- **Zoom once, at most.** In flow mode, one step may be opened into up to three gates. A second
  zoom is a second picture.

## The boundary

The scripts own line ranges, signatures, call edges and layout. **Claude owns judgement**: which
flow is worth drawing, which steps matter, what one sentence each step earns, what to leave out.
Do not push judgement into the scripts, and do not retype facts the scripts produce.

Claude does not commit or push the generated page, and does not publish it without being asked.

When a claim on the page and the source disagree, **the source wins** — regenerate, do not
patch the HTML. The page carries a footer saying exactly that, because a hand-edited generated
file is how these go stale.
