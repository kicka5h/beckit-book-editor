"""Entry point for the Beckit desktop app (python -m book_editor or beckit)."""

import os
from pathlib import Path

import flet as ft

from book_editor.app import main as app_main

# Temp directory used as Flet's static-asset root in web mode so generated
# PDFs can be served for browser download via page.launch_url().
WEB_DOWNLOADS_DIR = Path("/tmp/beckit_web_downloads")


def run_gui() -> None:
    """Run the Flet application.

    Set BECKIT_WEB=1 to serve on http://0.0.0.0:8080 instead of opening a
    native desktop window — used by the Docker dev container.
    """
    if os.environ.get("BECKIT_WEB"):
        WEB_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
        ft.app(
            target=app_main,
            view=ft.AppView.WEB_BROWSER,
            host="0.0.0.0",
            port=8080,
            assets_dir=str(WEB_DOWNLOADS_DIR),
        )
    else:
        ft.app(target=app_main)


if __name__ == "__main__":
    run_gui()
