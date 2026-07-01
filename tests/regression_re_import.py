"""Regression test: simulate the original 'import re' bug by stripping the
import from a copy of core/alive_kernel.py, then run the same AST check
the audit does. This proves the audit would have caught the bug.

This file is a one-shot regression check, not part of the normal CI suite.
"""
import ast
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "core", "alive_kernel.py")
TMP = os.path.join(ROOT, "tests", "_tmp_kernel_no_re.py")

# Make a buggy copy.
with open(SRC, "r", encoding="utf-8") as f:
    src = f.read()
buggy = "\n".join(line for line in src.split("\n") if line.strip() != "import re")
with open(TMP, "w", encoding="utf-8") as f:
    f.write(buggy)

try:
    tree = ast.parse(buggy)
    bound = set()
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
    bound.update({"__file__", "__name__", "__doc__"})

    # Find any `re.X(...)` call inside any function body.
    found = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) \
                        and isinstance(sub.func.value, ast.Name) \
                        and sub.func.value.id == "re":
                    found.append((node.name, sub.lineno))
                    break

    if found and "re" not in bound:
        print(f"REGRESSION TEST PASSES: audit would have caught {found[0]}")
        print(f"  're' is used inside {found[0][0]}() at line {found[0][1]}")
        print(f"  but 're' is not in the import block")
    else:
        print("REGRESSION TEST FAILED: did not detect the re bug")
finally:
    if os.path.exists(TMP):
        os.remove(TMP)
