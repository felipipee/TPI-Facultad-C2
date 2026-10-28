"""
Ejemplos de componentes y vistas para Food Store con Flet.
Verificado construyendo los controles con Flet 1.0.5.
En Flet 0.2x algunos nombres cambian (ver notas al final).

Ejecutar:  python ejemplos_flet.py
"""
from abc import ABC, abstractmethod
import flet as ft


# ---------------------------------------------------------------- 1. TOKENS
class Tema:
    PRIMARIO = "#E4572E"
    PRIMARIO_SUAVE = "#FFD8C7"
    BG = "#FBF7F1"
    BORDE = "#E9E2D6"
    TEXTO = "#1F1A17"
    MUTED = "#7A7068"
    DARK = "#2B211C"
    OK, OK_BG = "#15803D", "#DCFCE7"
    WARN, WARN_BG = "#B45309", "#FFEEAB"
    ERROR, ERROR_BG = "#B91C1C", "#FEE2E2"
    INFO, INFO_BG = "#1D4ED8", "#DBEAFE"
    GRIS = "#EFEAE2"


# ------------------------------------------------------------- 2. BOTONES
def _estilo(color_fondo, color_texto, borde=None):
    return ft.ButtonStyle(
        bgcolor=color_fondo,
        color=color_texto,
        side=borde,
        shape=ft.RoundedRectangleBorder(radius=10),
        padding=ft.Padding.symmetric(horizontal=18, vertical=14),
    )


def boton(texto, on_click=None, tipo="primario", deshabilitado=False):
    estilos = {
        "primario": _estilo(Tema.PRIMARIO, "#FFFFFF"),
        "secundario": _estilo("#FFFFFF", Tema.TEXTO, ft.BorderSide(1, Tema.BORDE)),
        "peligro": _estilo(Tema.ERROR_BG, Tema.ERROR),
    }
    return ft.Button(texto, on_click=on_click, style=estilos[tipo], disabled=deshabilitado)


# --------------------------------------------------------------- 3. BADGES
def badge(texto, fondo, color):
    return ft.Container(
        content=ft.Text(texto, size=11, weight=ft.FontWeight.W_700, color=color),
        bgcolor=fondo,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        border_radius=999,
    )


TONOS_ESTADO = {
    "PENDIENTE": (Tema.WARN_BG, Tema.WARN),
    "CONFIRMADO": (Tema.INFO_BG, Tema.INFO),
    "TERMINADO": (Tema.OK_BG, Tema.OK),
    "CANCELADO": (Tema.ERROR_BG, Tema.ERROR),
}


def tag_estado(nombre_estado: str):
    fondo, color = TONOS_ESTADO[nombre_estado]
    return badge(nombre_estado, fondo, color)


# ------------------------------------------------------- 4. CAMPOS / ERRORES
def campo(etiqueta, valor="", error=None, password=False, expand=False):
    return ft.TextField(
        label=etiqueta,
        value=valor,
        error=error,                   # 1.0.x: error (0.2x: error_text). None => sin error
        password=password,
        can_reveal_password=password,
        border_radius=10,
        border_color=Tema.BORDE,
        focused_border_color=Tema.PRIMARIO,
        expand=expand,
    )


def selector(etiqueta, opciones: list[str], valor=None, on_select=None):
    return ft.Dropdown(
        label=etiqueta,
        value=valor,
        options=[ft.DropdownOption(key=o, text=o) for o in opciones],
        on_select=on_select,           # 0.2x: on_change
        border_radius=10,
    )


# ----------------------------------------------------------------- 5. ALERTA
def alerta(tipo, titulo, detalle):
    fondo, color = {
        "ok": (Tema.OK_BG, Tema.OK),
        "warn": (Tema.WARN_BG, Tema.WARN),
        "error": (Tema.ERROR_BG, Tema.ERROR),
        "info": (Tema.INFO_BG, Tema.INFO),
    }[tipo]
    return ft.Container(
        bgcolor=fondo,
        border_radius=12,
        padding=14,
        content=ft.Column(
            spacing=2,
            controls=[
                ft.Text(titulo, weight=ft.FontWeight.W_700, color=color),
                ft.Text(detalle, size=12, color=color),
            ],
        ),
    )


# ------------------------------------------------------------------ 6. TABLA
def tabla(columnas: list[str], filas: list[list]):
    """filas: lista de listas con str o controles (botones, badges)."""
    def celda(x):
        return ft.DataCell(ft.Text(x) if isinstance(x, str) else x)

    return ft.DataTable(
        columns=[ft.DataColumn(ft.Text(c, weight=ft.FontWeight.W_700, size=12)) for c in columnas],
        rows=[ft.DataRow(cells=[celda(x) for x in fila]) for fila in filas],
        heading_row_color=Tema.GRIS,
        border=ft.Border.all(1, Tema.BORDE),
        border_radius=12,
    )


# ------------------------------------------------------------------ 7. MODAL
def abrir_modal(page: ft.Page, titulo, contenido: ft.Control, on_guardar):
    def cerrar(e=None):
        page.pop_dialog()              # 0.2x: dlg.open = False; page.update()

    def guardar(e):
        on_guardar()
        cerrar()

    page.show_dialog(                  # 0.2x: page.open(dlg)
        ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo),
            content=contenido,
            actions=[boton("Cancelar", cerrar, "secundario"), boton("Guardar", guardar)],
        )
    )


# --------------------------------------------------------- 8. VISTAS (POO)
class Vista(ABC):
    """Clase base: cada pantalla sabe construirse. Recibe la page y el contexto."""

    def __init__(self, page: ft.Page, app):
        self.page = page
        self.app = app

    @abstractmethod
    def construir(self) -> ft.Control: ...


class VistaLogin(Vista):
    MAX_INTENTOS = 3

    def __init__(self, page, app):
        super().__init__(page, app)
        self.intentos = 0
        self.mail = campo("Mail")
        self.clave = campo("Contraseña", password=True)
        self.aviso = ft.Container()    # acá se muestra la alerta de error

    def _ingresar(self, e):
        try:
            # Aquí llamarías a tu capa de servicios:
            # usuario = self.app.servicio_usuarios.autenticar(self.mail.value, self.clave.value)
            if (self.mail.value, self.clave.value) != ("admin@foodstore.com", "1234"):
                raise ValueError("credenciales")
            self.app.ir_a(VistaAdmin)
        except ValueError:             # en tu TP: except FoodStoreError / AutenticacionError
            self.intentos += 1
            if self.intentos >= self.MAX_INTENTOS:
                self.app.ir_a(VistaBloqueado)
                return
            self.aviso.content = alerta(
                "error",
                "Mail o contraseña incorrectos",
                f"Intento {self.intentos} de {self.MAX_INTENTOS}. No indicamos cuál dato falló.",
            )
            self.page.update()

    def construir(self):
        return ft.Container(
            width=420,
            padding=32,
            bgcolor="#FFFFFF",
            border_radius=16,
            border=ft.Border.all(1, Tema.BORDE),
            content=ft.Column(
                tight=True,
                spacing=16,
                controls=[
                    ft.Text("Iniciar sesión", size=28, weight=ft.FontWeight.W_800),
                    self.aviso,
                    self.mail,
                    self.clave,
                    boton("Ingresar", self._ingresar),
                ],
            ),
        )


class VistaBloqueado(Vista):
    def construir(self):
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Se agotaron los intentos", size=28, weight=ft.FontWeight.W_800),
                ft.Text("Por seguridad el programa se cierra.", color=Tema.MUTED),
                boton("Salir", lambda e: self.page.window.close(), "secundario"),
            ],
        )


class VistaAdmin(Vista):
    """Layout con barra lateral + área de contenido que cambia."""

    SECCIONES = ["Inicio", "Categorías", "Pedidos"]

    def __init__(self, page, app):
        super().__init__(page, app)
        self.contenido = ft.Container(expand=True, padding=24)

    def _seccion(self, nombre):
        if nombre == "Categorías":
            return self._categorias()
        if nombre == "Pedidos":
            return self._pedidos()
        return ft.Text("Hola, Ana", size=28, weight=ft.FontWeight.W_800)

    def _categorias(self):
        def nueva(e):
            nombre = campo("Nombre", error="Ya existe una categoría con ese nombre")
            abrir_modal(self.page, "Crear categoría", nombre, lambda: None)

        return ft.Column(
            controls=[
                ft.Row([ft.Text("Categorías", size=28, weight=ft.FontWeight.W_800),
                        boton("+ Crear categoría", nueva)],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                tabla(["ID", "Nombre", "Acciones"],
                      [["1", "Hamburguesas", ft.Row([boton("Editar", tipo="secundario"),
                                                     boton("Eliminar", tipo="peligro")])],
                       ["2", "Pizzas", ft.Row([boton("Editar", tipo="secundario"),
                                               boton("Eliminar", tipo="peligro")])]]),
            ]
        )

    def _pedidos(self):
        return ft.Column(
            controls=[
                ft.Text("Pedidos", size=28, weight=ft.FontWeight.W_800),
                tabla(["#", "Estado", "Total"],
                      [["1", tag_estado("PENDIENTE"), "$21.800"],
                       ["2", tag_estado("TERMINADO"), "$9.800"]]),
            ]
        )

    def _cambiar(self, e):
        self.contenido.content = self._seccion(self.SECCIONES[e.control.selected_index])
        self.page.update()

    def construir(self):
        self.contenido.content = self._seccion("Inicio")
        riel = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[ft.NavigationRailDestination(icon=ft.Icons.HOME, label="Inicio"),
                          ft.NavigationRailDestination(icon=ft.Icons.CATEGORY, label="Categorías"),
                          ft.NavigationRailDestination(icon=ft.Icons.RECEIPT_LONG, label="Pedidos")],
            on_change=self._cambiar,
        )
        return ft.Row(controls=[riel, ft.VerticalDivider(width=1), self.contenido], expand=True)


# ---------------------------------------------------- 9. APP / NAVEGACIÓN
class App:
    def __init__(self, page: ft.Page):
        self.page = page
        page.title = "Food Store"
        page.bgcolor = Tema.BG
        page.theme = ft.Theme(color_scheme_seed=Tema.PRIMARIO)
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.ir_a(VistaLogin)

    def ir_a(self, clase_vista):
        vista = clase_vista(self.page, self)
        self.page.clean()
        self.page.add(vista.construir())
        self.page.update()


def main(page: ft.Page):
    App(page)


if __name__ == "__main__":
    ft.run(main)                       # 0.2x: ft.app(target=main)