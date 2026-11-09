import sys
from pathlib import Path

import flet as ft

# Si se ejecuta este archivo directamente (botón ▶ de VS Code), Python solo ve la carpeta UI/
# y no encuentra el paquete "UI". Agregamos la raíz del proyecto al path.
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from UI.datos_demo import Rol, ServicioDemo
from UI.tema import aplicar_tema
from UI.vistas.admin_categorias import VistaAdminCategorias
from UI.vistas.admin_inicio import VistaAdminInicio
from UI.vistas.admin_pedidos import VistaAdminPedidoForm, VistaAdminPedidos
from UI.vistas.admin_productos import VistaAdminProductoForm, VistaAdminProductos
from UI.vistas.admin_usuarios import VistaAdminUsuarioForm, VistaAdminUsuarios
from UI.vistas.cliente import (VistaClienteCategorias, VistaClienteDatos, VistaClientePedidos,
                               VistaClienteProductos)
from UI.vistas.login import VistaLogin


class App:
    RUTAS = {
        "login": VistaLogin,
        "admin_inicio": VistaAdminInicio,
        "admin_categorias": VistaAdminCategorias,
        "admin_productos": VistaAdminProductos,
        "admin_producto_form": VistaAdminProductoForm,
        "admin_usuarios": VistaAdminUsuarios,
        "admin_usuario_form": VistaAdminUsuarioForm,
        "admin_pedidos": VistaAdminPedidos,
        "admin_pedido_form": VistaAdminPedidoForm,
        "cliente_categorias": VistaClienteCategorias,
        "cliente_productos": VistaClienteProductos,
        "cliente_pedidos": VistaClientePedidos,
        "cliente_datos": VistaClienteDatos,
    }

    def __init__(self, page: ft.Page):
        self.page = page
        self.servicio = ServicioDemo()
        self.usuario = None
        page.title = "Food Store"
        page.window.width, page.window.height = 1440, 900
        page.window.min_width, page.window.min_height = 1100, 700
        aplicar_tema(page)
        self.ir("login")

    def ir(self, ruta: str, **kwargs):
        """Cambia de pantalla. kwargs se pasan a la vista (ej. aviso=..., producto=...)."""
        if ruta != "login" and self.usuario is None:
            ruta = "login"
        vista = self.RUTAS[ruta](self, **kwargs)
        self.page.controls.clear()
        self.page.add(ft.Container(vista.construir(), expand=True))
        self.page.update()

    def iniciar_sesion(self, usuario):
        self.usuario = usuario
        self.ir("admin_inicio" if usuario.rol == Rol.ADMIN else "cliente_categorias")

    def cerrar_sesion(self):
        self.usuario = None
        self.ir("login")


if __name__ == "__main__":
    ft.run(lambda page: App(page), assets_dir=str(RAIZ / "assets"))
