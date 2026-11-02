#!/usr/bin/env python3
"""Lint app code for style-system violations. Keeps a large app consistent.

Usage (from the project root):
    python .claude/skills/streamlit-neubrutal-ui/scripts/check_style.py [PATH ...]

Checks every .py file outside ui/ (the kit itself may use raw HTML/CSS).
Exit code 1 if anything is found. Silence a single line with `# nb: ignore`.

Rules
  NB001  hex color literal            -> use ui.tokens (C., TAG.)
  NB002  unsafe_allow_html=True       -> use a ui.components function
  NB003  st.html / components.html    -> use a ui.components function
  NB004  st.plotly_chart(...)         -> use ui.charts.show(fig) (it sets theme=None)
  NB005  <style> in a string          -> CSS lives only in ui/theme.py
  NB006  generated Streamlit class    -> never target st-emotion-cache / css-xxxxx classes
  NB007  st.set_page_config(...)      -> use ui.theme.setup_page() once in the entry script
"""

import ast
import re
import sys
from pathlib import Path

SKIP_DIRS = {"ui", ".claude", ".git", ".venv", "venv", "env", "__pycache__", "site-packages", "node_modules",
             ".streamlit", "build", "dist"}
HEX = re.compile(r"(?<![\w&])#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
GENERATED = re.compile(r"st-emotion-cache|\bcss-(?=[a-z0-9]*\d)[a-z0-9]{5,}\b")
STYLE_TAG = re.compile(r"<style\b", re.I)


def iter_files(paths):
    for p in paths:
        p = Path(p)
        if p.is_file() and p.suffix == ".py":
            yield p
        elif p.is_dir():
            for f in sorted(p.rglob("*.py")):
                rel = f.relative_to(p)
                if any(part in SKIP_DIRS for part in rel.parts[:-1]):
                    continue
                yield f


def call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Attribute):
        base = f.value
        prefix = base.id if isinstance(base, ast.Name) else (base.attr if isinstance(base, ast.Attribute) else "")
        return f"{prefix}.{f.attr}"
    if isinstance(f, ast.Name):
        return f.id
    return ""


def check(path: Path):
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as exc:
        return [(exc.lineno or 0, "NB000", f"syntax error: {exc.msg}")]

    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            if HEX.search(s):
                found.append((node.lineno, "NB001", f"hex color {HEX.search(s).group(0)!r}: use ui.tokens"))
            if STYLE_TAG.search(s):
                found.append((node.lineno, "NB005", "<style> outside ui/theme.py"))
            if GENERATED.search(s):
                found.append((node.lineno, "NB006", f"generated Streamlit class {GENERATED.search(s).group(0)!r}"))
        elif isinstance(node, ast.Call):
            name = call_name(node)
            for kw in node.keywords:
                if kw.arg == "unsafe_allow_html" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    found.append((node.lineno, "NB002", "unsafe_allow_html=True: use ui.components"))
            if name in {"st.html", "components.html", "v1.html"}:
                found.append((node.lineno, "NB003", f"{name}(): use ui.components"))
            if name.endswith(".plotly_chart"):
                found.append((node.lineno, "NB004", "st.plotly_chart: use ui.charts.show(fig)"))
            if name == "st.set_page_config":
                found.append((node.lineno, "NB007", "st.set_page_config: use ui.theme.setup_page()"))

    result = []
    for lineno, code, msg in sorted(set(found)):
        line = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
        if "nb: ignore" in line:
            continue
        result.append((lineno, code, msg))
    return result


def main() -> int:
    paths = sys.argv[1:] or ["."]
    total = 0
    for f in iter_files(paths):
        for lineno, code, msg in check(f):
            print(f"{f}:{lineno}: {code} {msg}")
            total += 1
    if total:
        print(f"\n{total} style issue(s). See .claude/skills/streamlit-neubrutal-ui/references/rules.md")
        return 1
    print("style check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
