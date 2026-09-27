#!/usr/bin/env bash
# paul-base SessionStart hook.
#
# Injects the base-conduct rules into every session, in every folder, on every machine where
# paul-base is installed at user scope. This is what makes base-conduct actually always-on:
# skills are never auto-loaded (Claude Code only offers a skill's name+description and the model
# chooses), so without this the rules only fire where a folder's CLAUDE.md points at them.
# Plain stdout from a SessionStart hook is added to the session context.
set -euo pipefail

skill="${CLAUDE_PLUGIN_ROOT}/skills/base-conduct/SKILL.md"
[ -r "$skill" ] || exit 0   # never break a session if the file is missing

cat <<'EOF'
The base-conduct rules are in effect for this session, in every folder, whether or not the
current task matches any skill description. They are not situational. A folder's own CLAUDE.md
may override a specific rule for that folder; silence is not an override. The rules follow.

EOF

# Print the skill body, skipping the YAML frontmatter (everything up to the second '---' fence).
awk 'f>=2{print} /^---[[:space:]]*$/{f++}' "$skill"
