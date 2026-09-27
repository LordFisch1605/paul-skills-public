# CLAUDE.md

Standing instructions for every session on this machine.

## Follow base-conduct at all times

The `base-conduct` skill from the `paul-base` plugin is injected into context at session start
by that plugin's SessionStart hook. Its rules apply in every folder, whether or not the current
task looks like it matches the skill's description — it is not situational.

If those rules are **not** already present in context — the hook isn't installed or isn't
running — load the `base-conduct` skill yourself before doing anything else.

The rules live in the plugin, not here. Do not restate them in this file — one copy,
versioned with everything else.

## Folder rules

A folder's own `CLAUDE.md` adds context and may override `base-conduct` **for that folder**.
Where a folder says nothing, `base-conduct` applies.
