"""Planning pane helpers — list and manage files under repo/planning/."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Tuple


def planning_dir(repo_path: str) -> Path:
    """Return the planning directory for a repo (created on demand).

    Performs a case-insensitive search so that repos with a capitalised
    'Planning/' directory (created on macOS, which is case-insensitive)
    are found correctly on Linux (case-sensitive) inside Docker.

    When multiple case-variants exist (e.g. both 'Planning/' and a
    spurious lowercase 'planning/' that Beckit auto-created), the
    non-lowercase variant is preferred because the app always creates
    'planning' (lowercase) — any other casing is user-created.
    """
    base = Path(repo_path)
    candidates = []
    try:
        for d in base.iterdir():
            if d.is_dir() and d.name.lower() == "planning":
                candidates.append(d)
    except (PermissionError, OSError):
        pass
    if not candidates:
        return base / "planning"  # does not exist yet — will be created
    # Prefer a non-lowercase variant (user-created); app only creates 'planning'
    for d in candidates:
        if d.name != "planning":
            return d
    return candidates[0]


def ensure_planning_structure(repo_path: str) -> Path:
    """Create planning/ with a starter README if it does not already exist."""
    pdir = planning_dir(repo_path)
    pdir.mkdir(parents=True, exist_ok=True)
    readme = pdir / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Planning\n\nUse this directory for outlines, notes, and research.\n",
            encoding="utf-8",
        )
    return pdir


# ── File listing ─────────────────────────────────────────────────────────────

def list_planning_files(repo_path: str) -> List[Tuple[str, Path, bool]]:
    """
    Return a flat list of (display_label, absolute_path, is_dir) entries for
    everything inside planning/, sorted folders-first then alphabetically.

    Only .md files and directories are included; hidden entries are skipped.
    Entries are presented at all depths — the display_label is the path
    relative to planning/ so the caller can indent based on depth.
    """
    pdir = planning_dir(repo_path)
    if not pdir.exists():
        return []

    results: List[Tuple[str, Path, bool]] = []

    def _walk(directory: Path, prefix: str) -> None:
        entries = sorted(
            directory.iterdir(),
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )
        for entry in entries:
            if entry.name.startswith("."):
                continue
            rel = f"{prefix}{entry.name}" if prefix else entry.name
            if entry.is_dir():
                results.append((rel, entry, True))
                _walk(entry, f"{rel}/")
            elif entry.suffix.lower() == ".md":
                results.append((rel, entry, False))

    _walk(pdir, "")
    return results


# ── File operations ───────────────────────────────────────────────────────────

def create_planning_file(repo_path: str, rel_path: str) -> Path:
    """
    Create a new .md file at planning/<rel_path>.
    Creates parent directories as needed.
    """
    target = planning_dir(repo_path) / rel_path
    if not rel_path.endswith(".md"):
        target = target.with_suffix(".md")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text(f"# {target.stem}\n\n", encoding="utf-8")
    return target


def create_planning_folder(repo_path: str, rel_path: str) -> Path:
    """Create a new subdirectory under planning/."""
    target = planning_dir(repo_path) / rel_path
    target.mkdir(parents=True, exist_ok=True)
    return target


def delete_planning_entry(path: Path) -> None:
    """Delete a planning file or folder (recursive)."""
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
