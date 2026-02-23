<div align="center">
  
# Beckit

</div>

<div align="center">
  
> A lightweight desktop app for writing books — with GitHub sync, chapter versioning, and PDF export. Always free, always open source. Developed with the help of Claude.

[![Download](https://img.shields.io/github/release/tterb/PlayMusic.svg?style=flat)](https://github.com/kicka5h/beckit-book-editor/releases/latest)
[![CI](../../actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Open Source](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://opensource.org/)

</div>

---

<div align="center">

| [👤 &nbsp;For Users](#-for-users) | [🛠 &nbsp;For Developers](#-for-developers) |
|:---:|:---:|

</div>

---

## 👤 For Users

- [Beckit](#beckit)
  - [👤 For Users](#-for-users)
    - [Download \& Install](#download--install)
      - [macOS](#macos)
      - [Windows](#windows)
    - [First Launch](#first-launch)
    - [Writing Chapters](#writing-chapters)
    - [Planning Pane](#planning-pane)
    - [Version History](#version-history)
    - [GitHub Sync](#github-sync)
    - [PDF Export](#pdf-export)
    - [Word Count](#word-count)
    - [CLI Tools](#cli-tools)
  - [🛠 For Developers](#-for-developers)
    - [Docker Dev Container](#docker-dev-container)
    - [Run from Source](#run-from-source)
    - [Running Tests](#running-tests)
    - [Project Layout](#project-layout)
    - [Contributing](#contributing)
  - [License](#license)

---

### Download & Install

Beckit is distributed as a prebuilt installer — no Python or developer tools required. Download the version for your platform from the [latest release](../../releases/latest).

#### macOS

**Requirements:** macOS 11 (Big Sur) or later

1. Download `Beckit-macOS-<version>.pkg` from the [latest release](../../releases/latest)
2. Double-click the `.pkg` file and follow the installer wizard
3. Open **Launchpad** or your **Applications** folder and launch **Beckit**

> **"App can't be opened because it is from an unidentified developer"**
> The app is not yet signed with an Apple Developer certificate. To open it: right-click (or Control-click) the app icon → **Open** → **Open** again in the dialog. You only need to do this once.

#### Windows

**Requirements:** Windows 10 or later (64-bit)

1. Download `Beckit-Windows-<version>-installer.exe` from the [latest release](../../releases/latest)
2. Run the installer (Administrator rights may be required)
3. Launch **Beckit** from the Start Menu or Desktop shortcut

> **Windows Defender SmartScreen warning ("Windows protected your PC")**
> The app is not yet code-signed. Click **More info** → **Run anyway** to proceed.

---

### First Launch

The first time you open Beckit you will be asked to connect your GitHub account:

1. Click **Sign in with GitHub** — a code will appear on screen
2. Visit [github.com/login/device](https://github.com/login/device) and enter the code
3. Authorize Beckit, then return to the app — it will detect the sign-in automatically
4. Select an existing GitHub repository to use as your book, or create a new one

Beckit will clone your repository locally and set up the `Chapters/` and `Planning/` folders automatically.

Your settings are stored in your system config directory:

| Platform | Config location |
|---|---|
| macOS | `~/Library/Application Support/beckit/` |
| Windows | `%APPDATA%\beckit\` |

---

### Writing Chapters

The main editor is split into three areas:

- **Chapters pane** (left) — lists all your chapters with their current version numbers
- **Editor** (centre) — click any text to start editing; click away to return to the styled preview
- **Version history** (right) — a read-only view of every saved version of the current chapter

**Creating a chapter**

Click **+ New Chapter** at the bottom of the chapters pane. The new chapter is numbered automatically and starts at version `v1.0.0`.

**Editing**

Click anywhere in the preview to enter edit mode. The editor accepts standard Markdown. Click outside the editor (or switch to another pane) to save and return to the preview.

**Saving**

Click **Save** in the toolbar. Beckit automatically:
- Detects how much the content has changed
- Bumps the chapter version accordingly (patch → minor → major)
- Pushes the updated file to GitHub

A `● unsaved` indicator appears in the status bar whenever the current document has unsaved changes.

**Reordering chapters**

Drag the handle icon next to any chapter name to reorder it in the list.

**Deleting a chapter**

Select a chapter, open the overflow menu (⋯), and choose **Delete chapter**. You will be asked to confirm before anything is removed.

**Scratch pad**

The scratch pad is a free-form area that is always available, even when no chapter is open. When you save scratch pad content you can choose to:
- Create a new chapter from it
- Append it to an existing chapter
- Save it as a new planning file
- Append it to an existing planning file

---

### Planning Pane

The planning pane is a separate space for outlines, research notes, character sheets, and anything else that supports your writing but is not part of the manuscript.

- Toggle it open with the **Planning** button in the toolbar
- Files and folders are stored under `Planning/` in your repository
- Create new files or folders using the **+** buttons at the top of the pane
- Click any file to open it in the same preview/edit editor as chapters
- Changes are saved automatically when you click away

---

### Version History

Every time you save a chapter, Beckit records a new version in a `vMAJOR.MINOR.PATCH` subfolder. The version history pane on the right shows all saved versions:

- Click any version to view it in the read-only history panel
- Click **Restore this version** to copy that version's content into the editor

The folder structure inside your repository looks like this:

```
Chapters/
  Chapter 1/
    v1.0.0/
      v1.0.0.md
    v1.1.0/
      v1.1.0.md
  Chapter 2/
    v1.0.0/
      v1.0.0.md
```

---

### GitHub Sync

Beckit syncs your work to GitHub automatically:

- **On startup** — pulls the latest changes from your repository before you start writing
- **On save** — pushes the new version to GitHub immediately after saving
- **Switch repository** — use the repository button in the toolbar to switch to a different book

---

### PDF Export

Generate a PDF of your entire book from the toolbar's **Export PDF** button.

1. Enter your **Book title** and **Author name**
2. Optionally click **Choose…** to pick a custom save location
3. Click **Generate PDF** to create the file, or **Save & Open** to create it and open it immediately in your default PDF viewer

PDF export uses Pandoc and pdflatex, which are bundled with the app — no separate installation required.

---

### Word Count

The status bar at the bottom of the window shows:
- **Current document** word count (updates as you type)
- **Total book** word count across all latest chapter versions

---

### CLI Tools

After installing from source (see the Developer section), these commands are available from any directory that contains a `Chapters/` folder:

| Command | Description |
|---|---|
| `chapter-version list` | List all chapters and their current versions |
| `chapter-version minor -c 5` | Bump the minor version for chapter 5 |
| `chapter-version patch -c 1 2 3` | Bump the patch version for chapters 1–3 |
| `chapter-version major --all` | Bump the major version for all chapters |
| `create-chapter` | Create the next chapter (e.g. Chapter 11) at v1.0.0 |
| `increment-chapters 6` | Shift chapter numbers up: Chapter 6 → 7, 7 → 8, … |
| `count-chapter-words` | Word count for the latest version of each chapter |
| `format-markdown -r -i .` | Format all Markdown files in place |

Use `-d /path/to/Chapters` to point any tool at a specific directory.

---

## 🛠 For Developers

- [Docker Dev Container](#docker-dev-container)
- [Run from Source](#run-from-source)
- [Running Tests](#running-tests)
- [Project Layout](#project-layout)
- [Contributing](#contributing)

---

### Docker Dev Container

The fastest way to get a fully working development environment is with Docker. No Python, LaTeX, or system dependencies required — everything runs inside the container and is accessible in your browser.

**Requirements:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS / Windows / Linux)

```bash
git clone https://github.com/kicka5h/beckit-book-editor.git
cd beckit-book-editor
docker compose up app
```

Open **http://localhost:8080** in your browser. The app is fully functional — connect your GitHub account and start writing.

Source code is mounted into the container, so any edits you make to files under `src/` are reflected without rebuilding the image.

**Run the test suite inside the container:**

```bash
docker compose run --rm test
```

**Pull the published image from GitHub Container Registry:**

```bash
docker pull ghcr.io/kicka5h/beckit:latest
docker run -p 8080:8080 ghcr.io/kicka5h/beckit:latest
```

Then open **http://localhost:8080**.

---

### Run from Source

If you prefer a native Python environment:

**Requirements:** Python 3.9–3.12

```bash
git clone https://github.com/kicka5h/beckit-book-editor.git
cd beckit-book-editor

python3 -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -e .
python -m book_editor   # or: beckit
```

**PDF export** (optional — only needed if you use the Export PDF feature):
- **macOS:** `brew install pandoc && brew install --cask mactex-no-gui`
- **Windows:** Download [Pandoc](https://pandoc.org/installing.html) and [MiKTeX](https://miktex.org/download)
- **Linux:** `apt install pandoc texlive-latex-base texlive-fonts-recommended`

Alternatively, run `./run.sh` on macOS — it installs all dependencies automatically via Homebrew.

---

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

Or with coverage:

```bash
pytest --cov=book_editor tests/
```

---

### Project Layout

```
beckit-book-editor/
├── pyproject.toml              # Package metadata and dependencies
├── docker/
│   └── Dockerfile              # Dev container image
├── docker-compose.yml          # App (port 8080) and test services
├── installer/
│   ├── macos/                  # PKG installer scripts
│   └── windows/                # NSIS installer script
├── src/
│   └── book_editor/
│       ├── __main__.py         # Entry point (python -m book_editor)
│       ├── app.py              # Main Flet UI
│       ├── config/             # App config (repo path, GitHub token)
│       ├── services/           # Business logic (chapters, versioning, PDF, git)
│       └── utils/              # Path helpers, chapter number utilities
├── tests/
│   ├── api/
│   ├── services/
│   ├── repositories/
│   └── utils/
└── .github/
    └── workflows/
        ├── ci.yml              # Tests + Docker build on every PR
        └── cd.yml              # Release builds, PyPI publish, GHCR publish
```

---

### Contributing

1. **Fork** the repository and create a branch from `main`
2. Make your changes — fix a bug, add a feature, improve docs
3. Ensure all tests pass: `pytest`
4. Open a **Pull Request** against `main` with a clear description of what changed and why

**CI runs automatically on every PR:**
- Unit tests across Python 3.9–3.12 on Ubuntu 22.04 and 24.04
- Build checks on macOS 14, macOS 15, Windows 2019, Windows 2022
- Docker image build and test suite inside the container

Please open an [issue](../../issues) before starting large changes so we can discuss the approach first.

---

## License

[MIT](LICENSE)
