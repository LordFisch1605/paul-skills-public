---
name: secure-coding
description: The security layer beneath `coding` for any application code Claude writes or reviews — login and sessions, secrets, exposed endpoints and platform defaults, storage and queries, dependencies — as checkable never/instead rules with the evidence behind each, and the second pass over generated code that is the best-evidenced control. Use when implementing or reviewing anything that authenticates, authorises, stores secrets or personal data, exposes an HTTP endpoint, builds a query or shell command from input, handles uploads or file paths, encrypts, or adds a dependency; when asked to "add login", "add auth", "protect this endpoint", "make it secure", "review for security", "ist das sicher", "Sicherheit prüfen", "härten"; and when generated code takes a user id or role from the request body, stores a JWT in localStorage, ships a secret with a NEXT_PUBLIC_ or VITE_ prefix, leaves Supabase RLS off, or installs a package that does not exist on its registry. Evidence per rule lives in references/evidence.md.
---

# Secure coding

The security layer beneath `paul-dev:coding` for anything that authenticates, stores, exposes
or installs. `base-conduct` wins on conduct, the project's `CLAUDE.md` wins on stack, and the
OWASP Cheat Sheet Series wins on the secure pattern itself. Every rule here is checkable. The
evidence behind each — measured, observed, or standard only — is in `references/evidence.md`.

## The most important rule

**AI security failures are omissions, and omissions look finished.** The one confirmed
real-world incident (CVE-2025-48757: 170 of 1,645 Lovable apps with readable databases) was not
a bug that was written but a protection — Row-Level Security — that was never turned on, and
nothing in the workflow noticed the absence. In the one controlled human study (Perry et al.,
CCS 2023, 47 participants) people with an AI assistant wrote less secure code on four of five
tasks and were *more* confident it was secure. Fluent, well-commented security code earns more
scrutiny, not less.

Two consequences:

1. **A security instruction in the prompt is not the control.** The two best studies disagree on
   whether it reduces flaws at all; both agree it changes *which* flaws appear. Write specific
   rules (the tables below), never "make it secure" — and never rely on them alone.
2. **The second pass is the control.** Asked to review code it just wrote, a model finds and
   fixes 41.9–68.7% of the vulnerabilities it put there — the strongest prompt-side result in the
   literature. Nothing security-relevant is reported done before the pass in "Before done" ran.

## Login, sessions and identity

| # | Never | Instead |
|---|---|---|
| 1 | MD5, SHA-*, or a low-cost bcrypt on passwords | Argon2id (m≥19 MiB, t=2, p=1) or bcrypt cost ≥10, 12 preferred; verify with the library's own function |
| 2 | JWT signed with a literal like `"secret"`, no expiry, algorithm taken from the token | Secret ≥32 bytes from env; always set an expiry; the server pins the algorithm |
| 3 | Session token in `localStorage` | `HttpOnly; Secure; SameSite` cookie — anything in `localStorage` is readable by any XSS |
| 4 | Bare `res.cookie(name, value)`; same session id after login; logout that only clears the client | All three flags set explicitly; new session id on login and privilege change; server-side invalidation on logout |
| 5 | Login endpoint without throttling | Per-account **and** per-IP backoff on every authentication endpoint |
| 6 | `userId`, `isAdmin`, `role` read from the request body or query | Identity and role come only from the verified server-side session |
| 7 | Token checked, then `findById(req.params.id)` | Every query scoped by the principal: `where: { id, ownerId: req.user.id }` — the most common authorization gap |
| 8 | Guessable or non-expiring reset tokens; "no account with that email" | Single-use CSPRNG token that expires; identical response whether or not the account exists |
| 9 | `==` on a token or secret | `crypto.timingSafeEqual`, `hmac.compare_digest`, or the hashing library's verify |

## Secrets

| # | Never | Instead |
|---|---|---|
| 10 | A key or credential as a literal in source — even "temporarily" | Env or a secrets manager; `gitleaks` (or equivalent) on the diff before finishing. Claude Code-assisted commits leak secrets at about twice the all-commit baseline |
| 11 | A secret key with a `NEXT_PUBLIC_`/`VITE_` prefix; a Supabase `service_role` key in browser code | Only the anon/publishable key reaches the browser; secret keys never carry a public prefix |

## Exposed endpoints and configuration

| # | Never | Instead |
|---|---|---|
| 12 | A CRUD route with no auth guard | Deny by default: the guard on the router, not per handler |
| 13 | Admin check only in the UI (`if (user.role === 'admin')`) | Every privileged route enforces the role server-side; hiding a button is not authorization |
| 14 | `data: req.body` into the ORM; whole row (with `password_hash`) in the response | Allow-list writable fields; `select` only public fields on the way out |
| 15 | `Access-Control-Allow-Origin: *`, or the `Origin` header reflected with credentials | Server-side allow-list of origins; validate, then echo that one |
| 16 | `DEBUG=True`, GraphQL introspection, Swagger with a live token — outside development | Environment-based config; docs and introspection off or authenticated in production |
| 17 | Public endpoint without rate limit or schema validation | Rate-limiting middleware; Zod/Pydantic (or the stack's equivalent) at the boundary |
| 18 | A Supabase table reachable with the anon key and RLS off | Enable RLS on every table **before** any query from a public-key context. Tables created with SQL start with it off; the anon key is not an access control |

## Storage, queries and data

| # | Never | Instead |
|---|---|---|
| 19 | `f"SELECT ... WHERE id={user_id}"`, string-built JPQL, concatenated SQL | Bind parameters, always |
| 20 | `f"... ORDER BY {sort_col}"` | Identifiers cannot be bound: allow-list column and table names against a fixed set |
| 21 | `.raw()`/`.extra()` with interpolation when the ORM cannot express the query | The parameterised raw form (`.raw(sql, params)`); treat `extra()` as forbidden |
| 22 | `db.users.find(req.body)` | Strip `$`-prefixed keys; map permitted fields explicitly — otherwise `{"password": {"$ne": null}}` logs in |
| 23 | `shell=True`, `os.system(f"convert {filename}")` | Argument list, `shell=False`, never a shell string built from input |
| 24 | `os.path.join(UPLOAD_DIR, filename)` with a client-supplied name | Resolve and verify the path stays inside the base; store under a generated name outside the web root |
| 25 | `AES.MODE_ECB`, a fixed or zero IV, a literal key | AES-GCM with a unique nonce per encryption; key from a secrets manager |
| 26 | `verify=False`, `InsecureSkipVerify` to make a TLS error go away | Fix the trust store or supply the CA bundle |
| 27 | `return {"error": str(e)}`; whole request bodies in logs | Generic error to the client, detail server-side with secrets and PII redacted (GDPR Art. 5(1)(c)) |
| 28 | `pickle.load()` on untrusted input; `yaml.load()` without SafeLoader | `yaml.safe_load()`; no `pickle` on anything from outside |
| 29 | No deletion path; soft-deleted rows returned; unencrypted backups; real PII in seed data | Default filter `deleted_at IS NULL`; encrypted backups with separate keys; synthetic fixtures only |

## Dependencies

| # | Never | Instead |
|---|---|---|
| 30 | Install a package because the model named it — about 5% of commercial-model package names do not exist, models invent the same names repeatedly, and attackers register them | Confirm it exists on its registry with plausible download history **before** `npm install`/`pip install`. Typosquatting checks do not catch this: a hallucinated name is not a misspelling |
| 31 | A version remembered from training data | Check the current version and its advisories; pin it |
| 32 | `curl \| bash`, root in the Dockerfile, `:latest` base images, no lockfile | Checksummed downloads, a non-root user, pinned digests, a committed lockfile |

## Before done: the second pass

Run this on every diff that touches a rule area above, after the code works and before the
report:

1. **Name the trust boundaries** the diff touches: request input, file names, query building,
   shell calls, tokens, keys, third-party origins. For each, name the rule number that applies.
2. **Walk the tables** for those areas against the diff, not against memory. Look especially for
   what is *absent*: the guard not attached, the ownership clause not added, RLS not enabled,
   the flag not set.
3. **Run the tools that exist**: the project's static analysis (Semgrep, CodeQL) on the diff;
   `gitleaks` or a grep for `key`, `token`, `password`, `secret` in the diff; in Claude Code,
   `/security-review`, or the `security-guidance` plugin if installed.
4. **Report** which rules were checked, what was found and fixed, and what was not checked. A
   pass that found nothing says so; a pass that did not run is not reported as done (`coding`,
   most important rule).

## What does not work

- **"Write secure code" in the prompt.** Changes which CWEs appear, not how many.
- **Extended thinking as a security control.** On the A.S.E benchmark the thinking variant
  scored lower on security than its non-thinking sibling.
- **Choosing a bigger or newer model.** No study found security improving with scale or recency.
- **Trusting fluent code.** Confidence and security were anti-correlated in the one controlled
  human study (Perry et al.).

## Boundaries

- Never weaken a control to make something pass: no `verify=False`, no disabled RLS, no
  broadened CORS, no skipped auth guard "for now". If a control blocks the task, say so and ask.
- Never write a real secret into a file, a log, a test fixture or a commit.
- A new authentication, session or crypto scheme, a change to RLS policies or CORS origins, or a
  new security-relevant dependency is the user's decision (`base-conduct` rule 1): present the
  options, then implement the one chosen.
- Where this skill and the OWASP Cheat Sheet Series disagree on a pattern, OWASP wins; where a
  project's `CLAUDE.md` disagrees on stack choice, the project wins there.
