import flet as ft

from UI.tema import Tema, txt

# tipo -> (fondo, color, símbolo)
_TIPOS = {
    "error": (Tema.ERROR_BG, Tema.ERROR, "!"),
    "warn": (Tema.ALERTA_BG, Tema.ALERTA, "!"),
    "info": (Tema.INFO_BG, Tema.INFO, "i"),
    "ok": (Tema.EXITO_BG, Tema.EXITO, None),
}


def alerta(tipo, titulo, detalle=None, expand=False, width=None) -> ft.Container:
    fondo, color, simbolo = _TIPOS[tipo]
    icono = (txt(simbolo, 15, 800, Tema.BLANCO) if simbolo
             else ft.Icon(ft.Icons.CHECK, size=17, color=Tema.BLANCO))
    textos = [txt(titulo, 16, 700, color)]
    if detalle:
        textos.append(txt(detalle, 15, color=Tema.TEXTO))
    return ft.Container(
        bgcolor=fondo,
        border=ft.Border.all(1.2, color),
        border_radius=14,
        padding=ft.Padding.symmetric(horizontal=20, vertical=16),
        expand=expand,
        width=width,
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=14,
            controls=[
                ft.Container(icono, width=28, height=28, border_radius=14, bgcolor=color,
                             alignment=ft.Alignment.CENTER, margin=ft.Margin.only(top=2)),
                ft.Column(textos, spacing=2, expand=True),
            ],
        ),
    )
