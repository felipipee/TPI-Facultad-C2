"""Pantallas 08 y 09: listado de productos y alta/edición con vista previa."""
import flet as ft

from UI.componentes.alerta import alerta
from UI.componentes.badge import badge, badge_producto, envolver
from UI.componentes.boton import boton
from UI.componentes.campo import Campo, Selector
from UI.componentes.marca import encabezado, etiqueta_seccion, imagen_producto, nota, tarjeta
from UI.componentes.modal import modal_confirmar
from UI.componentes.tabla import acciones, tabla
from UI.datos_demo import ErroresValidacion
from UI.tema import Tema, pesos, txt
from UI.vistas.vista_abc import VistaAdmin

TODAS = "todas"


class VistaAdminProductos(VistaAdmin):
    ruta = "admin_productos"

    def __init__(self, app, categoria_id=None, **kwargs):
        super().__init__(app, **kwargs)
        self.busqueda = ""
        self.categoria = str(categoria_id) if categoria_id else TODAS
        self.zona_tabla = ft.Column(spacing=28)

    def _filtrados(self):
        res = self.servicio.productos()
        if self.categoria != TODAS:
            res = [p for p in res if str(p.categoria_id) == self.categoria]
        if self.busqueda.strip():
            res = [p for p in res if self.busqueda.strip().lower() in p.nombre.lower()]
        return res

    def _al_buscar(self, e):
        self.busqueda = e.control.value or ""
        self._pintar_tabla()
        self.page.update()

    def _al_filtrar(self, valor):
        self.categoria = valor
        self._pintar_tabla()
        self.page.update()

    def _eliminar(self, p):
        def ok():
            self.servicio.eliminar_producto(p.id)
            self.refrescar(("ok", "Operación exitosa", f"Se eliminó el producto \"{p.nombre}\"."))

        modal_confirmar(self.page, f"Eliminar \"{p.nombre}\"",
                        "Baja lógica: el producto deja de aparecer en los listados y para los clientes.",
                        "Eliminar", ok)

    def _pintar_tabla(self):
        prods = self._filtrados()
        nombre_cat = {c.id: c.nombre for c in self.servicio.categorias()}
        filas = [
            [
                str(p.id),
                txt(p.nombre, 16, 600),
                txt(nombre_cat.get(p.categoria_id, "—"), 16, color=Tema.TEXTO_SUAVE),
                pesos(p.precio),
                str(p.stock),
                envolver(badge_producto(p)),
                acciones(
                    boton("Editar", lambda e, p=p: self.app.ir("admin_producto_form", producto=p), "secundario", chico=True),
                    boton("Eliminar", lambda e, p=p: self._eliminar(p), "peligro", chico=True),
                ),
            ]
            for p in prods
        ]
        self.contador.value = f"{len(prods)} producto{'s' if len(prods) != 1 else ''} activo{'s' if len(prods) != 1 else ''}"
        self.zona_tabla.controls = [
            tabla([("ID", 1), ("Producto", 4), ("Categoría", 3), ("Precio", 2), ("Stock", 2),
                   ("Estado", 3), ("Acciones", 3)], filas),
            nota("El cliente solo ve los productos disponibles y con stock mayor a 0. "
                 "Baja lógica: eliminado = True."),
        ]

    def contenido(self):
        buscador = Campo(hint="Buscar por nombre...", valor=self.busqueda, on_change=self._al_buscar, width=460)
        filtro = Selector(
            opciones=[(TODAS, "Todas las categorías")] + [(c.id, c.nombre) for c in self.servicio.categorias()],
            valor=self.categoria, on_change=self._al_filtrar, width=340)
        self.contador = txt("", 17, color=Tema.TEXTO_SUAVE)
        self._pintar_tabla()
        return self.sin_nulos(
            encabezado("Productos", "Administrá precios, stock y disponibilidad",
                       boton("+ Crear producto", lambda e: self.app.ir("admin_producto_form"))),
            self.control_aviso(),
            ft.Row([buscador.control, filtro.control, ft.Container(expand=True), self.contador], spacing=20),
            self.zona_tabla,
        )


class VistaAdminProductoForm(VistaAdmin):
    ruta = "admin_productos"

    def __init__(self, app, producto=None, **kwargs):
        super().__init__(app, **kwargs)
        self.producto = producto
        p = producto
        cats = self.servicio.categorias()
        self.nombre = Campo("Nombre", p.nombre if p else "", on_change=self._previa)
        self.descripcion = Campo("Descripción", p.descripcion if p else "", multilinea=True, on_change=self._previa)
        self.precio = Campo("Precio", f"{p.precio:.0f}" if p else "", on_change=self._previa, expand=True)
        self.stock = Campo("Stock", p.stock if p else "", on_change=self._previa, expand=True)
        self.categoria = Selector("Categoría", [(c.id, c.nombre) for c in cats],
                                  str(p.categoria_id) if p else None, on_change=lambda v: self._previa(),
                                  expand=True, hint="Elegí una categoría")
        self.imagen = Campo("Imagen (ruta o URL)", p.imagen if p else "", expand=True)
        self.disponible = ft.Switch(value=p.disponible if p else True, active_color=Tema.BLANCO,
                                    active_track_color=Tema.EXITO, on_change=self._previa)
        self.vista_previa = ft.Container()

    # -------------------------------------------------------- vista previa
    def _tarjeta_previa(self):
        cat = self.servicio.categoria(int(self.categoria.valor)) if self.categoria.valor else None
        try:
            precio = pesos(float(self.precio.valor.replace(",", ".")))
        except ValueError:
            precio = "$—"
        stock = self.stock.valor.strip() or "—"
        disponible = self.disponible.value
        try:
            sin_stock = int(stock) <= 0
        except ValueError:
            sin_stock = False
        if not disponible:
            estado = badge("No disponible")
        elif sin_stock:
            estado = badge("Sin stock", Tema.ERROR_BG, Tema.ERROR)
        else:
            estado = badge("Disponible", Tema.EXITO_BG, Tema.EXITO)

        return ft.Container(
            bgcolor=Tema.BLANCO, border=ft.Border.all(1, Tema.BORDE), border_radius=20,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Column(spacing=0, controls=[
                imagen_producto(cat.nombre if cat else "", alto=190),
                ft.Container(padding=28, content=ft.Column(spacing=10, controls=[
                    ft.Row([badge(cat.nombre if cat else "Sin categoría"), txt(f"Stock: {stock}", 15, color=Tema.TEXTO_SUAVE)],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    txt(self.nombre.valor or "Nombre del producto", 24, 700),
                    txt(self.descripcion.valor or "Descripción", 16, color=Tema.TEXTO_SUAVE),
                    ft.Row([txt(precio, 30, 800, Tema.PRIMARIO), estado],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ])),
            ]),
        )

    def _previa(self, e=None):
        self.vista_previa.content = self._tarjeta_previa()
        if e is not None:
            self.page.update()

    # ------------------------------------------------------------ guardar
    def _guardar(self, e):
        datos = {
            "nombre": self.nombre.valor, "descripcion": self.descripcion.valor,
            "precio": self.precio.valor, "stock": self.stock.valor,
            "categoria_id": self.categoria.valor, "imagen": self.imagen.valor,
            "disponible": self.disponible.value,
        }
        campos = {"nombre": self.nombre, "descripcion": self.descripcion, "precio": self.precio,
                  "stock": self.stock, "categoria_id": self.categoria, "imagen": self.imagen}
        for c in campos.values():
            c.error(None)
        try:
            if self.producto:
                self.servicio.editar_producto(self.producto.id, datos)
                aviso = ("ok", "Operación exitosa", f"Se actualizó el producto #{self.producto.id}.")
            else:
                nuevo = self.servicio.crear_producto(datos)
                aviso = ("ok", "Operación exitosa", f"Producto creado con id {nuevo}.")
        except ErroresValidacion as err:
            for clave, msg in err.errores.items():
                campos[clave].error(msg)
            self.page.update()
            return
        self.app.ir("admin_productos", aviso=aviso)

    def contenido(self):
        self._previa()
        volver = boton("Volver al listado", lambda e: self.app.ir("admin_productos"), "secundario",
                       icono=ft.Icons.ARROW_BACK)
        formulario = tarjeta(ft.Column(spacing=26, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[
            self.nombre.control,
            self.descripcion.control,
            ft.Row([self.precio.control, self.stock.control], spacing=24,
                   vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Row([self.categoria.control, self.imagen.control], spacing=24,
                   vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Row([
                ft.Column([txt("Disponible", 18, 600),
                           txt("Se muestra a los clientes mientras haya stock", 15, color=Tema.TEXTO_SUAVE)],
                          spacing=2, expand=True),
                self.disponible,
            ]),
            ft.Row([boton("Cancelar", lambda e: self.app.ir("admin_productos"), "secundario"),
                    boton("Guardar producto", self._guardar)],
                   alignment=ft.MainAxisAlignment.END, spacing=14),
        ]), padding=44, expand=True)

        lateral = ft.Column(width=520, spacing=22, controls=[
            etiqueta_seccion("Vista previa · cómo lo ve el cliente"),
            self.vista_previa,
            alerta("info", "Validaciones",
                   "Nombre no vacío · precio ≥ 0 · stock ≥ 0 · categoría existente y no eliminada."),
        ])
        return [
            encabezado("Editar producto" if self.producto else "Nuevo producto",
                       "Todos los campos son obligatorios", volver),
            ft.Row([formulario, lateral], spacing=36, vertical_alignment=ft.CrossAxisAlignment.START),
        ]
