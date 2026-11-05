"""Pantallas 01, 02 y 03: login, credenciales incorrectas e intentos agotados."""
import flet as ft

from UI.componentes.alerta import alerta
from UI.componentes.boton import boton
from UI.componentes.campo import Campo
from UI.componentes.marca import logo
from UI.tema import Tema, txt
from UI.vistas.vista_abc import Vista

MAX_INTENTOS = 3


def _circulo(diametro, opacidad, color=Tema.BLANCO, **pos):
    return ft.Container(width=diametro, height=diametro, border_radius=diametro / 2,
                        bgcolor=ft.Colors.with_opacity(opacidad, color), **pos)


def panel_marca() -> ft.Container:
    """Mitad izquierda naranja con logo, círculos decorativos y lema."""
    centro = ft.Container(
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding.only(bottom=120),
        content=ft.Container(
            width=370, height=370, border_radius=185, alignment=ft.Alignment.CENTER,
            bgcolor=ft.Colors.with_opacity(0.13, Tema.BLANCO),
            content=ft.Container(
                width=260, height=260, border_radius=130, alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.with_opacity(0.22, Tema.BLANCO),
                content=_circulo(136, 1, "#FDF7F5"),
            ),
        ),
    )
    return ft.Container(
        expand=True,
        bgcolor=Tema.PRIMARIO,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            fit=ft.StackFit.EXPAND,
            controls=[
                _circulo(560, 0.1, right=-140, top=-300),
                _circulo(560, 0.1, left=-260, bottom=-380),
                centro,
                ft.Container(
                    left=80, top=80,
                    content=ft.Row([logo(54, Tema.BLANCO, Tema.PRIMARIO),
                                    txt("Food Store", 30, 700, Tema.BLANCO)], spacing=16),
                ),
                ft.Container(
                    left=80, right=60, bottom=56,
                    content=ft.Column(spacing=0, controls=[
                        txt("Pedidos de comida,\nbajo control.", 50, 800, Tema.BLANCO),
                        ft.Container(height=24),
                        txt("Categorías, productos, usuarios y pedidos en un solo lugar.", 19,
                            color=ft.Colors.with_opacity(0.92, Tema.BLANCO)),
                        ft.Container(height=60),
                        txt("TPI Programación II · UTN", 14, color=ft.Colors.with_opacity(0.85, Tema.BLANCO)),
                    ]),
                ),
            ],
        ),
    )


def barra_intentos(intentos: int) -> ft.Column:
    if intentos == 0:
        leyenda = txt(f"Tenés {MAX_INTENTOS} intentos", 14, 600, Tema.TEXTO_SUAVE)
    else:
        leyenda = txt(f"Intento {intentos} de {MAX_INTENTOS}", 14, 600, Tema.ERROR)
    segmentos = [
        ft.Container(height=5, expand=True, border_radius=3,
                     bgcolor=Tema.ERROR if i < intentos else Tema.GRIS)
        for i in range(MAX_INTENTOS)
    ]
    return ft.Column(spacing=12, controls=[
        ft.Row([txt("Intentos", 14, 600, Tema.TEXTO_SUAVE), leyenda],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row(segmentos, spacing=8),
    ])


class VistaLogin(Vista):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.intentos = 0
        self.mail = Campo("Mail", hint="tu@mail.com")
        self.clave = Campo("Contraseña", password=True, on_change=None)
        self.mail.input.on_submit = self._ingresar
        self.clave.input.on_submit = self._ingresar
        self.formulario = ft.Container(width=660, padding=ft.Padding.symmetric(horizontal=40))

    # ------------------------------------------------------------ eventos
    def _ingresar(self, e):
        usuario = self.servicio.autenticar(self.mail.valor, self.clave.valor)
        if usuario:
            self.app.iniciar_sesion(usuario)
            return
        self.intentos += 1
        if self.intentos >= MAX_INTENTOS:
            self.formulario.content = self._bloqueado()
        else:
            self.mail.error("")          # borde rojo sin mensaje: no decimos cuál falló
            self.clave.error("")
            self.formulario.content = self._form()
        self.page.update()

    async def _salir(self, e):
        await self.page.window.close()

    # -------------------------------------------------------- contenidos
    def _form(self):
        hijos = [
            txt("Iniciar sesión", 46, 800),
            txt("Ingresá con tu mail y contraseña para ver las opciones de tu rol.", 16, color=Tema.TEXTO_SUAVE),
        ]
        if self.intentos:
            hijos.append(alerta("error", "Mail o contraseña incorrectos",
                                "Por seguridad no indicamos cuál de los dos datos falló."))
        hijos += [
            self.mail.control,
            self.clave.control,
            barra_intentos(self.intentos),
            ft.Row([boton("Ingresar", self._ingresar, expand=True)]),
            ft.Row([txt("Al tercer intento fallido el programa informa y se cierra.", 14,
                        color=Tema.DESHABILITADO)], alignment=ft.MainAxisAlignment.CENTER),
        ]
        return ft.Column(hijos, spacing=24, tight=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    def _bloqueado(self):
        return ft.Column(
            tight=True, spacing=24, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(txt("!", 56, 800, Tema.ERROR), width=112, height=112, border_radius=56,
                             bgcolor=Tema.ERROR_BG, alignment=ft.Alignment.CENTER),
                txt("Se agotaron los intentos", 38, 800, text_align=ft.TextAlign.CENTER),
                txt(f"Fallaste el inicio de sesión {MAX_INTENTOS} veces. Por seguridad el programa "
                    "informa y se cierra.", 18, color=Tema.TEXTO_SUAVE, text_align=ft.TextAlign.CENTER),
                barra_intentos(MAX_INTENTOS),
                ft.Row([boton("Salir", self._salir, "secundario", expand=True)]),
                txt("Podés volver a abrir la aplicación para intentarlo de nuevo.", 14,
                    color=Tema.DESHABILITADO, text_align=ft.TextAlign.CENTER),
            ],
        )

    def construir(self):
        self.formulario.content = self._form()
        return ft.Row(
            spacing=0, expand=True,
            controls=[
                panel_marca(),
                ft.Container(expand=True, bgcolor=Tema.FONDO, alignment=ft.Alignment.CENTER,
                             content=self.formulario),
            ],
        )
