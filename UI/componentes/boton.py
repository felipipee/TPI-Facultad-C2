import flet as ft

from UI.tema import Tema, txt

# tipo -> (fondo, texto, borde)
_TIPOS = {
    "primario": (Tema.PRIMARIO, Tema.BLANCO, None),
    "secundario": (Tema.BLANCO, Tema.TEXTO, Tema.BORDE),
    "peligro": (Tema.ERROR_BG, Tema.ERROR, None),
    "deshabilitado": (Tema.GRIS, Tema.DESHABILITADO, None),
}


def boton(texto, on_click=None, tipo="primario", deshabilitado=False, chico=False,
          icono=None, expand=False, width=None, data=None) -> ft.Button:
    """Botones del sistema de diseño: primario, secundario, peligro, deshabilitado y chico."""
    if deshabilitado:
        tipo = "deshabilitado"
    fondo, color, borde = _TIPOS[tipo]

    tam = 14 if chico else 15
    etiqueta = txt(texto, tam, 600, color)
    contenido = etiqueta
    if icono:
        contenido = ft.Row([ft.Icon(icono, size=tam + 3, color=color), etiqueta],
                           tight=True, spacing=6)

    return ft.Button(
        content=contenido,
        on_click=on_click,
        disabled=deshabilitado,
        expand=expand,
        width=width,
        data=data,
        style=ft.ButtonStyle(
            bgcolor=fondo,
            color=color,
            elevation=0,
            overlay_color=ft.Colors.with_opacity(0.08, Tema.TEXTO if tipo != "primario" else Tema.BLANCO),
            side=ft.BorderSide(1, borde) if borde else None,
            shape=ft.RoundedRectangleBorder(radius=8 if chico else 12),
            padding=ft.Padding.symmetric(horizontal=16, vertical=10) if chico
            else ft.Padding.symmetric(horizontal=26, vertical=20),
        ),
    )
