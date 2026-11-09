"""Pantallas 12, 13 y 14: listado de pedidos, nuevo pedido (stock insuficiente) y cambio de estado."""
from datetime import date

import flet as ft

from UI.componentes.alerta import alerta
from UI.componentes.badge import badge_estado, envolver
from UI.componentes.boton import boton
from UI.componentes.campo import Campo, Opciones, Selector
from UI.componentes.marca import encabezado, nota, tarjeta
from UI.componentes.modal import (abrir_modal, cerrar_modal, modal_confirmar, pie_modal,
                                  titulo_modal)
from UI.componentes.pedido import fila_total, tabla_detalles
from UI.componentes.tabla import acciones, tabla
from UI.datos_demo import TRANSICIONES_VALIDAS, Estado, FoodStoreError, FormaPago
from UI.tema import Tema, pesos, txt
from UI.vistas.vista_abc import VistaAdmin

TODOS = "todos"
PASOS = [Estado.PENDIENTE, Estado.CONFIRMADO, Estado.TERMINADO]


def _fecha(d: date) -> str:
    return d.strftime("%d/%m/%Y")


# ------------------------------------------------------------ stepper
def _paso(numero, estado: Estado, actual: Estado):
    i, j = PASOS.index(estado), PASOS.index(actual) if actual in PASOS else -1
    if i < j or (actual == Estado.TERMINADO and i == j):
        circulo = ft.Container(ft.Icon(ft.Icons.CHECK, size=20, color=Tema.BLANCO), bgcolor=Tema.EXITO)
        color = Tema.EXITO
    elif i == j:
        circulo = ft.Container(txt(numero, 17, 700, Tema.INFO), bgcolor=Tema.INFO_BG,
                               border=ft.Border.all(2.5, Tema.INFO))
        color = Tema.INFO
    else:
        circulo = ft.Container(txt(numero, 17, 700, Tema.DESHABILITADO), bgcolor=Tema.GRIS)
        color = Tema.DESHABILITADO
    circulo.width = circulo.height = 46
    circulo.border_radius = 23
    circulo.alignment = ft.Alignment.CENTER
    return ft.Column([circulo, txt(estado.value, 15, 700, color)], width=150, spacing=12,
                     horizontal_alignment=ft.CrossAxisAlignment.CENTER)


def stepper(actual: Estado) -> ft.Row:
    j = PASOS.index(actual) if actual in PASOS else -1

    def linea(despues_de):
        return ft.Container(height=4, expand=True, margin=ft.Margin.only(top=21),
                            bgcolor=Tema.EXITO if despues_de < j else Tema.BORDE)

    return ft.Row(
        [_paso(1, PASOS[0], actual), linea(0), _paso(2, PASOS[1], actual), linea(1), _paso(3, PASOS[2], actual)],
        spacing=0, vertical_alignment=ft.CrossAxisAlignment.START,
    )


# ============================================================== LISTADO
class VistaAdminPedidos(VistaAdmin):
    ruta = "admin_pedidos"

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.filtro_usuario = TODOS
        self.filtro_estado = TODOS

    def _nombre(self, usuario_id):
        u = self.servicio.usuario(usuario_id)
        return u.nombre_completo if u else f"Usuario #{usuario_id} (baja)"

    # ---------------------------------------------------------- modales
    def _ver(self, p):
        abrir_modal(self.page, ft.Column(tight=True, spacing=24, controls=[
            ft.Row([titulo_modal(f"Pedido #{p.id}", f"{self._nombre(p.usuario_id)} · {p.forma_pago.value} · {_fecha(p.fecha)}"),
                    badge_estado(p.estado)],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START),
            tabla_detalles(p),
            fila_total(p.total, 34),
            pie_modal(boton("Cerrar", lambda e: cerrar_modal(self.page), "secundario")),
        ]), ancho=780)

    def _cambiar_estado(self, p):
        zona_error = ft.Container()
        zona_guardar = ft.Container(boton("Guardar cambios", deshabilitado=True))
        elegido = {"estado": None}

        def guardar(e):
            try:
                self.servicio.cambiar_estado(p.id, elegido["estado"])
            except FoodStoreError as err:
                zona_error.content = alerta("error", err.titulo, err.mensaje)
                self.page.update()
                return
            cerrar_modal(self.page)
            extra = " Se devolvió el stock." if elegido["estado"] == Estado.CANCELADO else ""
            self.refrescar(("ok", "Operación exitosa",
                            f"El pedido #{p.id} pasó a {elegido['estado'].value}.{extra}"))

        def al_elegir(valor):
            nuevo = Estado(valor)
            elegido["estado"] = nuevo
            valido = nuevo in TRANSICIONES_VALIDAS[p.estado]
            opciones.con_error = not valido
            opciones.refrescar()
            zona_error.content = None if valido else alerta(
                "error", "Transición no permitida",
                f"{p.estado.value} → {nuevo.value} no es válido. El pedido no se modificó.")
            zona_guardar.content = boton("Guardar cambios", guardar, deshabilitado=not valido)

        opciones = Opciones([(e.value, e.value) for e in Estado], on_change=al_elegir,
                            deshabilitadas={p.estado.value})

        abrir_modal(self.page, ft.Column(tight=True, spacing=26, controls=[
            titulo_modal(f"Cambiar estado · Pedido #{p.id}",
                         f"{self._nombre(p.usuario_id)} · {p.forma_pago.value} · {pesos(p.total)}"),
            ft.Container(stepper(p.estado), padding=ft.Padding.symmetric(horizontal=40)),
            ft.Column([txt("Nuevo estado", 15, 600, Tema.TEXTO_SUAVE), opciones.control], spacing=10),
            zona_error,
            txt("Válidas: PENDIENTE → CONFIRMADO → TERMINADO. PENDIENTE o CONFIRMADO → "
                "CANCELADO (devuelve el stock).", 15, color=Tema.TEXTO_SUAVE),
            pie_modal(boton("Cancelar", lambda e: cerrar_modal(self.page), "secundario"), zona_guardar),
        ]), ancho=900)

    def _eliminar(self, p):
        def ok():
            self.servicio.eliminar_pedido(p.id)
            extra = "" if p.cerrado else " Se devolvió el stock."
            self.refrescar(("ok", "Operación exitosa", f"Se eliminó el pedido #{p.id}.{extra}"))

        detalle = ("Es una baja lógica." if p.cerrado
                   else "Es una baja lógica y el stock de sus productos se devuelve.")
        modal_confirmar(self.page, f"Eliminar pedido #{p.id}", detalle, "Eliminar", ok)

    # --------------------------------------------------------- filtros
    def _al_filtrar_usuario(self, v):
        self.filtro_usuario = v
        self.refrescar(self.aviso)

    def _al_filtrar_estado(self, v):
        self.filtro_estado = v
        self.refrescar(self.aviso)

    def contenido(self):
        uid = None if self.filtro_usuario == TODOS else int(self.filtro_usuario)
        est = None if self.filtro_estado == TODOS else Estado(self.filtro_estado)
        pedidos = self.servicio.pedidos(uid, est)

        filas = [
            [
                str(p.id),
                txt(self._nombre(p.usuario_id), 16, 600),
                envolver(badge_estado(p.estado)),
                txt(p.forma_pago.value, 16, color=Tema.TEXTO_SUAVE),
                txt(pesos(p.total), 16, 700),
                txt(_fecha(p.fecha), 16, color=Tema.TEXTO_SUAVE),
                acciones(
                    boton("Ver", lambda e, p=p: self._ver(p), "secundario", chico=True),
                    boton("Estado", lambda e, p=p: self._cambiar_estado(p), "secundario", chico=True,
                          deshabilitado=p.cerrado),
                    boton("Eliminar", lambda e, p=p: self._eliminar(p), "peligro", chico=True),
                ),
            ]
            for p in pedidos
        ]

        f_usuario = Selector(opciones=[(TODOS, "Todos los usuarios")] +
                             [(u.id, u.nombre_completo) for u in self.servicio.usuarios()],
                             valor=self.filtro_usuario, on_change=self._al_filtrar_usuario, width=380)
        f_estado = Selector(opciones=[(TODOS, "Todos los estados")] + [(e.value, e.value) for e in Estado],
                            valor=self.filtro_estado, on_change=self._al_filtrar_estado, width=340)

        return self.sin_nulos(
            encabezado("Pedidos", "Seguimiento de estados, formas de pago y detalles",
                       boton("+ Nuevo pedido", lambda e: self.app.ir("admin_pedido_form"))),
            self.control_aviso(),
            ft.Row([f_usuario.control, f_estado.control, ft.Container(expand=True),
                    txt(f"{len(pedidos)} pedido{'s' if len(pedidos) != 1 else ''}", 17, color=Tema.TEXTO_SUAVE)],
                   spacing=20),
            tabla([("ID", 1), ("Usuario", 4), ("Estado", 3), ("Pago", 3), ("Total", 3), ("Fecha", 3),
                   ("Acciones", 6)], filas),
            nota("TERMINADO y CANCELADO no cambian más. Eliminar es una baja lógica y devuelve el stock "
                 "si el pedido no estaba cerrado."),
        )


# ========================================================= NUEVO PEDIDO
class VistaAdminPedidoForm(VistaAdmin):
    ruta = "admin_pedidos"

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.items: dict[int, int] = {}            # producto_id -> cantidad
        self.error_detalle = None                   # FoodStoreError del último intento
        self.error_general = None
        self.usuario = Selector("Usuario", [(u.id, u.nombre_completo) for u in self.servicio.usuarios()],
                                hint="Elegí un usuario", expand=True,
                                on_change=lambda v: self._redibujar())
        self.fecha = Campo("Fecha", _fecha(date.today()), bloqueado=True, width=260)
        self.pago = Opciones([(f.value, f.value) for f in FormaPago], FormaPago.TARJETA.value,
                             on_change=lambda v: self._redibujar())
        self.producto = Selector("Producto", self._opciones_producto(), hint="Elegí un producto", expand=True)
        self.cantidad = Campo("Cantidad", "1", width=200)
        self.cantidad.input.on_submit = self._agregar

    def _opciones_producto(self):
        return [(p.id, f"{p.nombre} · {pesos(p.precio)}") for p in self.servicio.productos_visibles()]

    def _redibujar(self):
        self.refrescar()

    # ----------------------------------------------------------- acciones
    def _agregar(self, e):
        self.cantidad.error(None)
        self.producto.error(None)
        self.error_general = None
        try:
            pid = int(self.producto.valor) if self.producto.valor else None
            p, cant = self.servicio.validar_detalle(pid, self.cantidad.valor, self.items.get(pid, 0))
        except FoodStoreError as err:
            self.error_detalle = err
            (self.cantidad if err.campo == "cantidad" else self.producto).error("")
            self.refrescar()
            return
        self.error_detalle = None
        self.items[p.id] = self.items.get(p.id, 0) + cant
        self.cantidad.valor = "1"
        self.refrescar()

    def _quitar(self, pid):
        self.items.pop(pid, None)
        self.refrescar()

    def _confirmar(self, e):
        try:
            uid = int(self.usuario.valor) if self.usuario.valor else None
            nuevo = self.servicio.crear_pedido(uid, FormaPago(self.pago.valor), self.items)
        except FoodStoreError as err:
            self.error_general = err
            self.refrescar()
            return
        self.app.ir("admin_pedidos", aviso=("ok", "Operación exitosa", f"Pedido creado con id {nuevo}."))

    # ---------------------------------------------------------- resumen
    def _resumen(self):
        lineas, total = [], 0
        for pid, cant in self.items.items():
            p = self.servicio.producto(pid)
            subtotal = cant * p.precio
            total += subtotal
            lineas.append(ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column([txt(p.nombre, 18, 600), txt(f"{cant} × {pesos(p.precio)}", 15, color=Tema.TEXTO_SUAVE)],
                              spacing=2, expand=True),
                    txt(pesos(subtotal), 18, 700),
                    ft.IconButton(ft.Icons.CLOSE, icon_size=18, icon_color=Tema.TEXTO_SUAVE,
                                  tooltip="Quitar", on_click=lambda e, pid=pid: self._quitar(pid)),
                ],
            ))
        if not lineas:
            lineas.append(txt("Todavía no agregaste detalles.", 15, color=Tema.TEXTO_SUAVE))

        puede = bool(self.items) and bool(self.usuario.valor)
        hijos = [
            ft.Row([txt("Resumen", 24, 700), badge_estado(Estado.PENDIENTE)],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            txt(f"{self.pago.valor} · {_fecha(date.today())}", 16, color=Tema.TEXTO_SUAVE),
            ft.Divider(color=Tema.BORDE, height=1),
            ft.Column(lineas, spacing=18),
            ft.Divider(color=Tema.BORDE, height=1),
            fila_total(total),
        ]
        if self.error_general:
            hijos.append(alerta("error", "No se pudo crear el pedido", self.error_general.mensaje))
        hijos += [
            ft.Row([boton("Confirmar pedido", self._confirmar, expand=True, deshabilitado=not puede)]),
            ft.Row([boton("Cancelar", lambda e: self.app.ir("admin_pedidos"), "secundario", expand=True)]),
            txt("Si algo falla, el pedido no se crea y el stock queda igual.", 14,
                color=Tema.DESHABILITADO, text_align=ft.TextAlign.CENTER),
        ]
        return tarjeta(ft.Column(hijos, spacing=20), padding=36, width=540)

    def contenido(self):
        arriba = ft.CrossAxisAlignment.START
        hijos = [
            txt("Datos del pedido", 22, 700),
            ft.Row([self.usuario.control, self.fecha.control], spacing=24, vertical_alignment=arriba),
            ft.Column([txt("Forma de pago", 14, 600, Tema.TEXTO_SUAVE), self.pago.control], spacing=10),
            ft.Divider(color=Tema.BORDE, height=1),
            txt("Agregar detalle", 22, 700),
            ft.Row([self.producto.control, self.cantidad.control], spacing=24, vertical_alignment=arriba),
        ]
        if self.error_detalle:
            hijos.append(alerta("error", self.error_detalle.titulo or "Detalle inválido", self.error_detalle.mensaje))
        hijos.append(ft.Row([boton("+ Agregar detalle", self._agregar, "secundario")],
                            alignment=ft.MainAxisAlignment.END))

        volver = boton("Volver al listado", lambda e: self.app.ir("admin_pedidos"), "secundario",
                       icono=ft.Icons.ARROW_BACK)
        return [
            encabezado("Nuevo pedido", "Agregá uno o más detalles; el precio se toma del producto", volver),
            ft.Row([tarjeta(ft.Column(hijos, spacing=24, horizontal_alignment=ft.CrossAxisAlignment.STRETCH), padding=44, expand=True), self._resumen()],
                   spacing=36, vertical_alignment=arriba),
        ]
