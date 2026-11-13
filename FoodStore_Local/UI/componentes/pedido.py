"""Detalle de un pedido (lo usan admin y cliente)."""
import flet as ft

from UI.componentes.tabla import tabla
from UI.tema import Tema, pesos, txt


def _derecha(control):
    return ft.Row([control], alignment=ft.MainAxisAlignment.END)


def _centro(control):
    return ft.Row([control], alignment=ft.MainAxisAlignment.CENTER)


def tabla_detalles(pedido) -> ft.Container:
    filas = [
        [d.nombre, _centro(txt(d.cantidad, 15)), _derecha(txt(pesos(d.precio), 15)),
         _derecha(txt(pesos(d.subtotal), 15, 700))]
        for d in pedido.detalles
    ]
    return tabla([("Producto", 5), ("Cant.", 2), ("Precio", 3), ("Subtotal", 3)], filas, alto_fila=64)


def fila_total(monto, tam=44) -> ft.Row:
    return ft.Row([txt("Total", 18, color=Tema.TEXTO_SUAVE), txt(pesos(monto), tam, 800, Tema.PRIMARIO)],
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN)


def dato(etiqueta, valor) -> ft.Column:
    return ft.Column([txt(etiqueta, 14, 600, Tema.TEXTO_SUAVE), txt(valor, 18, 600)], spacing=2)
