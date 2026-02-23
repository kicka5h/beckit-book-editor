"""Entry point for the Beckit desktop app (python -m book_editor or beckit)."""

import os

import flet as ft

from book_editor.app import main as app_main


def run_gui() -> None:
    """Run the Flet application.

    Set BECKIT_WEB=1 to serve on http://0.0.0.0:8080 instead of opening a
    native desktop window — used by the Docker dev container.
    """
    if os.environ.get("BECKIT_WEB"):
        ft.app(
            target=app_main,
            view=ft.AppView.WEB_BROWSER,
            host="0.0.0.0",
            port=8080,
        )
    else:
        ft.app(target=app_main)


if __name__ == "__main__":
    run_gui()
