"""Import-audit: every name referenced from a top-level statement in
core/alive_kernel.py must be defined in the import block. This catches
forgotten `import re` style regressions that would only surface at
runtime, deep in the audio stack, with a useless traceback.

Run: python tests/test_imports_audit.py
"""
import ast
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TARGET = os.path.join(ROOT, "core", "alive_kernel.py")


def _collect_names(expr: ast.AST) -> set[str]:
    """Return every Name in Load context inside the expression tree."""
    out: set[str] = set()
    for sub in ast.walk(expr):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
            out.add(sub.id)
    return out


def test_no_undefined_top_level_names() -> bool:
    with open(TARGET, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)

    # Collect names bound at module level: imports and assignments.
    bound: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                bound.add(alias.asname or alias.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    bound.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            bound.add(node.target.id)
        elif isinstance(node, ast.Try):
            for handler in node.handlers:
                if handler.name:
                    bound.add(handler.name)
    bound.update({"__file__", "__name__", "__doc__"})

    # Now look at every top-level statement that *executes* at import time
    # and collect the names it references. We only care about the RHS of
    # top-level Assign and the body of top-level Expr / If / Try.
    builtin_names = set(dir(__builtins__))
    referenced: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            referenced.update(_collect_names(node.value))
        elif isinstance(node, ast.Expr):
            referenced.update(_collect_names(node.value))
        elif isinstance(node, (ast.If, ast.Try)):
            # Walk the test/handlers/body but skip nested function defs.
            for sub in ast.walk(node):
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue
                if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
                    referenced.add(sub.id)
        # Other top-level statements (Import, FunctionDef, ClassDef, AnnAssign)
        # don't reference unbound names — they bind them.

    undefined = referenced - bound - builtin_names
    if undefined:
        print(f"test_no_undefined_top_level_names: [FAIL] {sorted(undefined)}")
        for n in sorted(undefined):
            print(f"  unbound name at module level: {n!r}")
        return False
    print(f"test_no_undefined_top_level_names: [PASS] {len(referenced)} top-level refs, all bound")
    return True


def test_imports_compile() -> bool:
    sys.path.insert(0, ROOT)
    try:
        import core.alive_kernel  # noqa: F401
        print("test_imports_compile: [PASS] alive_kernel imports without error")
        return True
    except Exception as e:
        print(f"test_imports_compile: [FAIL] {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    a = test_no_undefined_top_level_names()
    b = test_imports_compile()
    if a and b:
        print("imports: 2 passed / 0 failed")
        sys.exit(0)
    else:
        print("imports: FAILED")
        sys.exit(1)
