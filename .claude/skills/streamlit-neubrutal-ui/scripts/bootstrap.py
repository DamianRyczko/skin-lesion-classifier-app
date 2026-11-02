#!/usr/bin/env python3
"""Install the UI kit into a Streamlit project.

Usage (from the project root):
    python .claude/skills/streamlit-neubrutal-ui/scripts/bootstrap.py [--project PATH] [--force] [--no-demo]

Creates (never overwrites existing files unless --force):
    ui/__init__.py, ui/tokens.py, ui/theme.py, ui/components.py, ui/charts.py
    ui_demo.py                     living style guide (streamlit run ui_demo.py)
    .streamlit/config.toml         [theme] block generated from ui/tokens.py
    requirements.txt               adds streamlit / plotly if missing
"""

import argparse
import shutil
import sys
from importlib import metadata
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import sync_theme  # noqa: E402

UI_FILES = ["__init__.py", "tokens.py", "theme.py", "components.py", "charts.py"]
REQUIREMENTS = {"streamlit": "1.66.0", "plotly": "7.1.0"}  # versions the kit was tested with


def copy(src: Path, dst: Path, force: bool) -> str:
    if dst.exists() and not force:
        return f"kept     {dst}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return f"created  {dst}"


def ensure_requirements(project: Path) -> str:
    req = project / "requirements.txt"
    lines = req.read_text(encoding="utf-8").splitlines() if req.exists() else []
    names = {l.split("==")[0].split(">=")[0].split("[")[0].strip().lower() for l in lines if l.strip()
             and not l.startswith("#")}
    added = []
    for pkg, tested in REQUIREMENTS.items():
        if pkg in names:
            continue
        try:
            version = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            version = tested
        lines.append(f"{pkg}=={version}")
        added.append(f"{pkg}=={version}")
    if added:
        req.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return f"updated  {req} (+ {', '.join(added)})"
    return f"kept     {req}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=".", help="project root (default: current directory)")
    ap.add_argument("--force", action="store_true", help="overwrite existing ui/ files and ui_demo.py")
    ap.add_argument("--no-demo", action="store_true", help="do not create ui_demo.py")
    args = ap.parse_args()
    project = Path(args.project).resolve()

    report = [copy(TEMPLATES / "ui" / f, project / "ui" / f, args.force) for f in UI_FILES]
    if not args.no_demo:
        report.append(copy(TEMPLATES / "ui_demo.py", project / "ui_demo.py", args.force))
    report.append(f"updated  {sync_theme.sync(project)}")
    report.append(ensure_requirements(project))
    print("\n".join(report))
    print("\nNext: pip install -r requirements.txt && streamlit run ui_demo.py")


if __name__ == "__main__":
    main()
