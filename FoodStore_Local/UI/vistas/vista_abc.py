"""Clases base de las vistas y los dos layouts: admin (barra lateral) y cliente (barra superior)."""
from abc import ABC, abstractmethod

import flet as ft

from UI.componentes.alerta import alerta
from UI.componentes.badge import badge, badge_rol
from UI.componentes.boton import boton
from UI.componentes.marca import avatar, logo_con_nombre
from UI.tema import Tema, txt


class Vista(ABC):
    def __init__(self, app, **kwargs):
        self.app = app
        self.page: ft.Page = app.page
        self.servicio = app.servicio

    @abstractmethod
    def construir(self) -> ft.Control: ...


class VistaConMenu(Vista):
    """Vista con menú: se redibuja entera con `refrescar()` después de cada operación."""

    ruta = ""          # clave de la ruta en App.RUTAS, para marcar el ítem activo
    PADDING = ft.Padding.symmetric(horizontal=56, vertical=44)

    def __init__(self, app, aviso=None, **kwargs):
        super().__init__(app, **kwargs)
        self.aviso = aviso                     # (tipo, titulo, detalle) o None
        self.cuerpo = ft.Container(expand=True, padding=self.PADDING)

    @abstractmethod
    def contenido(self) -> list[ft.Control]: ...

    @abstractmethod
    def layout(self, cuerpo: ft.Control) -> ft.Control: ...

    def construir(self):
        self._render()
        return self.layout(self.cuerpo)

    def _render(self):
        controles = self.contenido()
        self.cuerpo.content = ft.Column(controles, spacing=28, scroll=ft.ScrollMode.AUTO, expand=True)

    def refrescar(self, aviso=None):
        self.aviso = aviso
        self._render()
        self.page.update()

    def control_aviso(self):
        """Alerta de resultado de la última operación (éxito o error)."""
        return alerta(*self.aviso) if self.aviso else None

    @staticmethod
    def sin_nulos(*controles):
        return [c for c in controles if c is not None]


# ----------------------------------------------------------------- ADMIN
MENU_ADMIN = [
    ("Inicio", ft.Icons.HOME_OUTLINED, "admin_inicio"),
    ("Categorías", ft.Icons.GRID_VIEW, "admin_categorias"),
    ("Productos", ft.Icons.CROP_SQUARE, "admin_productos"),
    ("Usuarios", ft.Icons.SENTIMENT_SATISFIED_ALT, "admin_usuarios"),
    ("Pedidos", ft.Icons.FORMAT_LIST_BULLETED, "admin_pedidos"),
]


class VistaAdmin(VistaConMenu):
    def _item_menu(self, texto, icono, ruta):
        activo = ruta == self.ruta
        color = Tema.BLANCO if activo else "#D9CFC6"
        return ft.Container(
            bgcolor=Tema.PRIMARIO if activo else None,
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=18, vertical=15),
            ink=True,
            on_click=lambda e: self.app.ir(ruta),
            content=ft.Row([ft.Icon(icono, size=20, color=color),
                            txt(texto, 17, 600 if activo else 500, color)], spacing=16),
        )

    def layout(self, cuerpo):
        u = self.app.usuario
        barra = ft.Container(
            width=270,
            bgcolor=Tema.OSCURO,
            padding=ft.Padding.symmetric(horizontal=22, vertical=34),
            content=ft.Column(
                expand=True,
                controls=[
                    logo_con_nombre(Tema.BLANCO, tam=42),
                    ft.Container(height=24),
                    ft.Column([self._item_menu(*i) for i in MENU_ADMIN], spacing=8),
                    ft.Container(expand=True),
                    ft.Container(
                        bgcolor=Tema.OSCURO_TARJETA, border_radius=14, padding=16,
                        content=ft.Row([
                            avatar(u.iniciales, 44),
                            ft.Column([txt(u.nombre_completo, 16, 600, Tema.BLANCO), ft.Row([badge_rol(u.rol)])],
                                      spacing=4, tight=True),
                        ], spacing=14),
                    ),
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=16, vertical=14), border_radius=12, ink=True,
                        on_click=lambda e: self.app.cerrar_sesion(),
                        content=ft.Row([ft.Icon(ft.Icons.LOGOUT, size=20, color="#D9CFC6"),
                                        txt("Cerrar sesión", 16, 500, "#D9CFC6")], spacing=14),
                    ),
                ],
            ),
        )
        return ft.Row([barra, cuerpo], spacing=0, expand=True,
                      vertical_alignment=ft.CrossAxisAlignment.STRETCH)


# --------------------------------------------------------------- CLIENTE
MENU_CLIENTE = [
    ("Categorías", "cliente_categorias"),
    ("Productos", "cliente_productos"),
    ("Mis pedidos", "cliente_pedidos"),
    ("Mis datos", "cliente_datos"),
]


class VistaCliente(VistaConMenu):
    PADDING = ft.Padding.symmetric(horizontal=60, vertical=44)

    def _item_menu(self, texto, ruta):
        activo = ruta == self.ruta
        return ft.Container(
            bgcolor=Tema.PRIMARIO_SUAVE if activo else None,
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=22, vertical=12),
            ink=True,
            on_click=lambda e: self.app.ir(ruta),
            content=txt(texto, 17, 700 if activo else 500, Tema.PRIMARIO if activo else Tema.TEXTO_SUAVE),
        )

    def layout(self, cuerpo):
        u = self.app.usuario
        barra = ft.Container(
            bgcolor=Tema.BLANCO,
            border=ft.Border.only(bottom=ft.BorderSide(1, Tema.BORDE)),
            padding=ft.Padding.symmetric(horizontal=60, vertical=16),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    logo_con_nombre(Tema.TEXTO, tam=44),
                    ft.Container(width=28),
                    ft.Row([self._item_menu(*i) for i in MENU_CLIENTE], spacing=6),
                    ft.Container(expand=True),
                    avatar(u.iniciales, 46),
                    ft.Column([txt(u.nombre_completo, 16, 600), ft.Row([badge(u.rol.value)])],
                              spacing=2, tight=True),
                    ft.Container(width=8),
                    boton("Cerrar sesión", lambda e: self.app.cerrar_sesion(), "secundario", chico=True),
                ],
            ),
        )
        return ft.Column([barra, cuerpo], spacing=0, expand=True)
