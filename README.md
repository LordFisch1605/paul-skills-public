# paul-skills-public

Claude Code skills, packaged as a plugin marketplace: working rules for every session,
delegating to subagents and verifying what comes back, reviews, and writing code — secure code
included.

They are exported from a private skill set with the personal context removed, and re-exported
when the originals change.

## Install

In a Claude Code session:

```
/plugin marketplace add LordFisch1605/paul-skills-public
/plugin install paul-base@paul-skills-public
/plugin install paul-dev@paul-skills-public
```

Choose **user scope** when prompted.

Know what `paul-base` does before installing it: it ships a `SessionStart` hook that injects the
`base-conduct` rules into **every** session, in every folder, and a `UserPromptSubmit` hook that
adds a one-paragraph reminder to ask before building to every prompt you type. That is the point
of the plugin — and the reason to read `plugins/paul-base/skills/base-conduct/SKILL.md` first.

## Skills

| Plugin | Skill | What it is for |
|---|---|---|
| `paul-base` | `base-conduct` | Standing working rules for every task in every folder |
| `paul-base` | `delegation` | How the main model decides whether to hand work to a paul-base subagent instead of doing it in-session |
| `paul-base` | `review` | How to review a piece of work |
| `paul-base` | `troubleshoot` | How to troubleshoot a broken command or a divergent environment on a Windows work machine (Windows 11, PowerShell 5.1) |
| `paul-base` | `voice-profile` | Build or extend a voice profile |
| `paul-base` | `work-directory-setup` | How to set up a work directory |
| `paul-dev` | `coding` | How code gets written, changed and handed back in any language |
| `paul-dev` | `draw-code` | Turn code the user did not write line by line into a picture they can learn from |
| `paul-dev` | `secure-coding` | The security layer beneath `coding` for any application code Claude writes or reviews |

`paul-base` also ships four subagents — extractor, implementer, reviewer, researcher — that the
`delegation` skill hands work to.

## License

[PolyForm Shield 1.0.0](https://polyformproject.org/licenses/shield/1.0.0) — see `LICENSE`, which
is the authoritative text. In short: you may use, change and share these skills for any purpose,
including at work, except to provide a product that competes with them — selling them, or
offering your own skills pack built from them, even for free.

Parts of `base-conduct` adapt MIT-licensed text; `THIRD-PARTY-NOTICES.md` says which, and those
parts stay under MIT.
