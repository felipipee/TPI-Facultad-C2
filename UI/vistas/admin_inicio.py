"""Pantalla 04: inicio del administrador."""
import flet as ft

from UI.componentes.badge import badge
from UI.datos_demo import Estado
from UI.tema import Tema, txt
from UI.vistas.vista_abc import VistaAdmin


class VistaAdminInicio(VistaAdmin):
    ruta = "admin_inicio"

    def _modulo(self, titulo, descripcion, cantidad, icono, ruta):
        return ft.Container(
            expand=True, bgcolor=Tema.BLANCO, border=ft.Border.all(1, Tema.BORDE), border_radius=22,
            padding=ft.Padding.symmetric(horizontal=36, vertical=44), ink=True,
            on_click=lambda e: self.app.ir(ruta),
            content=ft.Row(spacing=30, controls=[
                ft.Container(ft.Icon(icono, size=34, color=Tema.PRIMARIO), width=100, height=100,
                             border_radius=20, bgcolor=Tema.PRIMARIO_SUAVE, alignment=ft.Alignment.CENTER),
                ft.Column(expand=True, spacing=8, controls=[
                    txt(titulo, 28, 700),
                    txt(descripcion, 17, color=Tema.TEXTO_SUAVE),
                    ft.Row([badge(cantidad, tam=15)]),
                ]),
            ]),
        )

    def _dato(self, titulo, valor, color):
        return ft.Container(
            expand=True, bgcolor=Tema.BLANCO, border=ft.Border.all(1, Tema.BORDE), border_radius=20,
            padding=ft.Padding.symmetric(horizontal=30, vertical=28),
            content=ft.Column([txt(titulo, 17, color=Tema.TEXTO_SUAVE), txt(valor, 44, 800, color)], spacing=4),
        )

    def contenido(self):
        s = self.servicio
        cats, prods, users, peds = s.categorias(), s.productos(), s.usuarios(), s.pedidos()

        def plural(n, uno, varios):
            return f"{n} {uno if n == 1 else varios}"

        return [
            ft.Column([txt(f"Hola, {self.app.usuario.nombre}", 44, 800),
                       txt(f"Panel de administración · rol {self.app.usuario.rol.value}", 18, color=Tema.TEXTO_SUAVE)],
                      spacing=4),
            ft.Row(spacing=32, controls=[
                self._modulo("Categorías", "Organizá el catálogo: listar, crear, editar y eliminar.",
                             plural(len(cats), "categoría", "categorías"), ft.Icons.GRID_ON, "admin_categorias"),
                self._modulo("Productos", "Precios, stock y disponibilidad de cada producto.",
                             plural(len(prods), "producto", "productos"), ft.Icons.CROP_SQUARE, "admin_productos"),
            ]),
            ft.Row(spacing=32, controls=[
                self._modulo("Usuarios", "Altas, bajas y roles de administradores y clientes.",
                             plural(len(users), "usuario", "usuarios"), ft.Icons.SENTIMENT_SATISFIED_ALT, "admin_usuarios"),
                self._modulo("Pedidos", "Seguimiento de estados, formas de pago y detalles.",
                             plural(len(peds), "pedido", "pedidos"), ft.Icons.FORMAT_LIST_BULLETED, "admin_pedidos"),
            ]),
            txt("Resumen", 22, 700),
            ft.Row(spacing=32, controls=[
                self._dato("Pedidos pendientes", sum(p.estado == Estado.PENDIENTE for p in peds), Tema.ALERTA),
                self._dato("Productos sin stock", sum(p.stock == 0 for p in prods), Tema.ERROR),
                self._dato("Usuarios activos", len(users), Tema.TEXTO),
            ]),
        ]
