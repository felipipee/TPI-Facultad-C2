# Food Store: cómo funciona la interfaz

Este documento explica la interfaz gráfica del TPI: qué es Flet, cómo está organizado el código, qué pasa cuando hacés clic en algo y cómo se conecta con los datos. Al final hay un guion sugerido para el video.

---

## 1. Qué es Flet

[Flet](https://flet.dev) es una biblioteca de Python para hacer interfaces gráficas (ventanas, botones, formularios) **escribiendo solo Python**. Por dentro usa Flutter, el framework de Google para apps, pero nosotros nunca tocamos Flutter: armamos la pantalla con objetos de Python y Flet se encarga de dibujarlos.

Usamos la versión **1.0.5**.

### Las tres ideas que hay que entender

**1. La página (`ft.Page`)**
Es la ventana. Flet nos la da cuando arranca el programa y le agregamos cosas:

```python
def main(page: ft.Page):
    page.add(ft.Text("Hola"))

ft.run(main)
```

`ft.run(main)` abre la ventana y llama a `main` pasándole la página.

**2. Los controles**
Todo lo que se ve es un *control*: un objeto de Python. Se dividen en dos tipos:

| Tipo | Ejemplos | Para qué sirve |
|---|---|---|
| Controles visibles | `ft.Text`, `ft.TextField`, `ft.Button`, `ft.Icon`, `ft.Dropdown`, `ft.Switch` | Mostrar algo o recibir datos |
| Controles de distribución (layout) | `ft.Row` (fila), `ft.Column` (columna), `ft.Container` (caja) | Ordenar a los demás |

Los controles se meten unos dentro de otros, como cajas dentro de cajas. Una pantalla es un **árbol de controles**:

```python
ft.Column([                       # una columna...
    ft.Text("Iniciar sesión"),    # ...con un título
    ft.TextField(label="Mail"),   # ...un campo
    ft.Row([                      # ...y una fila con dos botones
        ft.Button("Cancelar"),
        ft.Button("Ingresar"),
    ]),
])
```

`ft.Container` es la caja más usada: le da a lo que tiene adentro fondo (`bgcolor`), bordes redondeados (`border_radius`), margen interno (`padding`), borde (`border`) y puede ser clickeable (`on_click`).

`expand=True` le dice a un control "ocupá todo el espacio que sobra". Así logramos, por ejemplo, que el contenido ocupe todo lo que deja libre la barra lateral.

**3. Los eventos y `update()`**
Los controles reciben funciones que se ejecutan cuando pasa algo:

```python
def al_hacer_click(e):
    texto.value = "¡Hiciste clic!"
    page.update()          # sin esto, la pantalla no cambia

boton = ft.Button("Clic", on_click=al_hacer_click)
```

Modificar un control en Python **no** cambia la pantalla automáticamente. Hay que llamar a `page.update()` para que Flet mande los cambios a la ventana. Esto es lo que más se olvida.

Otros eventos que usamos: `on_change` (cuando escribís en un campo), `on_select` (cuando elegís en un desplegable), `on_click` en contenedores (filas de tabla, tarjetas, ítems del menú).

### Otras cosas de Flet que usamos

- **Ventanas emergentes (modales):** `page.show_dialog(dialogo)` para abrir y `page.pop_dialog()` para cerrar. Las usamos para crear categorías, confirmar eliminaciones, cambiar el estado de un pedido, etc.
- **Fuentes propias:** en `page.fonts` registramos los archivos de la tipografía Inter que están en `assets/fonts/`. Por eso `ft.run(main, assets_dir="assets")` le indica a Flet dónde está esa carpeta.
- **Tamaño de la ventana:** `page.window.width`, `page.window.min_width`, etc.

---

## 2. Cómo arranca el programa

```
python main.py
```

1. [main.py](main.py) llama a `ft.run(main, assets_dir="assets")`.
2. Flet abre la ventana y ejecuta `main(page)`, que crea un objeto `App(page)`.
3. `App` ([UI/app.py](UI/app.py)) configura la ventana (título, tamaño, colores y fuentes del tema) y muestra el login.

---

## 3. Organización de las carpetas

```
main.py                  ← punto de entrada
assets/fonts/            ← tipografía Inter (5 grosores)
UI/
├── app.py               ← la App: navegación entre pantallas y sesión
├── tema.py              ← colores, tipografía y helpers de formato
├── datos_demo.py        ← datos de ejemplo y reglas de negocio (provisorio)
├── componentes/         ← piezas reutilizables (botón, campo, tabla, modal...)
└── vistas/              ← una clase por pantalla
```

La idea es separar responsabilidades:

| Capa | Pregunta que responde | Archivos |
|---|---|---|
| **Tema** | ¿De qué color y con qué letra se ve? | `tema.py` |
| **Componentes** | ¿Cómo es un botón, un campo, una tabla? | `componentes/` |
| **Vistas** | ¿Qué hay en cada pantalla y qué pasa al tocar algo? | `vistas/` |
| **App** | ¿En qué pantalla estoy y quién inició sesión? | `app.py` |
| **Servicio** | ¿Qué datos hay y qué reglas se cumplen? | `datos_demo.py` |

Las vistas **no** guardan datos ni validan reglas de negocio: le piden todo al servicio. Así, si mañana el servicio guarda en una base de datos, las pantallas no cambian.

---

## 4. El tema: `UI/tema.py`

Traduce a código la pantalla 19 del diseño (sistema de diseño).

- **Clase `Tema`:** todos los colores con nombre. En vez de escribir `"#E4572E"` en cada botón escribimos `Tema.PRIMARIO`. Si hay que cambiar el naranja, se cambia en un solo lugar.
  - `PRIMARIO` (naranja), `OSCURO` (marrón de la barra lateral), `FONDO` (crema), `TEXTO`, `TEXTO_SUAVE`, `BORDE`.
  - Colores de estado, cada uno con su fondo: `EXITO` (verde), `ALERTA` (ámbar), `ERROR` (rojo), `INFO` (azul).
- **`txt(valor, tamaño, peso, color)`:** atajo para crear textos con la tipografía Inter. El *peso* es el grosor (400 normal, 700 negrita, 800 extra negrita).
  - Detalle técnico: Flet registra **un archivo de fuente por nombre de familia**, entonces registramos cada grosor como una familia distinta (`"Inter"`, `"Inter700"`…) y `txt` elige la correcta según el peso.
- **`pesos(21800)`** → `"$21.800"`: formatea precios como en Argentina.
- **`aplicar_tema(page)`:** registra las fuentes y pone el fondo crema en la ventana.

---

## 5. Los componentes: `UI/componentes/`

Son funciones o clases que devuelven controles ya armados con el estilo del diseño. Cada pantalla los reutiliza, así todas se ven iguales y no repetimos código.

| Archivo | Qué ofrece |
|---|---|
| `boton.py` | `boton(texto, on_click, tipo)` con tipos `primario` (naranja), `secundario` (blanco con borde) y `peligro` (rojo). Puede estar deshabilitado o ser chico. |
| `campo.py` | `Campo`: campo de texto con la etiqueta arriba y el mensaje de error abajo. `Selector`: desplegable con el mismo estilo. `Opciones`: botones segmentados (por ejemplo, ADMIN / USUARIO). |
| `badge.py` | Etiquetas de colores: estado del pedido, rol, disponibilidad del producto. |
| `alerta.py` | Cajas de aviso de error, advertencia, información o éxito. |
| `tabla.py` | Tabla con cabecera, filas clickeables y fila seleccionada. |
| `modal.py` | Ventanas emergentes y `modal_confirmar` ("¿Seguro que querés eliminar…?"). |
| `marca.py` | Logo, avatar con iniciales, tarjeta blanca, encabezado de página, dibujo del plato de cada producto. |
| `pedido.py` | Tabla de detalles de un pedido y fila de total, compartidas por admin y cliente. |

### Ejemplo: cómo funciona `Campo`

Flet tiene `ft.TextField`, pero el diseño pide la etiqueta **arriba** del campo y el error **abajo** en rojo. Entonces `Campo` arma una columna con tres cosas:

```
Mail                      ← etiqueta (texto gris)
[ juan@mail.com        ]  ← ft.TextField
Ese mail ya está ...      ← texto de error (oculto hasta que hay error)
```

Y ofrece:
- `campo.valor` → lo que escribió el usuario.
- `campo.error("mensaje")` → borde rojo y mensaje abajo.
- `campo.error("")` → solo borde rojo, sin mensaje (lo usa el login para no decir qué dato estuvo mal).
- `campo.error(None)` → vuelve a la normalidad.

---

## 6. Las vistas: `UI/vistas/`

Cada pantalla es una **clase**. Acá aparece la programación orientada a objetos: herencia, clases abstractas y polimorfismo.

### La jerarquía de clases

```
Vista (abstracta)                     ← todas las pantallas
├── VistaLogin                        ← pantallas 01-03
└── VistaConMenu (abstracta)          ← pantallas con menú
    ├── VistaAdmin                    ← agrega la barra lateral oscura
    │   ├── VistaAdminInicio
    │   ├── VistaAdminCategorias
    │   ├── VistaAdminProductos / VistaAdminProductoForm
    │   ├── VistaAdminUsuarios  / VistaAdminUsuarioForm
    │   └── VistaAdminPedidos   / VistaAdminPedidoForm
    └── VistaCliente                  ← agrega la barra superior blanca
        ├── VistaClienteCategorias
        ├── VistaClienteProductos
        ├── VistaClientePedidos
        └── VistaClienteDatos
```

Está en [UI/vistas/vista_abc.py](UI/vistas/vista_abc.py) (ABC = *Abstract Base Class*).

- **`Vista`** guarda lo que toda pantalla necesita: la `app`, la `page` y el `servicio`. Tiene el método abstracto `construir()`, que devuelve el control raíz de la pantalla. Al ser abstracta, no se puede crear una `Vista` "a secas".
- **`VistaConMenu`** agrega dos métodos abstractos que cada hija tiene que completar:
  - `contenido()` → la lista de controles del centro de la pantalla.
  - `layout(cuerpo)` → dónde va el menú y dónde va el centro.

  `construir()` ya está implementado en `VistaConMenu`: junta `contenido()` y `layout()`. Las hijas no lo reescriben. Esto es el patrón **Template Method**: la clase padre define los pasos y las hijas completan los huecos.
- **`VistaAdmin`** implementa `layout()` con la barra lateral oscura (logo, menú, tarjeta del usuario, "Cerrar sesión").
- **`VistaCliente`** implementa `layout()` con la barra superior blanca.
- Cada pantalla concreta solo implementa `contenido()`. Por ejemplo, `VistaAdminUsuarios.contenido()` devuelve el encabezado, la tabla de usuarios y la alerta. No se preocupa por el menú, que lo hereda.

Cada vista tiene un atributo de clase `ruta` (por ejemplo `"admin_usuarios"`) que usa el menú para pintar de naranja el ítem de la pantalla actual.

### `refrescar()`: cómo se actualiza una pantalla

Después de cada operación (crear, editar, eliminar), la vista llama a:

```python
self.refrescar(("ok", "Operación exitosa", "Se eliminó a Juan Gómez."))
```

Eso vuelve a ejecutar `contenido()` (que le pide al servicio los datos actualizados), reemplaza el centro de la pantalla y llama a `page.update()`. El parámetro opcional es el **aviso**: una tupla `(tipo, título, detalle)` que se muestra como alerta verde o roja arriba de la tabla.

Es un enfoque simple: en vez de modificar fila por fila, se redibuja todo el centro. Para la cantidad de datos de este sistema es instantáneo y evita errores de "la tabla quedó desactualizada".

---

## 7. La App: navegación y sesión

[UI/app.py](UI/app.py) tiene un diccionario que asocia un nombre de ruta con la clase de la vista:

```python
RUTAS = {
    "login": VistaLogin,
    "admin_usuarios": VistaAdminUsuarios,
    "cliente_pedidos": VistaClientePedidos,
    ...
}
```

Para cambiar de pantalla, cualquier vista llama a:

```python
self.app.ir("admin_usuario_form", usuario=u)
```

`ir()` hace cuatro cosas:
1. **Control de acceso:** si nadie inició sesión, manda al login sin importar la ruta pedida.
2. Busca la clase en `RUTAS` y crea la vista, pasándole los datos extra (`usuario=u`, `aviso=...`, `categoria_id=...`).
3. Borra lo que había en la página y pone la vista nueva.
4. Llama a `page.update()`.

La App también guarda **quién inició sesión** en `self.usuario`:
- `iniciar_sesion(usuario)` lo guarda y manda al inicio de admin o al catálogo de cliente **según el rol**.
- `cerrar_sesion()` lo borra y vuelve al login.

Así cada vista sabe quién está usando el sistema (`self.app.usuario`). Por ejemplo, "Mis pedidos" solo muestra los pedidos de ese usuario, y un admin no puede eliminarse a sí mismo.

---

## 8. El servicio y las reglas de negocio: `UI/datos_demo.py`

Este archivo es **provisorio**: simula la capa de datos con listas en memoria (los datos se pierden al cerrar el programa) y trae los mismos ejemplos que se ven en las pantallas del diseño. Cuando esté lista la capa real de `Entidades/`, se reemplaza `ServicioDemo` por el servicio real con **los mismos métodos** y la interfaz sigue funcionando igual.

### Qué contiene

- **Enumeraciones (`Enum`):** `Rol` (ADMIN, USUARIO), `Estado` del pedido (PENDIENTE, CONFIRMADO, TERMINADO, CANCELADO), `FormaPago`.
- **Modelos:** `Categoria`, `Producto`, `Usuario`, `Pedido`, `DetallePedido`.
  - `Usuario` guarda la contraseña en un atributo **privado** `self.__clave` (doble guion bajo). Desde afuera no se puede leer: solo se puede verificar con `verificar_clave()` o cambiar con `cambiar_clave()`. Eso es **encapsulamiento**, y por eso la contraseña nunca aparece en pantalla.
  - `Pedido.total` es una propiedad calculada: suma los subtotales de sus detalles.
- **Excepciones propias:**
  - `FoodStoreError(mensaje, campo, titulo)`: error de negocio. `campo` indica qué input marcar en rojo.
  - `ErroresValidacion({campo: mensaje})`: varios errores de formulario juntos (hereda de `FoodStoreError`).
- **`ServicioDemo`:** los métodos que usan las pantallas (`autenticar`, `categorias`, `crear_producto`, `eliminar_usuario`, `crear_pedido`, `cambiar_estado`…).

### Cómo viaja un error hasta la pantalla

Ejemplo: el admin crea un usuario con un mail que ya existe.

```
1. El usuario toca "Guardar usuario"
2. La vista junta los valores de los campos en un diccionario
3. Llama a servicio.crear_usuario(datos)
4. El servicio valida y encuentra el mail repetido
      → raise ErroresValidacion({"mail": "Ese mail ya está registrado. Ingresá otro."})
5. La vista lo atrapa con try/except
      → self.mail.error("Ese mail ya está registrado...")  (borde rojo + mensaje)
      → page.update()
6. Si no hubo error: app.ir("admin_usuarios", aviso=("ok", "Operación exitosa", ...))
```

La regla ("el mail no se puede repetir") vive en el **servicio**. La vista solo decide **cómo mostrar** el error. Ese reparto se repite en todas las pantallas.

### Reglas de negocio implementadas

| Regla | Dónde se ve |
|---|---|
| 3 intentos de login; después se bloquea | Login (pantallas 02 y 03) |
| No hay dos categorías con el mismo nombre (sin importar mayúsculas) | Categorías (06) |
| No se puede eliminar una categoría con productos activos | Categorías (07) |
| Precio y stock no pueden ser negativos | Productos (09) |
| Mail único y contraseña de al menos 6 caracteres | Usuarios (11) |
| Un admin no puede eliminarse a sí mismo | Usuarios (10) |
| No se puede pedir más de lo que hay en stock (contando lo ya cargado en el pedido) | Nuevo pedido (13) |
| Crear un pedido es "todo o nada": si un detalle falla, el stock no cambia | Nuevo pedido (13) |
| Solo valen ciertas transiciones de estado | Cambiar estado (14) |
| Cancelar o eliminar un pedido abierto devuelve el stock | Pedidos (12) |
| El cliente solo ve productos disponibles y con stock | Productos del cliente (16) |
| El cliente solo ve sus propios pedidos | Mis pedidos (17) |
| Las eliminaciones son lógicas (se marca `eliminado = True`, no se borra) | Todas las bajas |

Transiciones de estado válidas:

```
PENDIENTE ──► CONFIRMADO ──► TERMINADO
    │              │
    └──────────────┴──► CANCELADO
```

TERMINADO y CANCELADO son estados finales: no se puede salir de ellos.

---

## 9. Recorrido completo: el login

Juntando todo, esto pasa cuando alguien inicia sesión ([UI/vistas/login.py](UI/vistas/login.py)):

1. `App` muestra `VistaLogin`, que tiene dos `Campo` (mail y contraseña) y un contador `self.intentos = 0`.
2. El usuario toca "Ingresar" → se ejecuta `_ingresar(e)`.
3. La vista llama a `servicio.autenticar(mail, clave)`, que busca el usuario por mail y usa `verificar_clave()`.
4. **Si es correcto:** `app.iniciar_sesion(usuario)` → según el rol, va a `admin_inicio` o a `cliente_categorias`.
5. **Si es incorrecto:** suma un intento, marca ambos campos en rojo **sin decir cuál falló** (por seguridad) y muestra la barra "Intento 1 de 3".
6. **Al tercer error:** la pantalla cambia a "Se agotaron los intentos" con un botón Salir que cierra la ventana.

---

## 10. Correspondencia con el diseño

| Pantalla del diseño | Clase | Archivo |
|---|---|---|
| 01–03 Login | `VistaLogin` | `vistas/login.py` |
| 04 Inicio admin | `VistaAdminInicio` | `vistas/admin_inicio.py` |
| 05–07 Categorías | `VistaAdminCategorias` | `vistas/admin_categorias.py` |
| 08–09 Productos | `VistaAdminProductos`, `VistaAdminProductoForm` | `vistas/admin_productos.py` |
| 10–11 Usuarios | `VistaAdminUsuarios`, `VistaAdminUsuarioForm` | `vistas/admin_usuarios.py` |
| 12–14 Pedidos | `VistaAdminPedidos`, `VistaAdminPedidoForm` | `vistas/admin_pedidos.py` |
| 15–18 Cliente | `VistaClienteCategorias`, `VistaClienteProductos`, `VistaClientePedidos`, `VistaClienteDatos` | `vistas/cliente.py` |
| 19 Sistema de diseño | `Tema` + componentes | `tema.py`, `componentes/` |

---

## 11. Conceptos de Programación II que aparecen

- **Clases y objetos:** cada pantalla, cada modelo y el servicio son clases.
- **Herencia:** `VistaAdminUsuarios` → `VistaAdmin` → `VistaConMenu` → `Vista`.
- **Clases abstractas (`ABC`, `@abstractmethod`):** `Vista` y `VistaConMenu` obligan a las hijas a implementar `construir`, `contenido` y `layout`.
- **Polimorfismo:** `App.ir()` llama a `vista.construir()` sin saber qué pantalla es; cada clase responde a su manera.
- **Encapsulamiento:** la contraseña privada `__clave` del `Usuario`.
- **Propiedades (`@property`):** `Pedido.total`, `Usuario.nombre_completo`, `Campo.valor`.
- **Excepciones propias:** `FoodStoreError` y `ErroresValidacion`, con herencia entre ellas.
- **Enumeraciones:** `Rol`, `Estado`, `FormaPago`.
- **Diccionarios como tabla de despacho:** `RUTAS` (nombre → clase) y `TRANSICIONES_VALIDAS` (estado → estados permitidos).
- **Separación en capas:** la interfaz no conoce cómo se guardan los datos.

---

## 12. Guion sugerido para el video

> Ajustalo a tu forma de hablar; es una guía de orden, no un texto para leer.

1. **Presentación (20 s).** "Food Store es un sistema de pedidos de comida con dos roles: administrador y cliente. La interfaz la hicimos con Flet, una biblioteca que permite armar apps de escritorio usando solo Python."
2. **Cómo funciona Flet (40 s).** "En Flet todo es un control: textos, botones, campos. Se anidan con filas, columnas y contenedores, como cajas dentro de cajas. Los botones reciben una función que se ejecuta al hacer clic, y después de cambiar algo llamamos a `page.update()` para que se vea."
3. **Organización (40 s).** Mostrar las carpetas. "Separamos en capas: el tema con colores y letras, componentes reutilizables como botones y tablas, una clase por pantalla, la App que maneja la navegación, y el servicio con los datos y las reglas."
4. **Herencia de vistas (1 min).** Mostrar `vista_abc.py`. "Todas las pantallas heredan de `Vista`, que es abstracta. Las del administrador heredan de `VistaAdmin`, que ya trae la barra lateral; las del cliente de `VistaCliente`, con la barra de arriba. Cada pantalla solo define su contenido."
5. **Navegación y sesión (30 s).** Mostrar `RUTAS` en `app.py`. "Para cambiar de pantalla llamamos a `ir()` con el nombre de la ruta. Si nadie inició sesión, siempre vuelve al login."
6. **Demo admin (2 min).** Login con un error (mostrar los intentos), entrar como admin, crear una categoría repetida, intentar eliminar una categoría con productos, precio negativo, mail repetido, pedido sin stock, transición de estado inválida.
7. **Cómo viaja un error (40 s).** "Las reglas viven en el servicio. Si algo está mal, el servicio lanza una excepción propia; la pantalla la atrapa y marca el campo en rojo con el mensaje."
8. **Demo cliente (1 min).** Login como cliente, categorías, filtro de productos, mis pedidos, mis datos en solo lectura.
9. **Cierre (20 s).** "La interfaz no sabe cómo se guardan los datos: si cambiamos el servicio de ejemplo por uno con base de datos, las pantallas siguen funcionando igual."

### Usuarios para la demo

| Rol | Mail | Contraseña |
|---|---|---|
| Admin | admin@foodstore.com | admin123 |
| Cliente | juan.gomez@mail.com | juan123 |
| Cliente | lucia.f@mail.com | lucia123 |
| Cliente | marcos.diaz@mail.com | marcos123 |

Los datos se reinician cada vez que abrís el programa, así que podés ensayar la demo todas las veces que quieras.
