# Food Store

Sistema de gestión de pedidos de comida con interfaz gráfica de escritorio.
Trabajo Práctico Integrador · Programación II · UTN.

Tiene dos roles:

- **Administrador:** gestiona categorías, productos, usuarios y pedidos.
- **Cliente:** consulta el catálogo, sus pedidos y sus datos. No puede modificar nada.

## Requisitos

- Python 3.10 o superior (probado con 3.14)
- [Flet](https://flet.dev) 1.0.5

```bash
pip install flet==1.0.5
```

## Cómo ejecutarlo

Desde la carpeta del proyecto:

```bash
python main.py
```

### Usuarios de prueba

| Rol | Mail | Contraseña |
|---|---|---|
| Administrador | admin@foodstore.com | admin123 |
| Cliente | juan.gomez@mail.com | juan123 |
| Cliente | lucia.f@mail.com | lucia123 |
| Cliente | marcos.diaz@mail.com | marcos123 |

Los datos viven en memoria: cada vez que se abre el programa vuelven a los valores de ejemplo.

## Versión web

La app también está publicada en **https://tpifacu.vercel.app**. Python corre dentro del navegador, así que cada visitante tiene su propia copia de los datos de ejemplo. La primera carga tarda unos segundos.

Para actualizarla después de cambiar el código:

```bash
flet build web --yes                     # compila en build/web
rm -rf web && cp -r build/web web        # copia el resultado a web/
git add web && git commit -m "Actualizar versión web" && git push
```

Vercel publica la carpeta `web/` tal cual: no compila nada (ver `vercel.json`).

## Funcionalidades

**Inicio de sesión**
- Tres intentos. Al fallar no se indica qué dato estuvo mal; al tercer error se bloquea.
- Según el rol, el usuario entra al menú de administrador o al de cliente.

**Administrador**
- **Categorías:** alta, edición y baja. El nombre no se puede repetir (sin distinguir mayúsculas) y no se puede eliminar una categoría con productos.
- **Productos:** alta, edición y baja, con búsqueda y filtro por categoría. Precio y stock no pueden ser negativos. El formulario muestra cómo verá el cliente el producto.
- **Usuarios:** alta, edición y baja. El mail es único, la contraseña tiene al menos 6 caracteres y un administrador no puede eliminarse a sí mismo.
- **Pedidos:** alta con varios productos, filtros por usuario y estado, detalle, cambio de estado y baja.
  - No se puede pedir más que el stock disponible.
  - Crear un pedido es todo o nada: si un detalle es inválido, el stock no cambia.
  - Transiciones válidas: `PENDIENTE → CONFIRMADO → TERMINADO`, y `PENDIENTE` o `CONFIRMADO → CANCELADO`.
  - Cancelar o eliminar un pedido abierto devuelve el stock.

**Cliente**
- Categorías y productos disponibles (solo los que tienen stock).
- Sus propios pedidos con el detalle.
- Sus datos, en solo lectura. La contraseña nunca se muestra.

Todas las bajas son lógicas: los registros se marcan como eliminados y no se borran.

## Estructura

```
main.py                 Punto de entrada: abre la ventana y crea la App
pyproject.toml          Datos del proyecto y dependencias (lo usa flet build)
assets/fonts/           Tipografía Inter
web/                    Versión web ya compilada (es lo que publica Vercel)
vercel.json             Le indica a Vercel que publique web/ sin compilar
.vercelignore           Evita que Vercel suba el código Python
UI/
├── app.py              Navegación entre pantallas y sesión del usuario
├── tema.py             Colores, tipografía y formato de precios
├── datos_demo.py       Datos de ejemplo y reglas de negocio (provisorio)
├── componentes/        Piezas reutilizables: botón, campo, tabla, alerta, modal...
└── vistas/             Una clase por pantalla
    ├── vista_abc.py    Clases base abstractas y los dos menús (admin y cliente)
    ├── login.py
    ├── admin_*.py
    └── cliente.py
```

### Cómo está organizado

- **La interfaz no valida ni guarda datos.** Cada pantalla llama a métodos de un objeto *servicio*. Si algo es inválido, el servicio lanza una excepción propia (`FoodStoreError` o `ErroresValidacion`) y la pantalla la muestra en el campo correspondiente.
- **Las pantallas usan herencia.** Todas heredan de la clase abstracta `Vista`. Las del administrador heredan de `VistaAdmin` (barra lateral) y las del cliente de `VistaCliente` (barra superior), así cada pantalla solo define su contenido.
- **El servicio se puede reemplazar.** `App` recibe el servicio como parámetro, por lo que se puede cambiar `UI/datos_demo.py` por otra implementación con los mismos métodos sin tocar las pantallas:

  ```python
  App(page, servicio=MiServicio())
  ```

## Conceptos aplicados

Clases abstractas, herencia, polimorfismo, encapsulamiento (contraseña privada en `Usuario`), propiedades, enumeraciones, excepciones propias y separación entre interfaz y lógica.
