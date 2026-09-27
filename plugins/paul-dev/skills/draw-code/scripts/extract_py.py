#!/usr/bin/env python3
"""Extract structure facts from a Python file using the standard-library AST.

Everything this prints is read off the syntax tree, never inferred from a name.
Output is JSON on stdout, shaped for scripts/render.py.

    python extract_py.py path/to/file.py
    python extract_py.py path/to/file.py --class FTLCombatSim
    python extract_py.py path/to/file.py --out facts.json

Stdlib only, so it runs anywhere a Python interpreter does.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
import tokenize
from pathlib import Path


def sig(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Render a parameter list the way the source declares it, minus `self`."""
    a = fn.args
    parts: list[str] = []
    pos = a.posonlyargs + a.args
    defaults = list(a.defaults)
    pad = len(pos) - len(defaults)
    for i, arg in enumerate(pos):
        if arg.arg == "self":
            continue
        text = arg.arg
        if i >= pad:
            try:
                text += " = " + ast.unparse(defaults[i - pad])
            except Exception:
                pass
        parts.append(text)
    if a.vararg:
        parts.append("*" + a.vararg.arg)
    for i, arg in enumerate(a.kwonlyargs):
        text = arg.arg
        d = a.kw_defaults[i]
        if d is not None:
            try:
                text += " = " + ast.unparse(d)
            except Exception:
                pass
        parts.append(text)
    if a.kwarg:
        parts.append("**" + a.kwarg.arg)
    return ", ".join(parts)


def returns(fn) -> str:
    if fn.returns is None:
        return ""
    try:
        return ast.unparse(fn.returns)
    except Exception:
        return ""


def first_doc_line(fn) -> str:
    doc = ast.get_docstring(fn)
    if not doc:
        return ""
    return doc.strip().splitlines()[0].strip()


def decorators(fn) -> list[str]:
    out = []
    for d in fn.decorator_list:
        try:
            out.append(ast.unparse(d))
        except Exception:
            pass
    return out


def collect_calls(fn, module_level: set[str]) -> dict:
    """Split calls into self.* (same class) and bare names defined in this module.

    The second bucket is the one a naive `self.`-only scan misses — for example a
    method calling a module-level helper.
    """
    own, module = set(), set()
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "self":
            own.add(f.attr)
        elif isinstance(f, ast.Name) and f.id in module_level:
            module.add(f.id)
    return {"self": sorted(own), "module": sorted(module)}


def fn_record(fn, module_level: set[str]) -> dict:
    return {
        "name": fn.name,
        "lines": f"{fn.lineno}-{fn.end_lineno}",
        "start": fn.lineno,
        "end": fn.end_lineno,
        "takes": sig(fn),
        "returns": returns(fn),
        "doc": first_doc_line(fn),
        "decorators": decorators(fn),
        "calls": collect_calls(fn, module_level),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract Python structure facts via AST.")
    ap.add_argument("file", help="the .py file to read")
    ap.add_argument("--class", dest="cls", default=None, help="only this class")
    ap.add_argument("--out", default=None, help="write JSON here instead of stdout")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"not a file: {path}", file=sys.stderr)
        return 2

    # tokenize.open reads the file the way Python itself does: it strips a UTF-8 BOM
    # (ordinary on Windows) and honours a PEP 263 `# coding:` line. Plain read_text
    # leaves the BOM in place and ast.parse then blames the user's line 1.
    try:
        with tokenize.open(path) as fh:
            src = fh.read()
    except (SyntaxError, UnicodeDecodeError) as exc:
        print(f"cannot decode {path}: {exc}", file=sys.stderr)
        return 1

    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as exc:
        print(f"{path} is not valid Python: line {exc.lineno}: {exc.msg}", file=sys.stderr)
        return 1

    fn_types = (ast.FunctionDef, ast.AsyncFunctionDef)
    module_level = {n.name for n in tree.body if isinstance(n, fn_types)}

    classes, functions, constants = [], [], []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if args.cls and node.name != args.cls:
                continue
            classes.append({
                "name": node.name,
                "lines": f"{node.lineno}-{node.end_lineno}",
                "doc": first_doc_line(node),
                "bases": [ast.unparse(b) for b in node.bases],
                "methods": [fn_record(f, module_level) for f in node.body if isinstance(f, fn_types)],
                "attrs": [
                    t.id
                    for s in node.body if isinstance(s, ast.Assign)
                    for t in s.targets if isinstance(t, ast.Name)
                ],
            })
        elif isinstance(node, fn_types) and not args.cls:
            functions.append(fn_record(node, module_level))
        elif isinstance(node, ast.Assign) and not args.cls:
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.isupper():
                    try:
                        constants.append({"name": t.id, "line": node.lineno,
                                          "value": ast.unparse(node.value)[:120]})
                    except Exception:
                        pass

    if args.cls and not classes:
        names = sorted(n.name for n in tree.body if isinstance(n, ast.ClassDef))
        print(f"no top-level class named {args.cls!r} in {path}. "
              f"Found: {', '.join(names) if names else 'none'}", file=sys.stderr)
        return 1

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    out = {
        "source": str(path),
        "language": "python",
        "provenance": "parsed",
        "lines": len(src.splitlines()),
        "imports": sorted(set(imports)),
        "constants": constants,
        "classes": classes,
        "functions": functions,
    }

    text = json.dumps(out, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
