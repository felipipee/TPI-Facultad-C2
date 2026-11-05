"""Tokens del sistema de diseño (diseño/19-sistema-de-diseno.png)."""
import flet as ft


class Tema:
    # Colores base
    PRIMARIO = "#E4572E"
    PRIMARIO_SUAVE = "#FDEBE3"
    OSCURO = "#2B211C"
    OSCURO_HOVER = "#3A2E28"
    OSCURO_TARJETA = "#3D312A"
    FONDO = "#FBF7F1"
    BORDE = "#E9E2D6"
    TEXTO = "#1F1A17"
    TEXTO_SUAVE = "#7A7068"
    BLANCO = "#FFFFFF"

    # Estados
    EXITO, EXITO_BG = "#15803D", "#DCFCE7"
    ALERTA, ALERTA_BG = "#B45309", "#FEF3C7"
    ERROR, ERROR_BG = "#B91C1C", "#FEE2E2"
    INFO, INFO_BG = "#1D4ED8", "#DBEAFE"

    # Neutros auxiliares
    GRIS = "#EFEAE3"            # badges neutros, campos bloqueados
    CABECERA_TABLA = "#F5F1EB"
    DESHABILITADO = "#A8A098"

    RADIO = 12


# Una familia por peso: Flet registra un archivo por familia.
FUENTES = {
    "Inter": "fonts/Inter-400.ttf",
    "Inter500": "fonts/Inter-500.ttf",
    "Inter600": "fonts/Inter-600.ttf",
    "Inter700": "fonts/Inter-700.ttf",
    "Inter800": "fonts/Inter-800.ttf",
}

_FAMILIA_POR_PESO = {400: "Inter", 500: "Inter500", 600: "Inter600", 700: "Inter700", 800: "Inter800"}


def familia(peso: int = 400) -> str:
    return _FAMILIA_POR_PESO.get(peso, "Inter")


def txt(valor, tam=14, peso=400, color=Tema.TEXTO, **kwargs) -> ft.Text:
    """Texto con la tipografía del sistema de diseño."""
    return ft.Text(str(valor), size=tam, font_family=familia(peso), color=color, **kwargs)


def estilo_texto(tam=14, peso=400, color=Tema.TEXTO) -> ft.TextStyle:
    return ft.TextStyle(size=tam, font_family=familia(peso), color=color)


def pesos(monto: float) -> str:
    """21800 -> '$21.800'"""
    return "$" + f"{monto:,.0f}".replace(",", ".")


def aplicar_tema(page: ft.Page):
    page.fonts = FUENTES
    page.theme = ft.Theme(color_scheme_seed=Tema.PRIMARIO, font_family="Inter")
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = Tema.FONDO
    page.padding = 0
    page.spacing = 0
