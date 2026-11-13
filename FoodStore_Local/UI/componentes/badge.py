import flet as ft

from UI.datos_demo import Estado, Rol
from UI.tema import Tema, txt

TONOS_ESTADO = {
    Estado.PENDIENTE: (Tema.ALERTA_BG, Tema.ALERTA),
    Estado.CONFIRMADO: (Tema.INFO_BG, Tema.INFO),
    Estado.TERMINADO: (Tema.EXITO_BG, Tema.EXITO),
    Estado.CANCELADO: (Tema.ERROR_BG, Tema.ERROR),
}


def badge(texto, fondo=Tema.GRIS, color=Tema.TEXTO_SUAVE, tam=13) -> ft.Container:
    return ft.Container(
        content=txt(texto, tam, 600, color),
        bgcolor=fondo,
        padding=ft.Padding.symmetric(horizontal=12, vertical=4),
        border_radius=999,
    )


def badge_estado(estado: Estado) -> ft.Container:
    fondo, color = TONOS_ESTADO[estado]
    return badge(estado.value, fondo, color)


def badge_rol(rol: Rol) -> ft.Container:
    if rol == Rol.ADMIN:
        return badge("ADMIN", Tema.PRIMARIO_SUAVE, Tema.PRIMARIO)
    return badge("USUARIO")


def badge_producto(producto) -> ft.Container:
    if not producto.disponible:
        return badge("No disponible")
    if producto.stock <= 0:
        return badge("Sin stock", Tema.ERROR_BG, Tema.ERROR)
    return badge("Disponible", Tema.EXITO_BG, Tema.EXITO)


def envolver(control: ft.Control) -> ft.Row:
    """Evita que un badge se estire a todo el ancho de su celda."""
    return ft.Row([control], tight=True)
