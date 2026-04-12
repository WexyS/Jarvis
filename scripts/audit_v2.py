"""Deep code audit for Jarvis v2 project."""
import ast, sys
from pathlib import Path

root = Path("jarvis/v2")
files = sorted(root.rglob("*.py"))

issues = []

for f in files:
    src = f.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src, str(f))
    except SyntaxError as e:
        issues.append(f"SYNTAX ERROR: {f}: {e}")
        continue

    # Check 1: Unused imports
    imports = []
    uses = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.asname or alias.name, alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append((alias.asname or alias.name, f"{node.module}.{alias.name}", node.lineno))
        elif isinstance(node, ast.Name):
            uses.add(node.id)
        elif isinstance(node, ast.Attribute):
            # Get root name of attribute access
            n = node
            while isinstance(n, ast.Attribute):
                n = n.value
            if isinstance(n, ast.Name):
                uses.add(n.id)

    for name, full, lineno in imports:
        if name not in uses and name != "_":
            issues.append(f"UNUSED IMPORT: {f}:{lineno} - {full} as {name}")

    # Check 2: Functions defined but never called
    # (Skip dunder methods and test functions)

    # Check 3: Bare except clauses
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                issues.append(f"BARE EXCEPT: {f}:{node.lineno} - except: without specific exception")

    # Check 4: Mutable default args
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in node.args.defaults + node.args.kw_defaults:
                if arg and isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                    issues.append(f"MUTABLE DEFAULT: {f}:{node.lineno} - {node.name}() has mutable default arg")

    # Check 5: Print statements in production code (should use logging)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                issues.append(f"PRINT STATEMENT: {f}:{node.lineno} - should use logging instead")

print(f"Scanned {len(files)} files, found {len(issues)} issues:\n")
for i in issues:
    print(i)
