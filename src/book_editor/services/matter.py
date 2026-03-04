"""Front matter and back matter section management."""

import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from book_editor.services.chapter_version import ChapterVersionManager


FRONT_MATTER_ORDER: List[str] = [
    "Copyright",
    "Dedication",
    "Epigraph",
    "Foreword",
    "Preface",
    "Prologue",
    "Acknowledgements",
]

BACK_MATTER_ORDER: List[str] = [
    "Epilogue",
    "Afterword",
    "Appendix",
    "Sources",
    "Glossary",
    "Index",
    "Acknowledgements",
    "About the Author",
    "Preview",
    "Call to Action",
]


def _matter_dir(repo_path: str, kind: str) -> Path:
    """Return Path to FrontMatter/ or BackMatter/ directory."""
    if kind == "front":
        return Path(repo_path) / "FrontMatter"
    elif kind == "back":
        return Path(repo_path) / "BackMatter"
    else:
        raise ValueError(f"kind must be 'front' or 'back', got: {kind!r}")


def _canonical_order(kind: str) -> List[str]:
    return FRONT_MATTER_ORDER if kind == "front" else BACK_MATTER_ORDER


def list_matter_sections(repo_path: str, kind: str) -> List[Tuple[str, Path]]:
    """Return list of (name, latest_md_path) in canonical order for existing sections."""
    base = _matter_dir(repo_path, kind)
    if not base.exists():
        return []
    manager = ChapterVersionManager()
    result = []
    for name in _canonical_order(kind):
        section_dir = base / name
        if not section_dir.is_dir():
            continue
        try:
            latest_ver = manager.get_latest_version(section_dir)
            md_path = manager.get_markdown_file(latest_ver)
            result.append((name, md_path))
        except Exception:
            continue
    return result


# Sections whose content should be centered on the page (standard book formatting).
# Applied transparently at PDF build time — source files stay as plain markdown.
CENTERED_MATTER_SECTIONS: frozenset = frozenset({"Dedication", "Epigraph"})


def create_matter_section(repo_path: str, kind: str, name: str) -> Path:
    """Create a new matter section with v1.0.0 and return the md file Path."""
    base = _matter_dir(repo_path, kind)
    base.mkdir(exist_ok=True)
    section_dir = base / name
    if section_dir.exists():
        raise ValueError(f"Section '{name}' already exists in {base.name}.")
    ver_dir = section_dir / "v1.0.0"
    ver_dir.mkdir(parents=True)
    md_file = ver_dir / "v1.0.0.md"
    md_file.write_text("", encoding="utf-8")
    return md_file


def delete_matter_section(repo_path: str, kind: str, name: str) -> None:
    """Delete a matter section directory tree."""
    base = _matter_dir(repo_path, kind)
    section_dir = base / name
    if section_dir.exists():
        shutil.rmtree(section_dir)


def get_all_matter_files(repo_path: str, kind: str) -> List[Path]:
    """Return ordered list of latest md Paths for all existing matter sections."""
    return [md for _name, md in list_matter_sections(repo_path, kind)]
