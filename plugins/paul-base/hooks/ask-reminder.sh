#!/usr/bin/env bash
# paul-base UserPromptSubmit hook.
#
# Repeats the trigger of base-conduct rule 1 next to every prompt the user types. The full rules
# arrive once, at session start (session-start.sh); a typed "ask me questions" works better than
# that because it sits in the current turn. This puts the rule there too.
# Plain stdout from a UserPromptSubmit hook is added to the context of that prompt.
#
# Paid on every typed prompt: keep it one paragraph, and keep it in step with rule 1 in
# skills/base-conduct/SKILL.md. hooks.json runs it through `bash`, so it needs no executable bit.
cat <<'EOF'
Reminder, base-conduct rule 1: if this prompt asks for work, look for open decisions before the first edit, draft, or state-changing command - a reading you would be guessing, or a choice the code and conventions leave open that shows in the result (scope, names or structure the user will see, which design, what to leave out). Ask them with AskUserQuestion, one decision per question, up to four per call, recommendation first, then wait. Nothing open, or the user already decided, left it to you, or said not to ask (earlier in the session counts): proceed.
EOF
