"""Pantallas 05, 06 y 07: listado, crear/editar (nombre repetido) y eliminación bloqueada."""
import flet as ft

from UI.componentes.alerta import alerta
from UI.componentes.boton import boton
from UI.componentes.campo import Campo
from UI.componentes.marca import encabezado, nota
from UI.componentes.modal import abrir_modal, cerrar_modal, modal_confirmar, pie_modal, titulo_modal
from UI.componentes.tabla import acciones, tabla
from UI.datos_demo import ErroresValidacion, FoodStoreError
from UI.tema import Tema, txt
from UI.vistas.vista_abc import VistaAdmin


class VistaAdminCategorias(VistaAdmin):
    ruta = "admin_categorias"

    # ------------------------------------------------------------ modales
    def _abrir_form(self, categoria=None):
        nombre = Campo("Nombre", categoria.nombre if categoria else "")
        descripcion = Campo("Descripción", categoria.descripcion if categoria else "")

        def guardar(e):
            nombre.error(None)
            descripcion.error(None)
            try:
                if categoria:
                    self.servicio.editar_categoria(categoria.id, nombre.valor, descripcion.valor)
                    aviso = ("ok", "Operación exitosa", f"Se actualizó la categoría #{categoria.id}.")
                else:
                    nuevo = self.servicio.crear_categoria(nombre.valor, descripcion.valor)
                    aviso = ("ok", "Operación exitosa", f"Categoría creada con id {nuevo}.")
            except ErroresValidacion as err:
                nombre.error(err.errores.get("nombre"))
                descripcion.error(err.errores.get("descripcion"))
                self.page.update()
                return
            cerrar_modal(self.page)
            self.refrescar(aviso)

        nombre.input.on_submit = guardar
        abrir_modal(self.page, ft.Column(tight=True, spacing=24, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[
            titulo_modal("Editar categoría" if categoria else "Crear categoría",
                         "Nombre y descripción son obligatorios."),
            nombre.control,
            descripcion.control,
            pie_modal(
                boton("Cancelar", lambda e: cerrar_modal(self.page), "secundario"),
                boton("Guardar categoría", guardar),
            ),
        ]), ancho=720)

    def _eliminar(self, categoria):
        def confirmar():
            try:
                self.servicio.eliminar_categoria(categoria.id)
            except FoodStoreError as err:      # tiene productos activos
                self._modal_bloqueado(categoria, err)
                return
            self.refrescar(("ok", "Operación exitosa", f"Se eliminó la categoría \"{categoria.nombre}\"."))

        if self.servicio.cantidad_productos(categoria.id):
            confirmar()                         # muestra directamente el bloqueo
        else:
            modal_confirmar(self.page, f"Eliminar \"{categoria.nombre}\"",
                            "La baja es lógica: la categoría deja de aparecer en los listados.",
                            "Eliminar", confirmar)

    def _modal_bloqueado(self, categoria, err: FoodStoreError):
        def ver_productos(e):
            cerrar_modal(self.page)
            self.app.ir("admin_productos", categoria_id=categoria.id)

        abrir_modal(self.page, ft.Column(tight=True, spacing=26, controls=[
            titulo_modal(f"No se puede eliminar \"{categoria.nombre}\""),
            alerta("warn", err.titulo, err.mensaje),
            txt("Regla de negocio: no se puede eliminar una categoría con productos activos.", 15,
                color=Tema.TEXTO_SUAVE),
            pie_modal(
                boton("Ver productos", ver_productos, "secundario"),
                boton("Entendido", lambda e: cerrar_modal(self.page)),
            ),
        ]), ancho=700)

    # ---------------------------------------------------------- contenido
    def contenido(self):
        cats = self.servicio.categorias()
        filas = [
            [
                str(c.id),
                txt(c.nombre, 16, 600),
                txt(c.descripcion, 16, color=Tema.TEXTO_SUAVE),
                str(self.servicio.cantidad_productos(c.id)),
                acciones(
                    boton("Editar", lambda e, c=c: self._abrir_form(c), "secundario", chico=True),
                    boton("Eliminar", lambda e, c=c: self._eliminar(c), "peligro", chico=True),
                ),
            ]
            for c in cats
        ]
        return self.sin_nulos(
            encabezado("Categorías", "Listá, creá, editá o eliminá las categorías del catálogo",
                       boton("+ Crear categoría", lambda e: self._abrir_form())),
            self.control_aviso(),
            tabla([("ID", 1), ("Nombre", 3), ("Descripción", 6), ("Productos", 2), ("Acciones", 3)], filas),
            nota(f"Mostrando {len(cats)} categoría{'s' if len(cats) != 1 else ''} · "
                 "La baja es lógica: las eliminadas dejan de aparecer en los listados."),
        )
