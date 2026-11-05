"""Piezas visuales reutilizables: logo, avatar, tarjeta, encabezado, imagen de producto."""
import flet as ft

from UI.tema import Tema, txt


def logo(tam=40, fondo=Tema.PRIMARIO, color_letra=Tema.BLANCO) -> ft.Container:
    return ft.Container(
        content=txt("F", tam * 0.55, 800, color_letra),
        width=tam, height=tam, border_radius=tam * 0.25,
        bgcolor=fondo, alignment=ft.Alignment.CENTER,
    )


def logo_con_nombre(color_texto=Tema.TEXTO, tam=40, **kw) -> ft.Row:
    return ft.Row([logo(tam, **kw), txt("Food Store", tam * 0.55, 700, color_texto)], spacing=14)


def avatar(iniciales, tam=44) -> ft.Container:
    return ft.Container(
        content=txt(iniciales, tam * 0.38, 700, Tema.BLANCO),
        width=tam, height=tam, border_radius=tam / 2,
        bgcolor=Tema.PRIMARIO, alignment=ft.Alignment.CENTER,
    )


def tarjeta(contenido, padding=36, **kw) -> ft.Container:
    return ft.Container(
        content=contenido, padding=padding, bgcolor=Tema.BLANCO,
        border=ft.Border.all(1, Tema.BORDE), border_radius=20, **kw,
    )


def encabezado(titulo, subtitulo=None, accion: ft.Control | None = None) -> ft.Row:
    textos = ft.Column([txt(titulo, 40, 800)], spacing=4)
    if subtitulo:
        textos.controls.append(txt(subtitulo, 17, color=Tema.TEXTO_SUAVE))
    hijos = [textos]
    if accion:
        hijos.append(accion)
    return ft.Row(hijos, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  vertical_alignment=ft.CrossAxisAlignment.START)


def nota(texto) -> ft.Text:
    return txt(texto, 14, color=Tema.TEXTO_SUAVE)


def etiqueta_seccion(texto) -> ft.Text:
    return txt(texto.upper(), 13, 700, Tema.TEXTO_SUAVE)


# Colores de la "foto" de cada categoría: (fondo, plato)
_COLORES_CATEGORIA = {
    "hamburguesas": ("#FDE8D7", "#C2410C"),
    "pizzas": ("#FEF3C7", "#D97706"),
    "bebidas": ("#E0F2FE", "#8B1C1C"),
    "postres": ("#FCE7F3", "#B45309"),
    "ensaladas": ("#DCFCE7", "#15803D"),
}


def imagen_producto(nombre_categoria: str, alto=150) -> ft.Container:
    fondo, plato = _COLORES_CATEGORIA.get((nombre_categoria or "").lower(), ("#F3EDE4", Tema.PRIMARIO))
    diametro = alto * 0.78
    interior = diametro * 0.72
    brillo = interior * 0.3
    return ft.Container(
        height=alto,
        bgcolor=fondo,
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=diametro, height=diametro, border_radius=diametro / 2,
            bgcolor="#FFFBF8", alignment=ft.Alignment.CENTER,
            content=ft.Container(
                width=interior, height=interior, border_radius=interior / 2, bgcolor=plato,
                alignment=ft.Alignment(-0.5, -0.5),
                content=ft.Container(width=brillo, height=brillo, border_radius=brillo / 2,
                                     bgcolor=ft.Colors.with_opacity(0.35, Tema.BLANCO)),
            ),
        ),
    )
