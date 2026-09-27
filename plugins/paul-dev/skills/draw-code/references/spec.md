# Spec shapes

`scripts/render.py` takes one JSON file. Everything below is that file's schema, plus a worked
example per mode. Unknown keys are ignored; missing optional keys just render nothing.

## Shared header keys

Both modes use these:

| Key | Required | What it is |
|---|---|---|
| `mode` | yes | `"flow"` or `"class"` |
| `title` | yes | The page name. A question for `flow`, the class name for `class` |
| `subtitle` | no | One sentence under the title |
| `source` | no | File name, shown in the eyebrow |
| `lines` | no | Line count, shown next to the source |
| `provenance` | yes | `"parsed"` or `"read"` — picks the banner, see below |
| `facts` | no | Short strings shown as chips. Real numbers only |

`provenance` is not decoration. `"parsed"` prints a green banner saying line ranges and call
edges were read off the syntax tree; `"read"` prints an orange one warning they were read by a
model and may be wrong. Set `"read"` for every language the extractor does not cover. Claiming
`"parsed"` for facts a model typed is the one dishonest thing this skill can do — and in class
mode on a Python source, `render.py` now catches it: it re-runs the extractor, compares the line
ranges, and replaces the banner with a warning if they disagree.

In **flow mode** `"parsed"` never prints the green banner, because flow mode renders no signatures
and no call edges and its step refs are typed by hand. It prints an orange one saying the steps
were written against a parsed file but not themselves verified. That is accurate; do not try to
dress it up.

## `flow` mode

| Key | Required | What it is |
|---|---|---|
| `flowLabel` | no | Small grey line above the panels, e.g. `one call to step() - L325-362` |
| `steps` | yes | 3–8 objects, in execution order; four to six reads best |
| `steps[].n` | no | Badge number; defaults to position |
| `steps[].title` | yes | Two or three words, ≤18 chars |
| `steps[].code` | no | The call this step is, ≤30 chars |
| `steps[].ref` | no | `L334` or `L340-344` |
| `steps[].in` | no | What goes in, ≤24 chars, drawn as an orange arrow |
| `steps[].out` | no | What comes out, ≤24 chars, drawn as a blue arrow |
| `zoom` | no | One step opened up |
| `zoom.fromStep` | no | 1-based step number the bracket rises from |
| `zoom.title` / `zoom.ref` | no | Labels for the zoom band |
| `zoom.gates` | no | Up to 3; a 4th is silently dropped, so do not write one |
| `zoom.gates[].exit` | no | A red escape route out of the gate |
| `zoom.gates[].note` | no | A blue note instead, when the gate has no exit |
| `zoom.footnote` | no | One grey line under the gates |

Text longer than the caps above is truncated with an ellipsis rather than overflowing. Write to
the cap; do not rely on the truncation.

```json
{
  "mode": "flow",
  "title": "One tick of the FTL combat sim",
  "subtitle": "What happens between calling step() and getting the next observation back.",
  "source": "ftl_combat_sim.py", "lines": 603, "provenance": "parsed",
  "facts": ["32 actions", "42-float obs vector"],
  "flowLabel": "one call to step() - L325-362",
  "steps": [
    {"n": 1, "title": "you act",     "code": "_apply(player, a)",    "ref": "L334",
     "in": "one of 32 actions",   "out": "power, aim or crew moved"},
    {"n": 2, "title": "enemy acts",  "code": "_enemy_ai()",          "ref": "L337",
     "in": "ENEMY_POWER_TARGET",  "out": "one system, +/- 1"},
    {"n": 3, "title": "physics",     "code": "_charge_and_fire x2",  "ref": "L340-344",
     "in": "both ships",          "out": "hull damage, t += 1"},
    {"n": 4, "title": "reward",      "code": "dealt - taken - 0.01", "ref": "L349",
     "in": "hull before vs after","out": "obs, reward, done, info"}
  ],
  "zoom": {
    "title": "zoom: what one shot has to survive",
    "ref": "_resolve_shot - L269-291", "fromStep": 3,
    "footnote": "two ways out before hull is ever touched",
    "gates": [
      {"n": 1, "title": "evasion", "code": "rng(1,100) <= evasion", "exit": "dodged - 0 dmg"},
      {"n": 2, "title": "shields", "code": "pierce >= layers ?",    "exit": "absorbed, strips 1 layer"},
      {"n": 3, "title": "hull",    "code": "hull -= damage",        "note": "+ the aimed system loses power"}
    ]
  }
}
```

## `class` mode

| Key | Required | What it is |
|---|---|---|
| `className` | no | Heading over the method list |
| `openOn` | no | Method name to show first. Pick the most interesting one, not the first |
| `methods` | yes | In file order |
| `methods[].name` | yes | |
| `methods[].lines` | yes | `"325-362"` |
| `methods[].takes` | no | Parameter list without `self` |
| `methods[].returns` | no | |
| `methods[].calls` | no | Either a flat list, or the extractor's `{"self": [...], "module": [...]}` |
| `methods[].note` | no | One sentence worth reading |

`calls` accepts the extractor's shape directly, so `raw.json` can be piped through with only
`note` added. Module-level calls render with a dashed border to mark that they leave the class.

```json
{
  "mode": "class",
  "title": "FTLCombatSim", "className": "class FTLCombatSim",
  "subtitle": "Every method on the combat environment, with the line ranges its syntax tree reports.",
  "source": "ftl_combat_sim.py", "lines": 603, "provenance": "parsed",
  "facts": ["13 methods", "32 actions"], "openOn": "step",
  "methods": [
    {"name": "step", "lines": "325-362", "takes": "action_index",
     "returns": "obs, reward, done, info",
     "calls": {"self": ["_apply", "_enemy_ai", "get_obs"], "module": []},
     "note": "An illegal index is silently turned into a noop - the mask is meant to prevent it."}
  ]
}
```

## Building a class spec from the extractor

```bash
python "<skill base directory>/scripts/extract_py.py" app/sim.py --class Engine --out raw.json
```

`raw.json` gives `classes[0].methods[]` with `name`, `lines`, `takes`, `returns`, `doc` and
`calls`. Copy those through unchanged, replace `doc` with a real `note` where the docstring is
thin or missing, add the header keys, and render. Do not retype the facts.

## Failure modes the renderer catches

- `mode` that is not `flow` or `class` → exits 2
- `flow` with no `steps`, or `class` with no `methods` → exits 2
- Missing optional keys → that element is simply not drawn
- `zoom.fromStep` outside the steps that exist → clamped to the nearest real step
- class mode, `"parsed"`, a readable `.py` `source` → line ranges re-checked against the file;
  a mismatch prints a warning on stderr and swaps the banner for one that says so

That last check is the only one that can catch a false `"parsed"`, and it only works for Python
class mode. Everywhere else — flow mode, and every other language — `provenance` is a declaration
nothing verifies, so declare it honestly.
