# Bash and PowerShell

Google's Shell Style Guide and ShellCheck govern Bash; PowerShell Practice and Style and
PSScriptAnalyzer govern PowerShell. Scripts for a locked-down Windows machine target Windows
PowerShell 5.1, not 7. Troubleshooting a command that breaks there is `paul-base:troubleshoot`,
not this file.

## Toolchain, September 2026

- Bash: `shellcheck script.sh` before reporting; `shfmt -i 2 -w` as formatter.
- PowerShell 7.6 is current LTS; the locked-down Windows machine runs 5.1, so anything for it
  avoids 7-only syntax.
- PowerShell: `Invoke-ScriptAnalyzer -Path .` before reporting.

## Bash

- `#!/bin/bash` as shebang. Past ~100 lines, or non-trivial control flow, use Python instead.
- `[[ ... ]]` over `[ ... ]`; `$(cmd)` over backticks.
- Quote every expansion: `"${var}"`, `"$(cmd)"`; unquoted expansions word-split, glob.
- `cd "$dir" || exit 1`; unchecked `cd` runs everything after it in the wrong directory.
- `local` for function variables, on its own line before a `$(...)` assignment — `local
  x=$(cmd)` swallows the exit code.
- `lower_case_with_underscores` for variables and functions; `UPPER_CASE` plus `readonly` for
  constants and exported values.
- A `main` function called as `main "$@"` on the last line once functions exist; 2-space
  indent; 80 columns.
- `set -euo pipefail` at the top is the usual opener and not a safety net: `set -e` skips
  `if`/`&&`/`||` conditions, `$(...)` without `inherit_errexit`, and non-final pipeline
  commands without `pipefail`. Check exit codes explicitly where it matters.
- Never parse `ls`; loop over a glob, or `find -print0 | while IFS= read -r -d '' f`.
- `printf` over `echo` for variables or escapes; `trap cleanup EXIT` for temp files.

## PowerShell

- `Verb-Noun` names, approved verb only: `Remove-`, never `Delete-`; check with `Get-Verb`.
- Full cmdlet names, no aliases: `Get-ChildItem` not `ls`/`gci`, `ForEach-Object` not `%`,
  `Where-Object` not `?`.
- Data goes to the pipeline (`Write-Output` or the object); progress to `Write-Verbose`;
  `Write-Host` only in `Show-*` functions that paint the screen.
- `$PSScriptRoot` for script-relative paths, never `.\`.
- `[CmdletBinding()]` on every function; `SupportsShouldProcess` with
  `$PSCmdlet.ShouldProcess()` on anything that changes state.
- `Set-StrictMode -Version Latest` at the top of a script.
- A non-terminating error skips `catch`: use `-ErrorAction Stop`, or
  `$ErrorActionPreference = 'Stop'` before any `try`.
- 7-only, absent in 5.1: `&&`/`||` chains, ternary `? :`, `??`/`??=`. In 5.1: `A; if ($?) { B }`,
  `if/else`, `if ($null -eq $x)`.
- Encoding differs: 5.1 `Out-File`/`>` write UTF-16 LE, `Set-Content`/`Add-Content` write the
  system ANSI page; 7 writes UTF-8 without BOM. In 5.1 pass `-Encoding utf8` for files other
  tools will read.
- `2>&1` on a native executable in 5.1 wraps each stderr line in a `NativeCommandError`, sets
  `$?` false even at exit 0; fixed in 7.1+. Don't redirect native stderr in 5.1.
- `New-Item -Force` truncates an existing file; check `Test-Path` first.

## What AI code gets wrong here

| Does | Instead |
|---|---|
| Unquoted `$var` or `$(cmd)` | `"${var}"`, `"$(cmd)"` |
| `cd dir` with no check | `cd dir \|\| exit 1` |
| `for f in $(ls)` | `for f in ./*` or `find -print0` |
| Relies on `set -e` inside `if` or a pipeline | Explicit `\|\| exit`, `pipefail`, or test the exit code |
| Backticks | `$(...)` |
| Bash arrays or `local` under `#!/bin/sh` | `#!/bin/bash`, or POSIX sh throughout |
| `echo -e "..."` | `printf '...\n'` |
| Aliases `ls`, `cat`, `%`, `?` in a `.ps1` | Full cmdlet names |
| `Write-Host` for a value the caller needs | Emit the object |
| `A && B` in a script that must run on 5.1 | `A; if ($?) { B }` |
| `Delete-Thing`, `Kill-Process` | `Remove-Thing`, `Stop-Process` |
| `try { Get-Item $p } catch` with no `-ErrorAction Stop` | Add it, or the catch never runs |
| `Invoke-Expression "cmd $userInput"` | Call the cmdlet with parameters, or `& $exe @args` |
| `Set-Content file` in 5.1 with no `-Encoding` | `-Encoding utf8` |

## Sources

- Google Shell Style Guide: https://google.github.io/styleguide/shellguide.html
- ShellCheck SC2086: https://github.com/koalaman/shellcheck/wiki/SC2086
- ShellCheck SC2164: https://github.com/koalaman/shellcheck/wiki/SC2164
- BashFAQ/105 on set -e: https://mywiki.wooledge.org/BashFAQ/105
- ParsingLs: https://mywiki.wooledge.org/ParsingLs
- PowerShell Practice and Style: https://poshcode.gitbook.io/powershell-practice-and-style/
- Approved verbs: https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands
- PSScriptAnalyzer rules: https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/rules/readme
- Differences from Windows PowerShell 5.1: https://learn.microsoft.com/en-us/powershell/scripting/whats-new/differences-from-windows-powershell
- about_Character_Encoding: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding
