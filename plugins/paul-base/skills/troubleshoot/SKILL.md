---
name: troubleshoot
description: How to troubleshoot a broken command or a divergent environment on a Windows work machine (Windows 11, PowerShell 5.1) — reproducing the exact command, the absolute-path test, where.exe versus Get-Command, comparing execution policy and language mode instead of only PATH, beacon files to prove a shared filesystem view, cross-tool corroboration, and fltmc filters when two processes disagree about whether a file exists. Use when something is broken — "not recognized", "command not found", "works for you but not for me", "warum geht das bei dir und nicht bei mir", "it worked yesterday", "Test-Path says False but the file is there", or a PSSecurityException from a .ps1 shim. Windows only, not Linux.
---

# Windows troubleshooting

A method for Windows, and only Windows: **Windows PowerShell 5.1**, Windows paths, Windows
tooling (`where.exe`, `cmd.exe`, `fltmc`, the Windows certificate store). Nothing here
transfers to a Linux box. It is distilled from one session on a Windows work machine in which every wrong
explanation was asserted first and disproven later. **base-conduct** wins on how to work.

## The most important rule: absolute path first, hypothesis before assertion

- **"Not recognized" is not automatically a PATH problem.** Invoke the thing by its full path
  before theorising: `& "C:\Users\<you>\.local\bin\cn.cmd" --version`. If that works, the
  fault is PATH or PowerShell discovery. If that *also* gives `ObjectNotFound`, PATH is
  eliminated entirely and the real question is why this process cannot see this file. That
  single test was available in the first message and would have saved roughly an hour.
- **Test the hypothesis before asserting it.** "Stale terminal environment", "PowerShell
  negative-caches a failed lookup", "the tool sandbox has a copy-on-write filesystem" were all
  stated as fact and all killed by one command each — a reboot, a `$env:PATH` edit followed by
  `Get-Command`, a rerun with sandboxing disabled. Name the command that would falsify the
  guess, run it, *then* say what is true.
- **Identity is not the same question as filesystem view.** `whoami`, SID, `SessionId`,
  `quser`, `ProfileImagePath` all matching proves the two processes are the same user in the
  same session. It does not prove they see the same files.

## A command is not found, or behaves differently in two shells

1. **Reproduce the user's exact command in your own shell** — same spelling, same quoting, same
   working directory. → verify: you have the literal error text, not a paraphrase of it.
2. **Absolute-path test** (above). → verify: full path works → PATH problem; full path fails
   with `ObjectNotFound` → visibility problem, stop looking at PATH.
3. **Ask for the raw value, never a filtered diagnostic.** `$env:PATH -split ';' |
   Where-Object {...}` hides the neighbouring evidence. Ask for `$env:PATH`; filter it
   yourself afterwards.
4. **`where.exe` versus `Get-Command`.** `where.exe` is the OS PATH search, `Get-Command` is
   PowerShell's own discovery. Agreement means PATH is telling the truth. Disagreement
   localises the fault inside PowerShell — a function, an alias, or a shim it refuses to run.
5. **Compare policies, not just PATH.** Side by side from both shells: `Get-ExecutionPolicy
   -List`, `$PSVersionTable`, `$ExecutionContext.SessionState.LanguageMode`, `$env:PATHEXT`.
   The execution-policy difference sat in captured output for several rounds before anyone
   read it.
6. **Beacon files.** Write a uniquely named file from process A, `Test-Path` it from process B
   — **per directory**, not once. This is what localised the split: the beacons proved
   `~\.continue` and `~\.local\bin` shared between the two processes, and a beacon later written
   to `AppData\Roaming` round-tripped `True` from the writer while physically sitting under
   `AppData\Local\Packages\<pkg>\LocalCache\Roaming\` — never in the real `AppData\Roaming` at
   all.
7. **Packaged-app parent chain.** When a file one process wrote is invisible to another, check
   whether the writing process descends from a packaged (MSIX) app — its children inherit the
   package's filesystem redirection even though `GetPackageFamilyName` on the child returns
   `15700` (`APPMODEL_ERROR_NO_PACKAGE`); package identity is not the test, the parent chain is.
   Walk it:
   ```powershell
   $proc = Get-WmiObject Win32_Process -Filter "ProcessId=$PID"
   while ($proc) {
     Write-Output "$($proc.ProcessId) $($proc.Name) $($proc.ExecutablePath)"
     $proc = Get-WmiObject Win32_Process -Filter "ProcessId=$($proc.ParentProcessId)"
   }
   ```
   Look for `C:\Program Files\WindowsApps\` in an ancestor's path, then look for the file under
   `C:\Users\<user>\AppData\Local\Packages\<pkg>\LocalCache\Roaming\` instead of the real
   `AppData\Roaming`. Rule: never install per-user tooling into `%APPDATA%` from inside a
   packaged app's process tree — npm's default prefix is `%APPDATA%\npm`.
8. **Cross-tool corroboration.** Check the same fact through four tools, run against the same
   path:
   ```powershell
   Test-Path 'C:\Users\<you>\.local\bin'
   cmd /c dir 'C:\Users\<you>\.local\bin'
   [System.IO.Directory]::Exists('C:\Users\<you>\.local\bin')
   ```
   and, in Git Bash: `ls -la "C:\Users\<you>\.local\bin"`. Note `cmd /c dir`, not `cmd.exe
   dir` — without `/c` it opens an interactive shell and hangs. When all four agree, the
   filesystem is not the variable — the difference is in the process.
9. **`fltmc filters`** — the right tool when two processes on one machine disagree about
   whether a file exists; it enumerates filesystem filter drivers. It needs elevation, so
   the user runs it (see Boundaries). `Instances 0` means loaded but attached to nothing, and is a
   real exclusion for that instant. A non-zero count proves attachment to N volumes and
   nothing more — not that it touches `C:`, not that it touches your path.

## PowerShell 5.1 specifics that repeatedly mislead

| Symptom | Cause | Fix |
|---|---|---|
| `PSSecurityException` running a `.ps1` shim (`cn.ps1`) | **Only if** `Get-ExecutionPolicy -List` shows CurrentUser at `Restricted`; measured 2026-09-17 it is `RemoteSigned` — re-check before blaming policy, it has moved once already | Call the `.cmd` sibling (`cn.cmd`). If CurrentUser really is `Restricted`, the user's fix is `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| A `$PROFILE` fix "has no effect" | Under `Restricted`, **profiles do not load at all** — check `Get-ExecutionPolicy -List` first | Nothing placed in `$PROFILE` works until the policy is relaxed — propose a different mechanism |
| The error names an **old** path you already fixed | Precedence is Alias > Function > Cmdlet > External; a leftover `function cn { ... }` can shadow the real binary | Run `Get-Command cn -All` first. **Only if** it lists a `Function` entry above the `Application`/`ExternalScript` one, `Remove-Item Function:\cn` — this clears it for the current session only, not future ones |
| `curl.exe` with a `-d` JSON payload fails — `bad range specification`, `unmatched brace`, or another URL-globbing error | PS 5.1 mangles `\"` escapes before curl sees them, and curl's own globbing parser (`{}`/`[]`) trips on what's left — the exact message varies with the payload | `Invoke-RestMethod` with a hashtable + `ConvertTo-Json`, or `curl.exe -d "@file.json"`, or `curl.exe -g` to disable globbing |
| A PATH change is invisible in a new tab | Windows Terminal is **one long-lived process**; new tabs inherit its environment | Quit Windows Terminal completely. Restarting Explorer does not help — and this was *not* the cause in the source session |

## Boundaries

- **Execution policy is the user's to change.** It is a security setting. Print
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` and say what it allows; do not run it.
- **No elevated commands.** `fltmc filters`, `fltmc instances`, `fltmc volumes` need an
  elevated shell that the user opens. Print the exact command, read the output they paste back.
- **Never change PATH, the npm prefix, or a config file silently.** State the file, the old
  value, the new value and how to undo it — e.g. the npm prefix moved to
  `C:\Users\<you>\.local\bin` because that directory is on PATH and provably shared.
- **Nothing on remote or employer systems.** Domain controllers, servers and other employer
  hosts are read-only; diagnose from this machine.
- **Say "unresolved" when it is unresolved.** A named suspect is not a cause; a measured
  mechanism is.
