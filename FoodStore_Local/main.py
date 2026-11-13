import flet as ft

from UI.app import App


def main(page: ft.Page):
    App(page)


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
