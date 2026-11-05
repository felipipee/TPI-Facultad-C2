"""
Datos de ejemplo en memoria para que la interfaz funcione de punta a punta.

Las vistas solo hablan con `ServicioDemo`. Cuando tengan la capa real
(Entidades/ + servicios), reemplacen esta clase por la suya respetando
los mismos métodos y excepciones, y la UI no cambia.
"""
from dataclasses import dataclass, field
from datetime import date
from enum import Enum


# ------------------------------------------------------------------ enums
class Rol(Enum):
    ADMIN = "ADMIN"
    USUARIO = "USUARIO"


class Estado(Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    TERMINADO = "TERMINADO"
    CANCELADO = "CANCELADO"


class FormaPago(Enum):
    TARJETA = "Tarjeta"
    TRANSFERENCIA = "Transferencia"
    EFECTIVO = "Efectivo"


TRANSICIONES_VALIDAS = {
    Estado.PENDIENTE: {Estado.CONFIRMADO, Estado.CANCELADO},
    Estado.CONFIRMADO: {Estado.TERMINADO, Estado.CANCELADO},
    Estado.TERMINADO: set(),
    Estado.CANCELADO: set(),
}


# ------------------------------------------------------------- excepciones
class FoodStoreError(Exception):
    """Error de negocio. `campo` indica qué input marcar en rojo (opcional)."""

    def __init__(self, mensaje: str, campo: str | None = None, titulo: str | None = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.campo = campo
        self.titulo = titulo


class ErroresValidacion(FoodStoreError):
    """Agrupa varios errores de formulario: {campo: mensaje}."""

    def __init__(self, errores: dict[str, str]):
        super().__init__("Hay datos inválidos")
        self.errores = errores


# ---------------------------------------------------------------- modelos
@dataclass
class Categoria:
    id: int
    nombre: str
    descripcion: str
    eliminado: bool = False


@dataclass
class Producto:
    id: int
    nombre: str
    descripcion: str
    precio: float
    stock: int
    categoria_id: int
    imagen: str
    disponible: bool = True
    eliminado: bool = False


class Usuario:
    def __init__(self, id, nombre, apellido, mail, celular, clave, rol: Rol):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.mail = mail
        self.celular = celular
        self.__clave = clave          # privada: nunca se muestra
        self.rol = rol
        self.eliminado = False

    def verificar_clave(self, clave: str) -> bool:
        return self.__clave == clave

    def cambiar_clave(self, clave: str):
        self.__clave = clave

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def iniciales(self):
        return (self.nombre[:1] + self.apellido[:1]).upper()


@dataclass
class DetallePedido:
    producto_id: int
    nombre: str
    cantidad: int
    precio: float

    @property
    def subtotal(self):
        return self.cantidad * self.precio


@dataclass
class Pedido:
    id: int
    usuario_id: int
    estado: Estado
    forma_pago: FormaPago
    fecha: date
    detalles: list[DetallePedido] = field(default_factory=list)
    eliminado: bool = False

    @property
    def total(self):
        return sum(d.subtotal for d in self.detalles)

    @property
    def cerrado(self):
        return self.estado in (Estado.TERMINADO, Estado.CANCELADO)


# --------------------------------------------------------------- servicio
class ServicioDemo:
    def __init__(self):
        self._categorias: dict[int, Categoria] = {}
        self._productos: dict[int, Producto] = {}
        self._usuarios: dict[int, Usuario] = {}
        self._pedidos: dict[int, Pedido] = {}
        self._cargar_ejemplos()

    # ---------- utilidades
    @staticmethod
    def _siguiente_id(tabla: dict) -> int:
        return max(tabla, default=0) + 1

    @staticmethod
    def _a_numero(texto, campo, entero=False):
        try:
            valor = int(texto) if entero else float(str(texto).replace(",", "."))
        except (TypeError, ValueError):
            tipo = "un número entero" if entero else "un número"
            raise FoodStoreError(f"Ingresá {tipo}.", campo)
        return valor

    # ---------- login
    def autenticar(self, mail: str, clave: str) -> Usuario | None:
        mail = (mail or "").strip().lower()
        for u in self.usuarios():
            if u.mail.lower() == mail and u.verificar_clave(clave or ""):
                return u
        return None

    # ---------- categorías
    def categorias(self) -> list[Categoria]:
        return [c for c in self._categorias.values() if not c.eliminado]

    def categoria(self, id_) -> Categoria | None:
        c = self._categorias.get(id_)
        return c if c and not c.eliminado else None

    def cantidad_productos(self, categoria_id: int) -> int:
        return sum(1 for p in self.productos() if p.categoria_id == categoria_id)

    def _validar_categoria(self, nombre, descripcion, id_actual=None):
        errores = {}
        nombre, descripcion = (nombre or "").strip(), (descripcion or "").strip()
        if not nombre:
            errores["nombre"] = "El nombre es obligatorio."
        elif any(c.nombre.lower() == nombre.lower() and c.id != id_actual for c in self.categorias()):
            errores["nombre"] = "Ya existe una categoría con ese nombre (no distingue mayúsculas)."
        if not descripcion:
            errores["descripcion"] = "La descripción es obligatoria."
        if errores:
            raise ErroresValidacion(errores)
        return nombre, descripcion

    def crear_categoria(self, nombre, descripcion) -> int:
        nombre, descripcion = self._validar_categoria(nombre, descripcion)
        nuevo = self._siguiente_id(self._categorias)
        self._categorias[nuevo] = Categoria(nuevo, nombre, descripcion)
        return nuevo

    def editar_categoria(self, id_, nombre, descripcion):
        nombre, descripcion = self._validar_categoria(nombre, descripcion, id_)
        c = self._categorias[id_]
        c.nombre, c.descripcion = nombre, descripcion

    def eliminar_categoria(self, id_):
        cantidad = self.cantidad_productos(id_)
        if cantidad:
            raise FoodStoreError(
                "Eliminá o reasigná esos productos antes de dar de baja la categoría.",
                titulo=f"La categoría tiene {cantidad} producto{'s' if cantidad != 1 else ''} activo{'s' if cantidad != 1 else ''}",
            )
        self._categorias[id_].eliminado = True

    # ---------- productos
    def productos(self) -> list[Producto]:
        return [p for p in self._productos.values() if not p.eliminado]

    def producto(self, id_) -> Producto | None:
        p = self._productos.get(id_)
        return p if p and not p.eliminado else None

    def productos_visibles(self) -> list[Producto]:
        """Lo que ve el cliente: disponibles y con stock."""
        return [p for p in self.productos() if p.disponible and p.stock > 0]

    def _validar_producto(self, datos: dict) -> dict:
        errores = {}
        limpio = {}
        for campo in ("nombre", "descripcion", "imagen"):
            limpio[campo] = (datos.get(campo) or "").strip()
            if not limpio[campo]:
                errores[campo] = "Este campo es obligatorio."
        for campo, entero, etiqueta in (("precio", False, "El precio"), ("stock", True, "El stock")):
            try:
                valor = self._a_numero(datos.get(campo), campo, entero)
                if valor < 0:
                    raise FoodStoreError(f"{etiqueta} no puede ser negativo.", campo)
                limpio[campo] = valor
            except FoodStoreError as e:
                errores[campo] = e.mensaje
        try:
            cat_id = int(datos.get("categoria_id"))
            if not self.categoria(cat_id):
                raise ValueError
            limpio["categoria_id"] = cat_id
        except (TypeError, ValueError):
            errores["categoria_id"] = "Elegí una categoría existente."
        limpio["disponible"] = bool(datos.get("disponible", True))
        if errores:
            raise ErroresValidacion(errores)
        return limpio

    def crear_producto(self, datos: dict) -> int:
        limpio = self._validar_producto(datos)
        nuevo = self._siguiente_id(self._productos)
        self._productos[nuevo] = Producto(id=nuevo, **limpio)
        return nuevo

    def editar_producto(self, id_, datos: dict):
        limpio = self._validar_producto(datos)
        p = self._productos[id_]
        for k, v in limpio.items():
            setattr(p, k, v)

    def eliminar_producto(self, id_):
        self._productos[id_].eliminado = True

    # ---------- usuarios
    def usuarios(self) -> list[Usuario]:
        return [u for u in self._usuarios.values() if not u.eliminado]

    def usuario(self, id_) -> Usuario | None:
        u = self._usuarios.get(id_)
        return u if u and not u.eliminado else None

    def _validar_usuario(self, datos: dict, id_actual=None) -> dict:
        errores = {}
        limpio = {k: (datos.get(k) or "").strip() for k in ("nombre", "apellido", "mail", "celular")}
        for campo in ("nombre", "apellido", "celular"):
            if not limpio[campo]:
                errores[campo] = "Este campo es obligatorio."
        mail = limpio["mail"]
        if not mail or "@" not in mail or "." not in mail.split("@")[-1]:
            errores["mail"] = "Ingresá un mail válido."
        elif any(u.mail.lower() == mail.lower() and u.id != id_actual for u in self.usuarios()):
            errores["mail"] = "Ese mail ya está registrado. Ingresá otro."
        clave = datos.get("clave") or ""
        if id_actual is None or clave:
            if len(clave) < 6:
                errores["clave"] = "La contraseña debe tener al menos 6 caracteres."
        limpio["clave"] = clave
        try:
            limpio["rol"] = Rol(datos.get("rol"))
        except ValueError:
            errores["rol"] = "Elegí un rol."
        if errores:
            raise ErroresValidacion(errores)
        return limpio

    def crear_usuario(self, datos: dict) -> int:
        d = self._validar_usuario(datos)
        nuevo = self._siguiente_id(self._usuarios)
        self._usuarios[nuevo] = Usuario(nuevo, d["nombre"], d["apellido"], d["mail"],
                                        d["celular"], d["clave"], d["rol"])
        return nuevo

    def editar_usuario(self, id_, datos: dict):
        d = self._validar_usuario(datos, id_)
        u = self._usuarios[id_]
        u.nombre, u.apellido, u.mail, u.celular, u.rol = (
            d["nombre"], d["apellido"], d["mail"], d["celular"], d["rol"])
        if d["clave"]:
            u.cambiar_clave(d["clave"])

    def eliminar_usuario(self, id_, id_sesion):
        if id_ == id_sesion:
            raise FoodStoreError("Un administrador no puede eliminarse a sí mismo mientras tiene la sesión abierta.")
        self._usuarios[id_].eliminado = True

    # ---------- pedidos
    def pedidos(self, usuario_id=None, estado: Estado | None = None) -> list[Pedido]:
        res = [p for p in self._pedidos.values() if not p.eliminado]
        if usuario_id is not None:
            res = [p for p in res if p.usuario_id == usuario_id]
        if estado is not None:
            res = [p for p in res if p.estado == estado]
        return res

    def pedido(self, id_) -> Pedido | None:
        p = self._pedidos.get(id_)
        return p if p and not p.eliminado else None

    def validar_detalle(self, producto_id, cantidad_texto, ya_en_carrito=0) -> tuple[Producto, int]:
        """Valida un detalle antes de agregarlo al carrito. No toca el stock."""
        p = self.producto(producto_id) if producto_id is not None else None
        if not p or not p.disponible:
            raise FoodStoreError("Elegí un producto disponible.", "producto", "Producto inválido")
        cantidad = self._a_numero(cantidad_texto, "cantidad", entero=True)
        if cantidad <= 0:
            raise FoodStoreError("La cantidad debe ser mayor a 0.", "cantidad", "Cantidad inválida")
        total = cantidad + ya_en_carrito
        if total > p.stock:
            extra = f" (ya tenés {ya_en_carrito} en el pedido)" if ya_en_carrito else ""
            raise FoodStoreError(
                f"{p.nombre} tiene {p.stock} unidades y pediste {total}{extra}. "
                "No se agregó el detalle ni se modificó el stock.",
                "cantidad", "Stock insuficiente")
        return p, cantidad

    def crear_pedido(self, usuario_id, forma_pago: FormaPago, items: dict[int, int]) -> int:
        """items: {producto_id: cantidad}. Todo o nada: si algo falla, el stock queda igual."""
        if not self.usuario(usuario_id):
            raise FoodStoreError("Elegí un usuario.", "usuario")
        if not items:
            raise FoodStoreError("Agregá al menos un detalle.")
        detalles = []
        for prod_id, cant in items.items():
            p, cant = self.validar_detalle(prod_id, cant)
            detalles.append(DetallePedido(p.id, p.nombre, cant, p.precio))
        for d in detalles:
            self._productos[d.producto_id].stock -= d.cantidad
        nuevo = self._siguiente_id(self._pedidos)
        self._pedidos[nuevo] = Pedido(nuevo, usuario_id, Estado.PENDIENTE, forma_pago, date.today(), detalles)
        return nuevo

    def _devolver_stock(self, pedido: Pedido):
        for d in pedido.detalles:
            if d.producto_id in self._productos:
                self._productos[d.producto_id].stock += d.cantidad

    def cambiar_estado(self, id_, nuevo: Estado):
        p = self._pedidos[id_]
        if nuevo not in TRANSICIONES_VALIDAS[p.estado]:
            raise FoodStoreError(
                f"{p.estado.value} → {nuevo.value} no es válido. El pedido no se modificó.",
                titulo="Transición no permitida")
        if nuevo == Estado.CANCELADO:
            self._devolver_stock(p)
        p.estado = nuevo

    def eliminar_pedido(self, id_):
        p = self._pedidos[id_]
        if not p.cerrado:
            self._devolver_stock(p)
        p.eliminado = True

    # ---------- datos iniciales (los de las pantallas del diseño)
    def _cargar_ejemplos(self):
        for c in [
            Categoria(1, "Hamburguesas", "Clásicas y gourmet, con pan de papa"),
            Categoria(2, "Pizzas", "Al molde y a la piedra"),
            Categoria(3, "Bebidas", "Gaseosas, jugos y cervezas"),
            Categoria(4, "Postres", "Dulces para cerrar la comida"),
            Categoria(5, "Ensaladas", "Frescas, para todos los días"),
        ]:
            self._categorias[c.id] = c

        for p in [
            Producto(1, "Hamburguesa Clásica", "Carne 150 g, cheddar, lechuga y tomate", 8500, 24, 1, "img/clasica.jpg"),
            Producto(2, "Doble Cheddar", "Doble carne, doble cheddar y panceta", 11200, 12, 1, "img/doble.jpg"),
            Producto(3, "Pizza Muzzarella", "Salsa de tomate, muzzarella y aceitunas", 9800, 8, 2, "img/muzza.jpg"),
            Producto(4, "Pizza Napolitana", "Tomate en rodajas, ajo y albahaca", 11500, 0, 2, "img/napo.jpg"),
            Producto(5, "Coca-Cola 500 ml", "Botella individual bien fría", 2400, 60, 3, "img/coca.jpg"),
            Producto(6, "Cerveza IPA", "Lata 473 ml, bien lupulada", 4200, 30, 3, "img/ipa.jpg", disponible=False),
            Producto(7, "Flan con dulce de leche", "Casero, con crema chantilly", 3900, 15, 4, "img/flan.jpg"),
        ]:
            self._productos[p.id] = p

        for u in [
            Usuario(1, "Ana", "Pérez", "admin@foodstore.com", "261 555-0101", "admin123", Rol.ADMIN),
            Usuario(2, "Juan", "Gómez", "juan.gomez@mail.com", "261 555-0148", "juan123", Rol.USUARIO),
            Usuario(3, "Lucía", "Fernández", "lucia.f@mail.com", "261 555-0172", "lucia123", Rol.USUARIO),
            Usuario(4, "Marcos", "Díaz", "marcos.diaz@mail.com", "261 555-0190", "marcos123", Rol.USUARIO),
        ]:
            self._usuarios[u.id] = u

        def det(prod_id, cant):
            p = self._productos[prod_id]
            return DetallePedido(p.id, p.nombre, cant, p.precio)

        for p in [
            Pedido(1, 2, Estado.PENDIENTE, FormaPago.EFECTIVO, date(2026, 10, 26), [det(1, 1), det(3, 1)]),
            Pedido(2, 3, Estado.CONFIRMADO, FormaPago.TARJETA, date(2026, 10, 25), [det(2, 1), det(5, 1)]),
            Pedido(3, 2, Estado.TERMINADO, FormaPago.TRANSFERENCIA, date(2026, 10, 22), [det(3, 2), det(7, 1)]),
            Pedido(4, 4, Estado.CANCELADO, FormaPago.EFECTIVO, date(2026, 10, 21), [det(1, 3)]),
            Pedido(5, 3, Estado.PENDIENTE, FormaPago.TARJETA, date(2026, 10, 26), [det(5, 2), det(7, 1)]),
            Pedido(6, 2, Estado.CANCELADO, FormaPago.EFECTIVO, date(2026, 10, 20), [det(5, 2)]),
        ]:
            self._pedidos[p.id] = p
