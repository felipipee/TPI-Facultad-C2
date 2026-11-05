import flet as ft

from UI.componentes.boton import boton
from UI.tema import Tema, txt


def abrir_modal(page: ft.Page, contenido: ft.Control, ancho=560) -> ft.AlertDialog:
    dlg = ft.AlertDialog(
        modal=True,
        bgcolor=Tema.BLANCO,
        shape=ft.RoundedRectangleBorder(radius=24),
        content_padding=0,
        barrier_color=ft.Colors.with_opacity(0.55, Tema.OSCURO),
        content=ft.Container(
            width=ancho,
            padding=ft.Padding.symmetric(horizontal=44, vertical=40),
            content=contenido,
        ),
    )
    page.show_dialog(dlg)
    return dlg


def cerrar_modal(page: ft.Page):
    page.pop_dialog()


def titulo_modal(titulo, subtitulo=None) -> ft.Column:
    hijos = [txt(titulo, 26, 700)]
    if subtitulo:
        hijos.append(txt(subtitulo, 17, color=Tema.TEXTO_SUAVE))
    return ft.Column(hijos, spacing=6)


def pie_modal(*botones) -> ft.Row:
    return ft.Row(list(botones), alignment=ft.MainAxisAlignment.END, spacing=14)


def modal_confirmar(page, titulo, mensaje, texto_ok, on_ok, peligro=True):
    def ok(e):
        cerrar_modal(page)
        on_ok()

    abrir_modal(page, ft.Column(tight=True, spacing=24, controls=[
        titulo_modal(titulo),
        txt(mensaje, 16, color=Tema.TEXTO_SUAVE),
        pie_modal(
            boton("Cancelar", lambda e: cerrar_modal(page), "secundario"),
            boton(texto_ok, ok, "peligro" if peligro else "primario"),
        ),
    ]))
