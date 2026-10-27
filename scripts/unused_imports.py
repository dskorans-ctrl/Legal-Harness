"""Count imported names that a module never uses: `unused_imports=N` (exit 1 when N > 0).

Usage: python scripts/unused_imports.py PATH... (files or folders; folders are walked for *.py).
A name counts as used when it appears as a Name or as the base of an Attribute chain, or is listed in
__all__. Star imports and __future__ imports are skipped. Names used only in comments or docstrings
do not count.
"""

import ast
import sys
from pathlib import Path


def imported(tree):
    """(bound name, line) for every import in the module, nested ones included."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield (alias.asname or alias.name.split(".")[0]), node.lineno
        elif isinstance(node, ast.ImportFrom) and node.module != "__future__":
            for alias in node.names:
                if alias.name != "*":
                    yield (alias.asname or alias.name), node.lineno


def used(tree):
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__"
                                                for t in node.targets):
            if isinstance(node.value, (ast.List, ast.Tuple)):
                names |= {e.value for e in node.value.elts
                          if isinstance(e, ast.Constant) and isinstance(e.value, str)}
    return names


def check(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    seen = used(tree)
    return [(path, line, name) for name, line in imported(tree) if name not in seen]


def files(roots):
    for root in roots:
        root = Path(root)
        if root.is_dir():
            yield from sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)
        else:
            yield root


def main(argv) -> int:
    if not argv:
        print("usage: unused_imports.py PATH...", file=sys.stderr)
        return 2
    found = [hit for path in files(argv) for hit in check(path)]
    for path, line, name in found:
        print(f"{path}:{line}: unused import {name}")
    print(f"unused_imports={len(found)}")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
