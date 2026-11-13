"""Pantallas 15 a 18: menú de cliente (solo consulta)."""
import flet as ft

from UI.componentes.alerta import alerta
from UI.componentes.badge import badge, badge_estado, envolver
from UI.componentes.marca import avatar, encabezado, imagen_producto, nota, tarjeta
from UI.componentes.campo import Campo
from UI.componentes.pedido import dato, fila_total, tabla_detalles
from UI.componentes.tabla import tabla
from UI.tema import Tema, pesos, txt
from UI.vistas.vista_abc import VistaCliente


def _grilla(tarjetas, por_fila=3):
    """Filas de N tarjetas del mismo ancho (rellena con huecos la última fila)."""
    filas = []
    for i in range(0, len(tarjetas), por_fila):
        grupo = tarjetas[i:i + por_fila]
        grupo += [ft.Container(expand=True) for _ in range(por_fila - len(grupo))]
        filas.append(ft.Row(grupo, spacing=36, vertical_alignment=ft.CrossAxisAlignment.START))
    return ft.Column(filas, spacing=36)


def _plural(n, uno, varios):
    return f"{n} {uno if n == 1 else varios}"


# ----------------------------------------------------------- categorías
class VistaClienteCategorias(VistaCliente):
    ruta = "cliente_categorias"

    def _tarjeta(self, c):
        cantidad = self.servicio.cantidad_productos(c.id)
        return ft.Container(
            expand=True, bgcolor=Tema.BLANCO, border=ft.Border.all(1, Tema.BORDE), border_radius=22,
            padding=40, ink=True,
            on_click=lambda e: self.app.ir("cliente_productos", categoria_id=c.id),
            content=ft.Column(spacing=14, controls=[
                ft.Container(txt(c.nombre[:1].upper(), 34, 800, Tema.PRIMARIO), width=84, height=84,
                             border_radius=18, bgcolor=Tema.PRIMARIO_SUAVE, alignment=ft.Alignment.CENTER),
                ft.Container(height=4),
                txt(c.nombre, 28, 700),
                txt(c.descripcion, 17, color=Tema.TEXTO_SUAVE),
                ft.Row([badge(_plural(cantidad, "producto", "productos"), tam=15)]),
            ]),
        )

    def contenido(self):
        return [
            encabezado("Categorías", "Explorá el catálogo por categoría"),
            _grilla([self._tarjeta(c) for c in self.servicio.categorias()]),
            nota("Menú de cliente: solo consulta, no hay opciones que modifiquen datos."),
        ]


# ------------------------------------------------------------ productos
class VistaClienteProductos(VistaCliente):
    ruta = "cliente_productos"

    def __init__(self, app, categoria_id=None, **kwargs):
        super().__init__(app, **kwargs)
        self.categoria_id = categoria_id

    def _chip(self, texto, cat_id):
        activo = cat_id == self.categoria_id

        def elegir(e):
            self.categoria_id = cat_id
            self.refrescar()

        return ft.Container(
            content=txt(texto, 17, 600, Tema.BLANCO if activo else Tema.TEXTO_SUAVE),
            bgcolor=Tema.PRIMARIO if activo else Tema.BLANCO,
            border=None if activo else ft.Border.all(1, Tema.BORDE),
            border_radius=999, padding=ft.Padding.symmetric(horizontal=26, vertical=12),
            on_click=elegir, ink=True,
        )

    def _tarjeta(self, p, nombre_cat):
        return ft.Container(
            expand=True, bgcolor=Tema.BLANCO, border=ft.Border.all(1, Tema.BORDE), border_radius=22,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Column(spacing=0, controls=[
                imagen_producto(nombre_cat, alto=200),
                ft.Container(padding=ft.Padding.symmetric(horizontal=30, vertical=26), content=ft.Column(spacing=10, controls=[
                    ft.Row([badge(nombre_cat), txt(f"Stock: {p.stock}", 15, color=Tema.TEXTO_SUAVE)],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    txt(p.nombre, 26, 700),
                    txt(p.descripcion, 17, color=Tema.TEXTO_SUAVE),
                    ft.Row([txt(pesos(p.precio), 32, 800, Tema.PRIMARIO),
                            badge("Disponible", Tema.EXITO_BG, Tema.EXITO)],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ])),
            ]),
        )

    def contenido(self):
        visibles = self.servicio.productos_visibles()
        nombre_cat = {c.id: c.nombre for c in self.servicio.categorias()}
        cats_con_productos = [c for c in self.servicio.categorias()
                              if any(p.categoria_id == c.id for p in visibles)]
        if self.categoria_id not in {c.id for c in cats_con_productos}:
            mostrar = visibles if self.categoria_id is None else []
        else:
            mostrar = [p for p in visibles if p.categoria_id == self.categoria_id]

        chips = [self._chip("Todas", None)] + [self._chip(c.nombre, c.id) for c in cats_con_productos]
        cuerpo = (_grilla([self._tarjeta(p, nombre_cat.get(p.categoria_id, "")) for p in mostrar]) if mostrar
                  else alerta("info", "No hay productos para mostrar",
                              "Esta categoría no tiene productos disponibles con stock en este momento."))
        return [
            encabezado("Productos disponibles", "Solo mostramos productos disponibles y con stock"),
            ft.Row([ft.Row(chips, spacing=14), ft.Container(expand=True),
                    txt(_plural(len(mostrar), "producto", "productos"), 17, color=Tema.TEXTO_SUAVE)]),
            cuerpo,
        ]


# ---------------------------------------------------------- mis pedidos
class VistaClientePedidos(VistaCliente):
    ruta = "cliente_pedidos"

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        mios = self.servicio.pedidos(self.app.usuario.id)
        self.seleccionado = mios[0].id if mios else None

    def _elegir(self, pedido_id):
        self.seleccionado = pedido_id
        self.refrescar()

    def _detalle(self, p):
        if not p:
            return tarjeta(txt("Elegí un pedido para ver su detalle.", 17, color=Tema.TEXTO_SUAVE), expand=True)
        return tarjeta(ft.Column(spacing=26, controls=[
            ft.Row([txt(f"Pedido #{p.id}", 32, 800), badge_estado(p.estado)],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([dato("Fecha", p.fecha.strftime("%d/%m/%Y")), dato("Forma de pago", p.forma_pago.value)], spacing=40),
            tabla_detalles(p),
            fila_total(p.total),
        ]), padding=32, expand=9)

    def contenido(self):
        mios = self.servicio.pedidos(self.app.usuario.id)
        filas = [[str(p.id), envolver(badge_estado(p.estado)), txt(p.forma_pago.value, 16, color=Tema.TEXTO_SUAVE),
                  txt(pesos(p.total), 16, 700), txt(p.fecha.strftime("%d/%m/%Y"), 16, color=Tema.TEXTO_SUAVE)]
                 for p in mios]
        izquierda = ft.Column(expand=10, spacing=24, controls=[
            tabla([("#", 1), ("Estado", 3), ("Pago", 3), ("Total", 2), ("Fecha", 3)], filas,
                  on_click_fila=self._elegir, seleccionada=self.seleccionado, datos_filas=[p.id for p in mios]),
            nota("Elegí un pedido para ver su detalle. Si el id es de otro usuario, se informa como inexistente."),
        ])
        return [
            encabezado("Mis pedidos", "Solo ves tus propios pedidos y sus detalles"),
            ft.Row([izquierda, self._detalle(self.servicio.pedido(self.seleccionado) if self.seleccionado else None)],
                   spacing=36, vertical_alignment=ft.CrossAxisAlignment.START),
        ]


# ------------------------------------------------------------ mis datos
class VistaClienteDatos(VistaCliente):
    ruta = "cliente_datos"

    def contenido(self):
        u = self.app.usuario
        arriba = ft.CrossAxisAlignment.START
        ficha = tarjeta(ft.Column(spacing=26, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[
            ft.Row([avatar(u.iniciales, 112),
                    ft.Column([txt(u.nombre_completo, 36, 700), ft.Row([badge(u.rol.value, tam=15)])], spacing=8)],
                   spacing=26),
            ft.Divider(color=Tema.BORDE, height=1),
            ft.Row([Campo("Nombre", u.nombre, bloqueado=True, expand=True).control,
                    Campo("Apellido", u.apellido, bloqueado=True, expand=True).control], spacing=24),
            Campo("Mail", u.mail, bloqueado=True).control,
            ft.Row([Campo("Celular", u.celular, bloqueado=True, expand=True).control,
                    Campo("Rol", u.rol.value, bloqueado=True, expand=True).control], spacing=24),
        ]), padding=44, width=1000)
        lateral = ft.Column(width=480, spacing=22, controls=[
            alerta("info", "Tu contraseña nunca se muestra", "Solo se usa para verificar tu inicio de sesión."),
            alerta("warn", "Solo lectura",
                   "El menú de cliente no permite editar datos. Pedile a un administrador cualquier cambio."),
        ])
        return [
            encabezado("Mis datos", "Revisá que tu información sea correcta"),
            ft.Row([ficha, lateral], spacing=32, vertical_alignment=arriba),
        ]
