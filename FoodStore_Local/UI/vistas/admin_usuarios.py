"""Pantallas 10 y 11: listado de usuarios y alta/edición (mail repetido)."""
import flet as ft

from UI.componentes.alerta import alerta
from UI.componentes.badge import badge_rol, envolver
from UI.componentes.boton import boton
from UI.componentes.campo import Campo, Opciones
from UI.componentes.marca import encabezado, tarjeta
from UI.componentes.modal import modal_confirmar
from UI.componentes.tabla import acciones, tabla
from UI.datos_demo import ErroresValidacion, FoodStoreError, Rol
from UI.tema import Tema, txt
from UI.vistas.vista_abc import VistaAdmin


class VistaAdminUsuarios(VistaAdmin):
    ruta = "admin_usuarios"

    def _eliminar(self, u):
        def ok():
            try:
                self.servicio.eliminar_usuario(u.id, self.app.usuario.id)
            except FoodStoreError as err:
                self.refrescar(("error", "No se pudo eliminar", err.mensaje))
                return
            self.refrescar(("ok", "Operación exitosa", f"Se eliminó a {u.nombre_completo}."))

        modal_confirmar(self.page, f"Eliminar a {u.nombre_completo}",
                        "Baja lógica: el usuario ya no podrá iniciar sesión.", "Eliminar", ok)

    def contenido(self):
        yo = self.app.usuario
        filas = []
        for u in self.servicio.usuarios():
            es_yo = u.id == yo.id
            filas.append([
                str(u.id),
                txt(u.nombre, 16, 600),
                u.apellido,
                txt(u.mail, 16, color=Tema.TEXTO_SUAVE),
                envolver(badge_rol(u.rol)),
                acciones(
                    boton("Editar", lambda e, u=u: self.app.ir("admin_usuario_form", usuario=u), "secundario", chico=True),
                    boton("Eliminar", lambda e, u=u: self._eliminar(u), "peligro", chico=True, deshabilitado=es_yo),
                ),
            ])
        return self.sin_nulos(
            encabezado("Usuarios", "Altas, bajas y roles · la contraseña nunca se muestra",
                       boton("+ Crear usuario", lambda e: self.app.ir("admin_usuario_form"))),
            self.control_aviso(),
            tabla([("ID", 1), ("Nombre", 3), ("Apellido", 3), ("Mail", 5), ("Rol", 2), ("Acciones", 3)], filas),
            alerta("info", f"{yo.nombre_completo} tiene la sesión iniciada",
                   "Un administrador no puede eliminarse a sí mismo mientras tiene la sesión abierta."),
        )


class VistaAdminUsuarioForm(VistaAdmin):
    ruta = "admin_usuarios"

    def __init__(self, app, usuario=None, **kwargs):
        super().__init__(app, **kwargs)
        self.usuario = u = usuario
        self.nombre = Campo("Nombre", u.nombre if u else "", expand=True)
        self.apellido = Campo("Apellido", u.apellido if u else "", expand=True)
        self.mail = Campo("Mail", u.mail if u else "")
        self.celular = Campo("Celular", u.celular if u else "", expand=True)
        self.clave = Campo("Contraseña", password=True, expand=True,
                           ayuda="Dejala vacía para mantener la actual" if u else "Mínimo 6 caracteres")
        self.rol = Opciones([(r.value, r.value) for r in Rol], (u.rol if u else Rol.USUARIO).value)

    def _guardar(self, e):
        campos = {"nombre": self.nombre, "apellido": self.apellido, "mail": self.mail,
                  "celular": self.celular, "clave": self.clave}
        for c in campos.values():
            c.error(None)
        datos = {k: c.valor for k, c in campos.items()}
        datos["rol"] = self.rol.valor
        try:
            if self.usuario:
                self.servicio.editar_usuario(self.usuario.id, datos)
                aviso = ("ok", "Operación exitosa", f"Se actualizó el usuario #{self.usuario.id}.")
            else:
                nuevo = self.servicio.crear_usuario(datos)
                aviso = ("ok", "Operación exitosa", f"Usuario creado con id {nuevo}.")
        except ErroresValidacion as err:
            for clave, msg in err.errores.items():
                if clave in campos:
                    campos[clave].error(msg)
            self.page.update()
            return
        self.app.ir("admin_usuarios", aviso=aviso)

    def contenido(self):
        volver = boton("Volver al listado", lambda e: self.app.ir("admin_usuarios"), "secundario",
                       icono=ft.Icons.ARROW_BACK)
        arriba = ft.CrossAxisAlignment.START
        formulario = tarjeta(ft.Column(spacing=26, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[
            ft.Row([self.nombre.control, self.apellido.control], spacing=24, vertical_alignment=arriba),
            self.mail.control,
            ft.Row([self.celular.control, self.clave.control], spacing=24, vertical_alignment=arriba),
            ft.Column([txt("Rol", 14, 600, Tema.TEXTO_SUAVE), self.rol.control], spacing=10),
            ft.Row([boton("Cancelar", lambda e: self.app.ir("admin_usuarios"), "secundario"),
                    boton("Guardar usuario", self._guardar)],
                   alignment=ft.MainAxisAlignment.END, spacing=14),
        ]), padding=44, expand=True)

        lateral = ft.Column(width=520, spacing=22, controls=[
            alerta("info", "Contraseña protegida",
                   "Se guarda dentro del objeto y no se puede leer: solo se usa para verificar el inicio de sesión."),
            alerta("warn", "Roles",
                   "ADMIN gestiona todo. USUARIO solo consulta categorías, productos, sus pedidos y sus datos."),
        ])
        return [
            encabezado("Editar usuario" if self.usuario else "Nuevo usuario",
                       "Solo un ADMIN puede crear usuarios", volver),
            ft.Row([formulario, lateral], spacing=36, vertical_alignment=arriba),
        ]
