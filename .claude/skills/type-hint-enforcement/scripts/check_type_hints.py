#!/usr/bin/env python3
"""AST-based checker for the type hinting rules in .claude/CLAUDE.md.

Checks, per Django app under the given root:
  1. Every function/method parameter (except self/cls) and every return
     value is annotated, in every layer (models, repositories, services,
     serializers, views).
  2. `services/` and `views/` files do not import Django models at module
     level outside an `if TYPE_CHECKING:` block.
  3. Any file with a TYPE_CHECKING-guarded model import also has
     `from __future__ import annotations`.

This script is a static approximation, not a type checker: it flags missing
annotations and layer-import violations, but does not judge whether an
existing annotation is semantically correct, and does not see imports made
inside function bodies. Treat its output as a checklist, not ground truth.

Usage:
    python3 check_type_hints.py [root] [--json]

`root` defaults to "backend" if that directory exists, otherwise ".".
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

LAYER_DIRS = {"models", "repositories", "services", "serializers", "views"}
NO_RUNTIME_MODEL_LAYERS = {"services", "views"}
SKIP_APP_DIRS = {".venv", "venv", "node_modules", "__pycache__", ".git", "staticfiles", "media"}
SKIP_PATH_PARTS = {"migrations", "__pycache__"}


class Violation:
    def __init__(self, path: str, line: int, message: str) -> None:
        self.path = path
        self.line = line
        self.message = message

    def as_dict(self) -> dict[str, object]:
        return {"path": self.path, "line": self.line, "message": self.message}

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def iter_target_files(root: Path):
    for app_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        if app_dir.name in SKIP_APP_DIRS or app_dir.name.startswith("."):
            continue
        for layer in LAYER_DIRS:
            layer_dir = app_dir / layer
            if not layer_dir.is_dir():
                continue
            for f in sorted(layer_dir.rglob("*.py")):
                if any(part in SKIP_PATH_PARTS for part in f.parts):
                    continue
                if f.name == "__init__.py" and f.stat().st_size == 0:
                    continue
                yield layer, f


def check_function(func, path: str, violations: list[Violation]) -> None:
    args = func.args
    positional = args.posonlyargs + args.args
    for i, a in enumerate(positional):
        if i == 0 and a.arg in ("self", "cls"):
            continue
        if a.annotation is None:
            violations.append(
                Violation(path, a.lineno, f"parameter '{a.arg}' in '{func.name}' is missing a type hint")
            )
    for a in args.kwonlyargs:
        if a.annotation is None:
            violations.append(
                Violation(path, a.lineno, f"keyword-only parameter '{a.arg}' in '{func.name}' is missing a type hint")
            )
    if args.vararg is not None and args.vararg.annotation is None:
        violations.append(
            Violation(path, func.lineno, f"*{args.vararg.arg} in '{func.name}' is missing a type hint")
        )
    if args.kwarg is not None and args.kwarg.annotation is None:
        violations.append(
            Violation(path, func.lineno, f"**{args.kwarg.arg} in '{func.name}' is missing a type hint")
        )
    if func.returns is None:
        violations.append(Violation(path, func.lineno, f"'{func.name}' is missing a return type hint"))


def _is_type_checking_guard(test: ast.expr) -> bool:
    if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
        return True
    if isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING":
        return True
    return False


def _is_model_module(module: str | None) -> bool:
    if not module:
        return False
    return module == "models" or module.endswith(".models") or ".models." in module


def check_runtime_model_imports(tree: ast.Module, path: str, violations: list[Violation]) -> None:
    has_future_annotations = False
    has_type_checking_model_import = False
    runtime_model_import_lines: list[int] = []

    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == "__future__" and any(a.name == "annotations" for a in node.names):
                has_future_annotations = True
            elif _is_model_module(node.module):
                runtime_model_import_lines.append(node.lineno)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if ".models" in alias.name or alias.name.endswith(".models") or alias.name == "models":
                    runtime_model_import_lines.append(node.lineno)
        elif isinstance(node, ast.If) and _is_type_checking_guard(node.test):
            for sub in node.body:
                if isinstance(sub, (ast.Import, ast.ImportFrom)):
                    has_type_checking_model_import = True

    for line in runtime_model_import_lines:
        violations.append(
            Violation(
                path,
                line,
                "imports Django models at module level; services/views must import them only under "
                "`if TYPE_CHECKING:` (see .claude/CLAUDE.md > Type hints)",
            )
        )

    if has_type_checking_model_import and not has_future_annotations:
        violations.append(
            Violation(
                path,
                1,
                "has a TYPE_CHECKING-guarded model import but is missing "
                "`from __future__ import annotations`",
            )
        )


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv[1:]
    root = Path(args[0]) if args else (Path("backend") if Path("backend").is_dir() else Path("."))

    if not root.is_dir():
        print(f"error: root directory '{root}' does not exist", file=sys.stderr)
        return 2

    violations: list[Violation] = []
    for layer, f in iter_target_files(root):
        src = f.read_text()
        try:
            tree = ast.parse(src, filename=str(f))
        except SyntaxError as e:
            violations.append(Violation(str(f), e.lineno or 1, f"syntax error: {e.msg}"))
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                check_function(node, str(f), violations)

        if layer in NO_RUNTIME_MODEL_LAYERS:
            check_runtime_model_imports(tree, str(f), violations)

    violations.sort(key=lambda v: (v.path, v.line))

    if as_json:
        print(json.dumps([v.as_dict() for v in violations], indent=2))
    else:
        for v in violations:
            print(v)
        if violations:
            print(f"\n{len(violations)} violation(s) found.")
        else:
            print("No type hint violations found.")

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
