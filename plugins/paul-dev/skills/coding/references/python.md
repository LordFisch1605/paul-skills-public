# Python 3.12 and later

PEP 8 and PEP 257 are the authority on style and docstrings; Ruff enforces both. The project's
`pyproject.toml` and existing code win over either where they disagree.

## Toolchain, September 2026

- Python 3.14.7 is current (2026-08-05); 3.13 is bugfix maintenance, 3.12 security-only. Write
  3.12+ syntax unless the project pins lower.
- Ruff is linter and formatter in one, at parity with Black: `ruff format .` then
  `ruff check --fix .`; configure under `[tool.ruff]`.
- uv manages the project, venv, dependencies and Python version: `uv init`, `uv add <pkg>`,
  `uv run <cmd>`, `uv sync`; lockfile `uv.lock`.
- `pyproject.toml` with a `[project]` table is the single metadata file (PEP 621);
  `python setup.py` is deprecated; `requirements.txt` is at most an export.
- pytest is the test runner.

## Conventions

- `snake_case` functions, variables, modules; `PascalCase` classes; `UPPER_CASE` constants; a
  leading `_` marks an internal name.
- Line length: Ruff's default 88 unless `pyproject.toml` sets `line-length`; never change an
  existing setting. PEP 8's 79 (or 99 by agreement) is what that setting overrides.
- Imports at the top, one per line, grouped stdlib / third-party / local with a blank line
  between groups; never `from x import *`.
- Docstrings in triple double quotes, one-line imperative summary, on public functions and
  classes only.
- Typing on public signatures: `X | None` (PEP 604), builtin generics `list[str]`,
  `dict[str, int]` (PEP 585), `type` statement and `def f[T](x: T)` (PEP 695, 3.12);
  `typing.Optional`/`typing.List` are legacy spellings.
- Newer typing where the Python allows it: TypeVar defaults (PEP 696, 3.13), deferred
  annotation evaluation (PEP 649, 3.14), template strings `t"..."` (PEP 750, 3.14).
- `pathlib.Path` for paths, `Path.read_text()`, `/` joins — not `os.path` string juggling.
- `logging` with lazy arguments, `log.info("loaded %s", path)`; `print` only for CLI output.
- `@dataclass` (`frozen=True` where it should not change) instead of a hand-written `__init__`.
- `with` for files, locks and connections; every resource released by a context manager.
- f-strings for formatting; `%`/`.format` only where a library requires them.
- `if __name__ == "__main__": main()` guarding the entry point, logic in `main()`.
- `is None` / `is not None`; `isinstance(x, T)`, never `type(x) == T`.

## Testing

- pytest discovers `test_*.py`/`*_test.py` files and `test_` functions; keep them in `tests/`
  beside the package.
- Plain `assert x == y`; pytest rewrites it to show both sides on failure, not
  `unittest`-style `self.assertEqual`.
- Fixtures over `setUp`; `@pytest.mark.parametrize` for tables of cases; `pytest.raises` for
  exceptions.
- `uv run pytest` (or `pytest`) for the whole suite before reporting.

## What AI code gets wrong here

| Does | Instead |
|---|---|
| Bare `except:` or `except Exception: pass` | Catch the specific exception, or propagate; a bare except also swallows `KeyboardInterrupt`. |
| Mutable default `def f(items=[])` | `items: list[str] \| None = None`, create inside. |
| `from module import *` | Explicit names. |
| `== None` | `is None`. |
| `type(x) == T` | `isinstance(x, T)`. |
| `subprocess.run(cmd_string, shell=True)` with a built string | An argument list, `shell=False`. |
| A package that does not exist on PyPI | Check `pypi.org/project/<name>` first; hallucinated names recur, get squatted. |
| `typing.Optional[str]`, `typing.List[int]` on 3.10+ | `str \| None`, `list[int]`. |
| `os.path.join(str(a), "b")` | `a / "b"` on a `Path`. |
| `print(...)` left as debugging output | `logging`, or removed. |
| f-string inside a logging call | `%s` arguments so the string builds only when the level is enabled. |
| Shadowing builtins (`list`, `id`, `type`, `input`) as variable names | A descriptive name. |
| Unpinned `requirements.txt` as the dependency record | `pyproject.toml` plus `uv.lock`. |

## Sources

- PEP 8: https://peps.python.org/pep-0008/
- PEP 257: https://peps.python.org/pep-0257/
- PEP 604: https://peps.python.org/pep-0604/
- PEP 585: https://peps.python.org/pep-0585/
- PEP 695: https://peps.python.org/pep-0695/
- Python downloads: https://www.python.org/downloads/
- Ruff: https://docs.astral.sh/ruff/
- uv: https://docs.astral.sh/uv/
- Writing pyproject.toml: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- pytest good practices: https://docs.pytest.org/en/stable/explanation/goodpractices.html
- Logging HOWTO: https://docs.python.org/3/howto/logging.html
- subprocess security: https://docs.python.org/3/library/subprocess.html#security-considerations
