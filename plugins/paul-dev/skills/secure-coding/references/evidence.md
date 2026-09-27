# Evidence behind the secure-coding rules

Evidence as of 2026-09-20. Source: a research report, whose figures were checked against
primary sources by three independent fact-checkers and a reviewer on the same day.

## The marks

| Mark | Meaning |
|---|---|
| **[M]** | Measured — a study or vendor scan counted how often AI does this |
| **[O]** | Observed — documented reproductions by researchers or practitioners; nobody counted |
| **[S]** | Standard only — the secure pattern is authoritative, but no evidence was found that AI gets this wrong more than humans do |

An **[S]** rule still applies. It is just not evidence of an *AI* problem. Roughly a third of the
catalogue is **[S]**; the six **[O]** entries in the login section rest on blog posts, four of
them on one author's blog (simonroses.com).

## Headline numbers, with their limits

- **45% of AI-generated samples introduced an OWASP Top 10 flaw** — Veracode, 2025 GenAI Code
  Security Report (blog 30 July 2025, October 2025 update), 100+ models. Narrower than usually
  quoted: 80 tasks in Java, Python, C# and JavaScript, scored on four CWEs (SQL injection, XSS,
  log injection, weak crypto). Java failed worst at 72%; XSS not prevented in 86% of relevant
  samples, log injection in 88%. No improvement with model size or recency. The task count, CWE
  list and 88% come from the report PDF via Help Net Security; the rest is on Veracode's blog.
- **BaxBench (ICML 2025, 392 backend tasks):** the best model (o1) was functionally correct only
  62% of the time; no flagship model exceeded 35–37% correct *and* secure (the paper gives both);
  about half of functionally correct programs were exploitable.
- **Checkmarx-commissioned study (run independently by The Weather Report Inc.):** frontier
  models produced working code 83–95% of the time, but only 24–36% of it was secure.
- **Perry, Srivastava, Kumar, Boneh, CCS 2023:** 47 participants (33 with an assistant, 14
  without), five tasks; the assisted group wrote less secure code on four and was more likely to
  believe its code was secure. The most rigorous single result in the field.
- **GitGuardian, State of Secrets Sprawl 2026 (17 March 2026):** Claude Code-assisted commits on
  public GitHub leaked secrets at 3.2%, against a 1.5% baseline across all public commits. The
  baseline is every commit, not a human-only control group.
- **Not established:** no public breach has been confirmed with AI-generated code as the proven
  root cause. The Tea app (2025) is explicitly unconfirmed as AI-written.

## The catalogue

Numbers match the rule numbers in `SKILL.md`.

### Login, sessions and identity

| # | Mark | What the AI writes | Why | Evidence |
|---|---|---|---|---|
| 1 | [O] | `createHash('md5')` or plain SHA-256 on passwords, no salt, or bcrypt at a low cost | Tutorials hash with MD5/SHA "to focus on the login logic"; the model copies the shape | simonroses.com reproduction (May 2026). Standard: OWASP Password Storage Cheat Sheet — Argon2id m=19456 (19 MiB), t=2, p=1 is one of five listed equivalents; bcrypt "a minimum of 10" |
| 2 | [O] | JWT signed with `"secret"`, no `expiresIn`, algorithm not pinned | Demo code hardcodes the secret and skips expiry for clarity | simonroses.com reproduction |
| 3 | [O] | The JWT goes in `localStorage` | The most-upvoted pattern; the model returns the popular answer, not the secure one | kusari.dev (2026) |
| 4 | [S] | Cookies without `HttpOnly`/`Secure`/`SameSite`; no session rotation; client-only logout | Minimal `res.cookie(name, value)` is what tutorials show | OWASP Session Management Cheat Sheet |
| 5 | [O] | No throttling or lockout on login | Rate limiting reads as infrastructure, outside the code sample | simonroses.com |
| 6 | [O] | `userId` or `isAdmin` taken from the request body | Literal satisfaction of the prompt, no trust-boundary reasoning | Endor Labs blog on common vulnerabilities in AI code |
| 7 | [O] | Token verified, then the record fetched by URL id with no ownership check | "Check auth" is satisfied by verifying the token; ownership needs domain reasoning the model does not volunteer | simonroses.com curl reproduction; dev.to (Cursor IDOR) |
| 8 | [S] | Guessable or non-expiring reset tokens; account-existence leaks | — | OWASP Forgot Password Cheat Sheet: CSPRNG, "sufficiently long", single use. 128 bits and 15–60 min are common practice, not OWASP figures |
| 9 | [S] | `==` on secrets and tokens | — | Standard constant-time comparison |

### Secrets

| # | Mark | What the AI writes | Why | Evidence |
|---|---|---|---|---|
| 10 | [M] | Credentials as literals in source, then committed | A demo needs a concrete value; the model supplies a plausible literal instead of a placeholder plus loading instructions | GitGuardian 2026: 3.2% vs 1.5% (see above) |
| 11 | [O] | Secret key with a `NEXT_PUBLIC_`/`VITE_` prefix; Supabase `service_role` key in browser code | Shortest working call path; every key pasted into `.env` treated the same | vibe-eval.com pattern write-up |

### Exposed endpoints and configuration

| # | Mark | What the AI writes | Why | Evidence |
|---|---|---|---|---|
| 12 | [O] | CRUD route with no auth guard | Getting-started examples leave auth out of scope | Practitioner write-ups (dev.to, vibe-eval.com), no disclosed methodology |
| 13 | [S] | Admin check only client-side | The prompt scoped the task to the frontend | Standard |
| 14 | [O] | `req.body` spread into the ORM; full row including `password_hash` returned | Shortest way to satisfy "update the profile"; JS/TS ORMs lack Strong Parameters | vibe-eval.com mass-assignment pattern |
| 15 | [O] | `Access-Control-Allow-Origin: *`, or `Origin` reflected with credentials | The "allow everything" fix dominates the answers the model learned from | dev.to (Cursor wildcard CORS) |
| 16 | [O] | `DEBUG=True`, introspection on, Swagger live | Framework quick-start defaults; "build me an API" does not distinguish dev from prod | vibe-eval.com; Sourcery vulnerability database |
| 17 | [S] | No rate limit, no schema validation | — | Standard |
| 18 | [M] | Supabase tables with RLS never enabled, reachable via the anon key | The generator wires frontend to database as the fastest path to a demo; enabling RLS is a separate step it does not perform | **CVE-2025-48757** (Matt Palmer, disclosed 29 May 2025): 1,645 public Lovable apps scanned, 170 (10.3%) exposed across 303 endpoints — names, phone numbers, API keys, payment data readable without credentials. Supabase docs: the Table Editor enables RLS on new tables; "When you create a table with SQL, enable it yourself" |

### Storage, queries and data

| # | Mark | What the AI writes | Why | Evidence |
|---|---|---|---|---|
| 19 | [M] | `f"SELECT * FROM users WHERE id={user_id}"` | Reads naturally as "insert the variable"; dominant in training data | Veracode 2025 (SQLi one of the four CWEs). Majdinasab et al. 2023 replication of the Copilot audit: "for SQL injection … more than half of Copilot's generated codes were vulnerable" |
| 20 | [S] | `f"... ORDER BY {sort_col}"` | Bind parameters cannot carry identifiers; the model does not flag the exception | Standard |
| 21 | [S] | `.extra(where=[f"..."])` / `.raw()` with interpolation | The model drops out of the ORM when the fluent API cannot express the query | Sourcery vulnerability database (Django `extra()`) |
| 22 | [S] | `db.users.find(req.body)` | Body-to-query mapping is a common convenience pattern | HackTricks NoSQL injection |
| 23 | [O] | `shell=True`, `os.system(f"convert {filename}")` | Extremely common in scraped code; taint crosses several functions before the sink | JFrog, "Analyzing Vulnerabilities Injected by Code-Generative AI" |
| 24 | [M] | Client-supplied filename joined onto a base path | The happy-path join is the natural next line; the traversal check is a separate step | Morkonda, Selim, Assal, arXiv 2605.23091 (May 2026), seven LLMs: 66 path-traversal findings, "in the most common instance of CWE-22 (79%), the vulnerable code did not sanitize external inputs sufficiently" |
| 25 | [O] | `AES.MODE_ECB`, fixed or zero IV, literal key | ECB has the simplest constructor signature | Pre-2024 study of generated crypto code. Standard: OWASP Cryptographic Storage — authenticated modes "should always be used", GCM and CCM "first preference"; ECB "should not be used outside of very specific circumstances" |
| 26 | [S] | `verify=False`, `InsecureSkipVerify` as the fix for a certificate error | — | Standard |
| 27 | [O] | `return {"error": str(e)}`; request bodies logged whole | Shortest working debug pattern | Practitioner write-ups. GDPR Art. 5(1)(c): data "limited to what is necessary" |
| 28 | [S] | `pickle.load()` on untrusted input; `yaml.load()` without SafeLoader | First-listed, simplest-signature functions in the docs | Standard |
| 29 | [S] | No retention or deletion path; soft-deleted rows returned; unencrypted backups; real PII in seed data | — | Standard |

### Dependencies

| # | Mark | What the AI writes | Why | Evidence |
|---|---|---|---|---|
| 30 | [M] | Install commands for packages that do not exist ("slopsquatting") | The model emits a plausible name | Spracklen et al., USENIX Security 2025: 576,000 samples, 16 LLMs, 5.2% hallucination for commercial models, 21.7% for open-source, 205,474 unique invented names; 43% of hallucinated names repeated in all 10 reruns of the same prompt. Churilov, arXiv 2605.17062 (2026 preprint, not peer-reviewed): 4.62–6.10% on frontier models; 127 names hallucinated identically by all five models tested, 53 still registrable. Lanyado (Lasso, March 2024) registered the empty `huggingface-cli`: 30,000+ downloads in three months; an Alibaba research repository's README carried the install line. Proof of concept, not a malware campaign |
| 31 | [O] | Versions with known CVEs | Training cutoff: a version the model saw as normal has since been patched | Endor Labs 2025: 49% of dependency versions imported by AI coding agents had known vulnerabilities — vendor figure, sample size undisclosed |
| 32 | [O] | `curl \| bash`, root in the Dockerfile, `:latest`, no lockfile | The dominant public pattern optimises for "it works" | Practitioner discussion; standard supply-chain practice |

## What fixes it, ranked by evidence

The two best studies on security prompting disagree, and both were read directly:

| Study | Finding |
|---|---|
| *Benchmarking Prompt Engineering Techniques for Secure Code Generation with GPT Models*, FORGE 2025, arXiv 2502.06039 | A security-focused prompt prefix reduced vulnerabilities "by up to 56%" on GPT-4o/4o-mini |
| *An Empirical Evaluation of LLM-Generated Code Security Across Prompting Methods*, arXiv 2605.24298 (May 2026), five models, four languages | No statistically significant reduction in vulnerability count or density; prompting changed *which* CWEs appeared. Verbatim: "prompt engineering alone is insufficient to reliably reduce overall vulnerability levels." |

Reading: a security instruction reliably changes what kind of flaw appears; it does not reliably
reduce how many. Worth writing, never the control relied on.

1. **A second pass over generated code.** FORGE 2025: iterative self-review detected and repaired
   "between 41.9% and 68.7% of vulnerabilities in previously generated code". The model is far
   better at finding its own flaw when asked to look than at not writing it.
2. **Static analysis in the loop.** GitHub (blog, Aug 2024): Copilot Autofix remediates "more than
   two-thirds of supported alerts with little or no editing", median 28 minutes vs 1.5 hours
   manual — vendor-measured on its own product.
3. **Secret scanning before commit.** Given the GitGuardian figures, the cheapest high-value control.
4. **Specific, checkable rules instead of "be secure".** Backslash Security (April 2025, seven
   LLMs, ten CWEs): under naive prompts every model was vulnerable to at least 4 of 10; a generic
   "make it secure" prompt lifted Claude 3.7 Sonnet from 6/10 to 10/10 but left GPT-4o vulnerable
   to 8 of 10; prompts bound to rules for the specific CWEs produced secure code on every model.
5. **Human review of security-relevant AI code** — widely recommended, not measured, and working
   against Perry et al.: reviewers trust fluent code.

What backfires: extended thinking (A.S.E benchmark, arXiv 2508.18106, Aug 2025 — Claude Sonnet 4
Thinking scored lower on code security than its non-thinking counterpart, "possibly by generating
more complex code"); model choice (no study found security improving with scale or recency);
confidence (Perry et al.).

Claude Code's own features, verified in the docs 2026-09-20: `/security-review` checks the
current diff for vulnerabilities on demand; the `security-guidance` plugin has Claude review and
fix its own changes during the session, at edit, end of turn and commit. Neither has a published
independent detection rate; both implement mitigation 1.

## Primary sources

- Veracode, 2025 GenAI Code Security Report: https://www.veracode.com/blog/genai-code-security-report/
- BaxBench, Vero et al., ICML 2025: https://arxiv.org/abs/2502.11844
- Checkmarx / The Weather Report, *Capability Without Security*: https://checkmarx.com/capability-without-security-measuring-functionality-security-gap-ai-generated-code/
- Perry et al., CCS 2023: https://arxiv.org/abs/2211.03622
- GitGuardian, State of Secrets Sprawl 2026: https://blog.gitguardian.com/the-state-of-secrets-sprawl-2026/
- CVE-2025-48757, researcher statement: https://mattpalmer.io/posts/statement-on-CVE-2025-48757/
- Supabase, Tables and RLS docs: https://supabase.com/docs/guides/database/tables ; https://supabase.com/docs/guides/database/postgres/row-level-security
- Majdinasab et al., Copilot replication, 2023: https://arxiv.org/abs/2311.11177
- Morkonda, Selim, Assal, 2026: https://arxiv.org/abs/2605.23091
- Backslash Security, April 2025 release: https://www.globenewswire.com/news-release/2025/04/24/3067494/0/en/backslash-security-reveals-in-new-research-that-gpt-4-1-other-popular-llms-generate-insecure-code-unless-explicitly-prompted.html
- Spracklen et al., USENIX Security 2025: https://www.usenix.org/system/files/usenixsecurity25-spracklen.pdf
- Churilov, 2026 preprint: https://arxiv.org/abs/2605.17062
- Lanyado, Lasso Security, March 2024: https://www.lasso.security/blog/ai-package-hallucinations
- Endor Labs, *When AI Imports Vulnerable Dependencies*: https://www.endorlabs.com/learn/when-ai-imports-vulnerable-dependencies-securing-ai-generated-code
- FORGE 2025 prompting study: https://arxiv.org/abs/2502.06039
- Prompting methods study, May 2026: https://arxiv.org/abs/2605.24298
- GitHub, Copilot Autofix: https://github.blog/news-insights/product-news/secure-code-more-than-three-times-faster-with-copilot-autofix/
- A.S.E benchmark: https://arxiv.org/abs/2508.18106
- Claude Code docs: https://code.claude.com/docs/en/security-guidance ; https://code.claude.com/docs/en/commands
- OWASP Cheat Sheet Series (Password Storage, Cryptographic Storage, Forgot Password, Session Management): https://cheatsheetseries.owasp.org/
