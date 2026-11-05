"""Tabla con cabecera crema, filas blancas y bordes redondeados (no usa DataTable
para poder igualar el diseño y permitir filas clickeables)."""
import flet as ft

from UI.tema import Tema, txt


def _celda(valor, flex):
    contenido = txt(valor, 15) if isinstance(valor, (str, int, float)) else valor
    return ft.Container(contenido, expand=flex)


def tabla(columnas, filas, on_click_fila=None, seleccionada=None, datos_filas=None,
          alto_fila=72) -> ft.Container:
    """
    columnas: [(titulo, flex)]
    filas: [[valor_o_control, ...]]
    on_click_fila(dato): si se pasa, las filas son clickeables. `datos_filas`
    tiene el dato asociado a cada fila (ej. id del pedido); `seleccionada` resalta una.
    """
    flexes = [f for _, f in columnas]
    pad = ft.Padding.symmetric(horizontal=28)

    cabecera = ft.Container(
        bgcolor=Tema.CABECERA_TABLA,
        padding=ft.Padding.symmetric(horizontal=28, vertical=20),
        content=ft.Row([_celda(txt(t.upper(), 13, 600, Tema.TEXTO_SUAVE), f) for t, f in columnas]),
    )

    def click(e):
        on_click_fila(e.control.data)

    renglones = []
    for i, fila in enumerate(filas):
        dato = datos_filas[i] if datos_filas else None
        renglones.append(ft.Container(
            height=alto_fila,
            padding=pad,
            bgcolor=Tema.PRIMARIO_SUAVE if (seleccionada is not None and dato == seleccionada) else Tema.BLANCO,
            border=ft.Border.only(top=ft.BorderSide(1, Tema.BORDE)),
            data=dato,
            on_click=click if on_click_fila else None,
            content=ft.Row([_celda(v, f) for v, f in zip(fila, flexes)],
                           vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ))

    if not filas:
        renglones.append(ft.Container(
            padding=32, bgcolor=Tema.BLANCO, alignment=ft.Alignment.CENTER,
            border=ft.Border.only(top=ft.BorderSide(1, Tema.BORDE)),
            content=txt("No hay registros para mostrar.", 15, color=Tema.TEXTO_SUAVE),
        ))

    return ft.Container(
        border=ft.Border.all(1, Tema.BORDE),
        border_radius=18,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        bgcolor=Tema.BLANCO,
        content=ft.Column([cabecera, *renglones], spacing=0),
    )


def acciones(*botones) -> ft.Row:
    return ft.Row(list(botones), spacing=10)
