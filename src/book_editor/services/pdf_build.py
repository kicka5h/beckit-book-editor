"""Build a single PDF from the latest version of each chapter (same logic as generate_book_pdf workflow)."""

import os
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, Optional


# ── Bundled binary resolution ──────────────────────────────────────────────────


def _resources_dir() -> Optional[Path]:
    """Return path to bundled Resources directory when running from a packaged app.

    macOS .app bundle layout:  Beckit.app/Contents/MacOS/python (sys.executable)
                                → Beckit.app/Contents/Resources/
    Windows onedir layout:     Beckit/Beckit.exe (sys.executable)
                                → Beckit/bin/pandoc.exe  (no Resources subdir)
    Returns None in dev/pip-install mode so callers fall back to system PATH.
    """
    exe = Path(sys.executable)
    # macOS: go up two levels from Contents/MacOS → Contents/Resources
    mac = exe.parent.parent / "Resources"
    if mac.is_dir() and (mac / "bin").exists():
        return mac
    # Windows onedir: exe lives in the bundle root; check for bin/pandoc.exe sentinel
    win = exe.parent
    if (win / "bin" / "pandoc.exe").exists():
        return win
    return None


def _resolve_bin(name: str) -> str:
    """Return absolute path to a bundled binary, or bare name for PATH fallback."""
    res = _resources_dir()
    if res:
        if sys.platform == "darwin":
            candidate = res / "bin" / name
            if candidate.exists():
                return str(candidate)
        elif sys.platform == "win32":
            candidate = res / "bin" / (name + ".exe")
            if candidate.exists():
                return str(candidate)
    return name  # dev mode — rely on system PATH


def _augmented_env() -> dict:
    """Return os.environ copy with bundled and known system paths prepended.

    Prepends bundled bin/ and tinytex/ paths so subprocess calls find the
    right binaries even when launched from a GUI (Dock/Start Menu) where
    the inherited PATH is stripped of Homebrew/TeX Live directories.
    """
    env = os.environ.copy()
    extra: List[str] = []

    res = _resources_dir()
    if res:
        if sys.platform == "darwin":
            extra.append(str(res / "bin"))
            tinytex_bin = res / "tinytex" / "bin" / "universal-darwin"
            if tinytex_bin.exists():
                extra.append(str(tinytex_bin))
        elif sys.platform == "win32":
            extra.append(str(res / "bin"))
            tinytex_bin = res / "tinytex" / "bin" / "windows"
            if tinytex_bin.exists():
                extra.append(str(tinytex_bin))

    # Fallback system paths for dev mode (no-op when bundled paths take priority)
    if sys.platform == "darwin":
        extra += ["/Library/TeX/texbin", "/opt/homebrew/bin", "/usr/local/bin"]

    env["PATH"] = os.pathsep.join(extra) + os.pathsep + env.get("PATH", "")
    return env


# ── Chapter discovery ──────────────────────────────────────────────────────────


def get_latest_chapter_files(chapters_dir: Path) -> List[Path]:
    """
    Collect the latest version of each chapter's markdown file, in chapter order.
    Returns list of Paths to .md files.
    """
    def parse_version(version_str: str) -> Optional[tuple]:
        match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", version_str)
        if not match:
            return None
        return tuple(map(int, match.groups()))

    if not chapters_dir.exists() or not chapters_dir.is_dir():
        return []

    chapter_dirs = sorted(
        [
            d
            for d in chapters_dir.iterdir()
            if d.is_dir() and d.name.lower().startswith("chapter")
        ],
        key=lambda x: int(re.search(r"\d+", x.name).group()) if re.search(r"\d+", x.name) else 0,
    )

    latest_chapters = []
    for chapter_dir in chapter_dirs:
        version_dirs = []
        for version_dir in chapter_dir.iterdir():
            if version_dir.is_dir() and version_dir.name.startswith("v"):
                version = parse_version(version_dir.name)
                if version:
                    version_dirs.append((version, version_dir))
        if not version_dirs:
            continue
        version_dirs.sort(key=lambda x: x[0], reverse=True)
        latest_version_dir = version_dirs[0][1]
        md_files = list(latest_version_dir.glob("*.md"))
        if md_files:
            latest_chapters.append(md_files[0])
    return latest_chapters


# ── PDF generation ─────────────────────────────────────────────────────────────


@contextmanager
def _prepared_files(files: List[Path]) -> Iterator[List[str]]:
    """Yield a list of file path strings for pandoc, wrapping centered sections in temp files."""
    from book_editor.services.matter import CENTERED_MATTER_SECTIONS
    tmp_files: List[tempfile.NamedTemporaryFile] = []
    paths: List[str] = []
    try:
        for f in files:
            section_name = f.parent.parent.name  # .../SectionName/vX.Y.Z/vX.Y.Z.md
            if section_name in CENTERED_MATTER_SECTIONS:
                content = f.read_text(encoding="utf-8")
                wrapped = f"\\begin{{center}}\n{content}\n\\end{{center}}\n"
                tmp = tempfile.NamedTemporaryFile(
                    mode="w", suffix=".md", delete=False, encoding="utf-8"
                )
                tmp.write(wrapped)
                tmp.flush()
                tmp.close()
                tmp_files.append(tmp)
                paths.append(tmp.name)
            else:
                paths.append(str(f))
        yield paths
    finally:
        for tmp in tmp_files:
            try:
                Path(tmp.name).unlink(missing_ok=True)
            except Exception:
                pass


def build_pdf(
    repo_path: str,
    output_path: Optional[Path] = None,
    title: str = "Book",
    author: str = "",
) -> Path:
    """
    Generate a single PDF from the latest version of each chapter using pandoc.
    Uses bundled pandoc/pdflatex when running from the packaged app; falls back
    to system PATH in dev mode.
    Returns the path to the generated PDF.
    """
    from book_editor.services.matter import get_all_matter_files
    front_files = get_all_matter_files(repo_path, "front")
    chapter_files = get_latest_chapter_files(Path(repo_path) / "Chapters")
    back_files = get_all_matter_files(repo_path, "back")
    files = front_files + chapter_files + back_files
    if not files:
        raise ValueError("No content found to build PDF.")

    if output_path is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_") or "Book"
        output_path = Path(repo_path) / f"{safe_title}_{date_str}.pdf"
    output_path = Path(output_path)

    date_str = datetime.now().strftime("%Y-%m-%d")
    with _prepared_files(files) as file_paths:
        cmd = [
            _resolve_bin("pandoc"),
            *file_paths,
            "-o",
            str(output_path),
            "--pdf-engine=pdflatex",
            "-V", "geometry:margin=1in",
            "-V", "fontsize=12pt",
            "-V", "documentclass=book",
            "-V", "papersize=letter",
            "--toc",
            "--toc-depth=2",
            "-V", f"title={title}",
            "-V", f"author={author}",
            "-V", f"date={date_str}",
            "--highlight-style=tango",
            "--number-sections",
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=repo_path, env=_augmented_env()
        )
    if result.returncode != 0:
        raise RuntimeError(
            f"Pandoc failed: {result.stderr or result.stdout or 'unknown error'}"
        )
    return output_path


# ── Availability checks ────────────────────────────────────────────────────────


def check_pandoc_available() -> bool:
    """Return True if pandoc is available (bundled or on PATH)."""
    try:
        result = subprocess.run(
            [_resolve_bin("pandoc"), "--version"],
            capture_output=True,
            text=True,
            env=_augmented_env(),
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_pdflatex_available() -> bool:
    """Return True if pdflatex is available (bundled or on PATH)."""
    try:
        result = subprocess.run(
            [_resolve_bin("pdflatex"), "--version"],
            capture_output=True,
            text=True,
            env=_augmented_env(),
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
