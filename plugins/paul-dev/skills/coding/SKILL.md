---
name: coding
description: How code gets written, changed and handed back in any language — what to read before the first edit, the conventions that hold across Java, TypeScript/Angular, Python, Bash and PowerShell, what a test has to assert, the security basics, the commit shape, and the specific ways AI-generated code goes wrong while looking right. Use when asked to "implement", "add a feature", "fix this bug", "refactor", "write a script", "bau das ein", "schreib mir ein Skript", "mach den Code sauber", or to review code; and when generated code was reported done but never run, a test was deleted or skipped to make the suite pass, a package or API "does not exist", or a review calls the code AI-looking — over-commented, over-abstracted, swallowing errors. Per-language detail lives in references/.
---

# Coding

The layer beneath `base-conduct` for anything that compiles or runs. `base-conduct` wins on
conduct. On style, the project wins: its `CLAUDE.md`, its formatter and linter config, and the
code already in the file. This skill fills what those leave open, and `references/` holds the
per-language part.

## The most important rule

**Code that looks finished and was never run is the failure this skill exists for.** It
compiles, reads well, the report says "done" — and the check did not happen. Developers rank
"almost right" output as their top frustration with AI code (66%, Stack Overflow survey 2025),
and Veracode's 2025 benchmark found a security flaw in 45% of AI-generated samples, with no
improvement from newer models.

The rule: **nothing is reported as done until its pass/fail check ran and the output is in the
report.** Anthropic's Claude Code best practices put it as "if you can't verify it, don't
ship it". Three shapes fake completion and are checked for by name:

1. **A test that cannot fail** — asserts nothing, asserts only not-null, or was deleted or
   skipped when it went red; GitHub's review guidance for AI code names this one explicitly.
2. **A stub in a live path** — a TODO, a hard-coded return, mock data, a placeholder string.
3. **A silent fallback** — a catch-all that logs and continues, a default that hides a failure,
   an empty list where an error belongs.

Then say what was run and what it printed, and what was not tested. "Should work" is not a
result (`base-conduct` rule 4).

## Where base-conduct rules 1 to 4 come from

They are Andrej Karpathy's four guidelines against LLM coding mistakes (post of January 2026,
packaged at https://github.com/multica-ai/andrej-karpathy-skills), generalised to all work.
In a coding session, read them literally again:

| Rule | In code it means |
|---|---|
| 1 Ask | Two readings of the request give two different diffs: ask before writing either. |
| 2 Simplicity | No interface for one implementation, no config for a fixed value, no handler for an impossible input. |
| 3 Surgical | The diff contains only lines the request explains. No reformatting, no drive-by renames, no fixing adjacent lint. |
| 4 Goal-driven | The task is restated as a check that can fail — a test, a build, a curl — before the first edit. |

## Before writing

- **Read the surrounding code first**: the formatter and linter config, how errors and logging
  are done, how tests are laid out, what utilities exist. Match the file you are in; if a
  formatter exists, run it rather than hand-format.
- **Read the versions** in `pom.xml`, `package.json` or `pyproject.toml`, and the language
  reference in `references/` when writing more than a few lines. Training data is older than
  the dependency: an API remembered from an earlier version may not exist in the installed one.
- **Confirm a package on its registry before adding it.** Commercial models hallucinate a
  package name in about 5% of samples, and 43% of those names recur on every rerun (Spracklen
  et al. 2025).
- **Grep for an existing helper** (utility, HTTP client, error type) before writing one.
- **Restate the task as a check** (`base-conduct` rule 4) and, for a bug, reproduce it with a
  failing test before touching the code.
- **Plan a large change as reviewable steps.** Copy-pasted blocks rose from 8.3% to 12.3% of
  changed lines between 2021 and 2024 while refactoring fell below 10% (GitClear).

## Writing

**Names.** Full words, no abbreviations beyond the language's own (`i`, `id`, `url`). A function
is a verb phrase, a type a noun, a boolean a predicate (`isOpen`, `hasItems`). Names say what a
thing is for, not its type or how it works. Casing follows the language, see `references/`.
Identifiers are English (`base-conduct` rule 8); comments follow the project.

**Functions.** One job, one level of abstraction, readable without scrolling. Guard clauses
first, then the happy path. A boolean parameter that switches behaviour is two functions. More
than three or four parameters is a small object or record.

**Comments.** Why, never what. No narration ("increment the counter"), no commented-out code, no
"generated by" markers, no TODO without an owner or issue.

**Errors.** Fail loudly at the boundary where input arrives — HTTP, file, CLI — and trust
internal calls. An error message names what failed and with which value. Never catch and
continue; never return a default that hides a failure.

**Values.** No magic numbers or strings inline; a named constant, defined once.

## Testing

- A test's name states the behaviour: `returnsEmptyWhenNoMatches`,
  `test_rejects_negative_amount`. Arrange, act, assert, in that order.
- One behaviour per test. Prove it can fail: break the code once and watch it go red.
- Test through the unit's public boundary. Do not mock what you own.
- Run the whole suite, not only the new test, before reporting.
- Frameworks and their conventions per language are in `references/`.

## Security basics

- **No secrets in code or in history.** Environment variables or an ignored secrets file.
  Before finishing, grep the diff for `key`, `token`, `password`, `secret`.
- **Parameterised queries only.** Never build SQL, JPQL or a shell command by concatenating
  input.
- **Validate and bound input at the trust boundary** — type, size, range — and encode output
  for where it goes (HTML, shell, SQL).
- **Least privilege by default.** No `chmod 777`, no disabled TLS verification, no
  `--no-verify`, no root in a container without a reason.
- **A new dependency** exists on its registry, is maintained, has a compatible licence, and
  gets a pinned version. Do not add one for what the standard library does in ten lines.

These five are the minimum for every change. Anything that authenticates, authorises, stores
secrets or personal data, exposes an endpoint, builds a query or shell command from input, handles
uploads, encrypts, or adds a dependency loads `secure-coding` in this plugin: 32 never/instead
rules with the evidence behind each, and the second pass that has to run before "done".

## Git and commits

- One logical change per commit, reviewable in one sitting. Look at `git log --oneline -20`
  and match the repository's message style.
- Subject in the imperative, under about 72 characters, saying what and why, not "fix" or
  "update". The body carries the why when it is not obvious.
- Before proposing a commit, `git status` shows only the intended files: no build output, no
  secrets, no formatter churn in files the request did not touch.
- Committing and pushing happen only when the user asks: the commit is their step (`base-conduct`
  rule 9), the push reaches beyond this machine (rule 5). No `--no-verify`, no rewriting
  published history. Offer the exact `git add` / `git commit` lines instead.

## Per language

| Stack | Read | Format and lint with |
|---|---|---|
| Java 25, Spring Boot 4 | `references/java.md` | the project's formatter plugin; `mvn verify` |
| TypeScript, Angular | `references/typescript-angular.md` | Prettier; `ng lint` (typescript-eslint) |
| Python | `references/python.md` | `ruff format`; `ruff check` |
| Bash, PowerShell | `references/shell.md` | `shellcheck`, `shfmt`; `Invoke-ScriptAnalyzer` |

Read the reference when writing or reviewing more than a few lines in that language. Each one
lists the conventions, the current toolchain, and the language-specific ways AI code goes wrong.

## Boundaries

- No commit, push, deploy, install into a shared environment, or migration without the user
  naming it (`base-conduct` rules 5 and 9).
- Pre-existing lint or style violations outside the change are mentioned, not fixed
  (`base-conduct` rule 3).
- A failing test is never deleted or skipped to make the suite pass; that decision is the user's.
- Where the project's `CLAUDE.md`, formatter or linter disagrees with this skill, the project
  wins in that project.

## Sources

- Anthropic, *Claude Code: Best practices*: https://code.claude.com/docs/en/best-practices
- Stack Overflow Developer Survey 2025, AI section: https://survey.stackoverflow.co/2025/ai
- Veracode, *2025 GenAI Code Security Report*: https://www.veracode.com/resources/analyst-reports/2025-genai-code-security-report/
- Spracklen et al., *We Have a Package for You!*, USENIX Security 2025: https://www.usenix.org/system/files/usenixsecurity25-spracklen.pdf
- GitClear, *AI Copilot Code Quality 2025*: https://www.gitclear.com/ai_assistant_code_quality_2025_research
- GitHub Docs, *Review AI-generated code*: https://docs.github.com/en/copilot/tutorials/review-ai-generated-code
