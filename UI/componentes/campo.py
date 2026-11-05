"""Campos con etiqueta arriba y mensaje de error abajo, como en el diseño."""
import flet as ft

from UI.tema import Tema, estilo_texto, txt

_PADDING = ft.Padding.symmetric(horizontal=18, vertical=18)


def _etiqueta(texto):
    return txt(texto, 14, 600, Tema.TEXTO_SUAVE) if texto else None


class Campo:
    def __init__(self, etiqueta=None, valor="", password=False, bloqueado=False,
                 multilinea=False, ayuda=None, hint=None, on_change=None,
                 expand=False, width=None):
        self.bloqueado = bloqueado
        self.input = ft.TextField(
            value=str(valor),
            password=password,
            can_reveal_password=password,
            read_only=bloqueado,
            multiline=multilinea,
            min_lines=3 if multilinea else None,
            max_lines=3 if multilinea else 1,
            hint_text=hint,
            hint_style=estilo_texto(15, color=Tema.DESHABILITADO),
            on_change=on_change,
            text_style=estilo_texto(15, color=Tema.TEXTO_SUAVE if bloqueado else Tema.TEXTO),
            filled=True,
            border_radius=12,
            content_padding=_PADDING,
            cursor_color=Tema.PRIMARIO,
        )
        self.error_txt = txt("", 13, color=Tema.ERROR, visible=False)
        self.ayuda_txt = txt(ayuda or "", 13, color=Tema.TEXTO_SUAVE, visible=bool(ayuda))
        hijos = [c for c in (_etiqueta(etiqueta), self.input, self.error_txt, self.ayuda_txt) if c]
        self.control = ft.Column(hijos, spacing=8, expand=expand, width=width)
        self._pintar(False)

    def _pintar(self, con_error):
        borde = Tema.ERROR if con_error else Tema.BORDE
        self.input.border_color = borde
        self.input.focused_border_color = Tema.ERROR if con_error else Tema.PRIMARIO
        self.input.border_width = 1.5 if con_error else 1
        self.input.focused_border_width = 1.5
        self.input.fill_color = Tema.GRIS if self.bloqueado else Tema.BLANCO

    @property
    def valor(self) -> str:
        return self.input.value or ""

    @valor.setter
    def valor(self, v):
        self.input.value = str(v)

    def error(self, mensaje: str | None):
        """Marca el campo en rojo con el mensaje; None lo limpia."""
        self._pintar(bool(mensaje))
        self.error_txt.value = mensaje or ""
        self.error_txt.visible = bool(mensaje)
        self.ayuda_txt.visible = not mensaje and bool(self.ayuda_txt.value)


class Selector:
    """Dropdown con el mismo look que Campo. opciones: lista de (clave, texto)."""

    def __init__(self, etiqueta=None, opciones=(), valor=None, on_change=None,
                 expand=False, width=None, hint=None):
        self._on_change = on_change
        self.input = ft.Dropdown(
            value=valor,
            options=[ft.DropdownOption(key=str(k), text=t) for k, t in opciones],
            on_select=self._cambio,
            hint_text=hint,
            text_style=estilo_texto(15),
            filled=True,
            fill_color=Tema.BLANCO,
            bgcolor=Tema.BLANCO,
            border_radius=12,
            border_color=Tema.BORDE,
            focused_border_color=Tema.PRIMARIO,
            content_padding=_PADDING,
            expand=True,
        )
        self.error_txt = txt("", 13, color=Tema.ERROR, visible=False)
        hijos = [c for c in (_etiqueta(etiqueta), ft.Row([self.input]), self.error_txt) if c]
        self.control = ft.Column(hijos, spacing=8, expand=expand, width=width)

    def _cambio(self, e):
        if self._on_change:
            self._on_change(self.valor)

    @property
    def valor(self) -> str | None:
        return self.input.value

    def error(self, mensaje: str | None):
        self.input.border_color = Tema.ERROR if mensaje else Tema.BORDE
        self.error_txt.value = mensaje or ""
        self.error_txt.visible = bool(mensaje)


class Opciones:
    """Selector segmentado (Opción A / B / C, rol, forma de pago, estado)."""

    def __init__(self, opciones, valor=None, on_change=None, deshabilitadas=(), alto=56):
        self.opciones = list(opciones)        # [(clave, texto)]
        self.valor = valor
        self.on_change = on_change
        self.deshabilitadas = set(deshabilitadas)
        self.con_error = False
        self.alto = alto
        self.control = ft.Row(spacing=14)
        self._render()

    def _click(self, e):
        clave = e.control.data
        if clave in self.deshabilitadas:
            return
        self.valor = clave
        self._render()
        if self.on_change:
            self.on_change(clave)
        e.control.page.update()

    def _render(self):
        items = []
        for clave, texto in self.opciones:
            seleccionado = clave == self.valor
            bloqueado = clave in self.deshabilitadas
            if bloqueado:
                fondo, borde, color, peso = Tema.GRIS, Tema.GRIS, Tema.DESHABILITADO, 500
            elif seleccionado and self.con_error:
                fondo, borde, color, peso = Tema.ERROR_BG, Tema.ERROR, Tema.ERROR, 700
            elif seleccionado:
                fondo, borde, color, peso = Tema.PRIMARIO_SUAVE, Tema.PRIMARIO, Tema.PRIMARIO, 700
            else:
                fondo, borde, color, peso = Tema.BLANCO, Tema.BORDE, Tema.TEXTO, 500
            items.append(ft.Container(
                content=txt(texto, 15, peso, color),
                alignment=ft.Alignment.CENTER,
                height=self.alto,
                expand=True,
                bgcolor=fondo,
                border=ft.Border.all(1.5 if seleccionado else 1, borde),
                border_radius=12,
                data=clave,
                on_click=None if bloqueado else self._click,
            ))
        self.control.controls = items

    def refrescar(self):
        self._render()
