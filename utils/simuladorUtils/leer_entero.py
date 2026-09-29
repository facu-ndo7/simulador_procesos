"""Lectura unificada de enteros desde widgets Tkinter."""
from tkinter import messagebox


def _raw_de_widget(widget):
    try:
        return widget.get().strip()
    except Exception:
        return ""


def leer_entero(self, widget, nombre, obligatorio=False, defecto=None):
    """Variante estricta: valida y muestra messagebox ante dato inválido."""
    raw = _raw_de_widget(widget)
    if not raw:
        if obligatorio:
            messagebox.showerror(
                "Dato inválido",
                f"{nombre} debe ser un número entero mayor que cero."
            )
            return None
        return defecto
    try:
        valor = int(raw)
    except ValueError:
        messagebox.showerror(
            "Dato inválido",
            f"{nombre} debe ser un número entero."
        )
        return None
    if valor <= 0:
        messagebox.showerror(
            "Dato inválido",
            f"{nombre} debe ser mayor que cero."
        )
        return None
    return valor


def leer_entero_optimo(self, nombre_attr, defecto):
    """Variante silenciosa: no muestra messagebox; None si no parsea."""
    if not hasattr(self, nombre_attr):
        return defecto
    try:
        raw = getattr(self, nombre_attr).get().strip()
    except Exception:
        return defecto
    if not raw:
        return defecto
    try:
        return int(raw)
    except ValueError:
        return None


def leer_tam_pagina(self, obligatorio=False):
    if hasattr(self, "entry_tam_pagina"):
        return leer_entero(self, self.entry_tam_pagina, "El tamaño de página",
                           obligatorio=obligatorio, defecto=8)
    return 8
