"""Comparativa Paginación vs Segmentación vs Segmentación paginada (req. 5)."""
from copy import deepcopy
from tkinter import ttk, messagebox
import tkinter as tk

import controllers.memoriaController as mc
from utils.simuladorUtils.registrar import registrar


def calcular_comparativa(procesos, tamanio_total, tam_pagina=8,
                         ajuste="First-Fit"):
    """Instancia los 3 esquemas en igualdad de condiciones y los compara.

    No muta la lista original (trabaja sobre copias). Devuelve una fila
    por esquema: {"esquema", "admitidos", "total", "ocupacion",
    "frag_interna", "frag_externa", "estructura"}.
    """
    base = deepcopy(list(procesos or []))
    filas = []

    g_pag = mc.crear_gestor("Paginación", tamanio_total, tam_pagina=tam_pagina)
    adm = [p for p in deepcopy(base) if g_pag.asignar(p)]
    filas.append({
        "esquema": g_pag.nombre,
        "admitidos": len(adm), "total": len(base),
        "ocupacion": (f"{sum(1 for m in g_pag.marcos if m is not None)}"
                      f"/{g_pag.num_marcos} marcos"),
        "frag_interna": g_pag.fragmentacion_interna(),
        "frag_externa": g_pag.fragmentacion_externa(),
        "estructura": (f"{sum(len(g_pag.tabla_paginas[p.pid]) for p in adm)} "
                       "páginas en tablas"),
    })

    g_seg = mc.crear_gestor("Segmentación", tamanio_total, ajuste=ajuste)
    adm = [p for p in deepcopy(base) if g_seg.asignar(p)]
    filas.append({
        "esquema": g_seg.nombre,
        "admitidos": len(adm), "total": len(base),
        "ocupacion": (f"{sum(1 for b in g_seg.bloques if not b.libre)} "
                      "segmentos residentes"),
        "frag_interna": 0,
        "frag_externa": g_seg.fragmentacion_externa(),
        "estructura": (f"{sum(len(g_seg.tabla_segmentos[p.pid]) for p in adm)} "
                       "segmentos en tablas"),
    })

    g_sp = mc.crear_gestor("Segmentación paginada", tamanio_total,
                           tam_pagina=tam_pagina)
    adm = [p for p in deepcopy(base) if g_sp.asignar(p)]
    filas.append({
        "esquema": g_sp.nombre,
        "admitidos": len(adm), "total": len(base),
        "ocupacion": (f"{sum(1 for m in g_sp.marcos if m is not None)}"
                      f"/{g_sp.num_marcos} marcos"),
        "frag_interna": g_sp.fragmentacion_interna(),
        "frag_externa": g_sp.fragmentacion_externa(),
        "estructura": (f"{sum(len(g_sp.tabla[p.pid]) for p in adm)} segs / "
                       f"{sum(len(e.tabla_paginas) for p in adm for e in g_sp.tabla[p.pid])} págs"),
    })
    return filas


def comparar_esquemas(self):
    """Muestra la comparativa en ventana + registro de eventos."""
    fuente = list(getattr(self, "procesos_sim", []) or getattr(self, "procesos", []) or [])
    if not fuente:
        messagebox.showwarning("Sin procesos", "Cargue procesos para comparar.")
        return
    try:
        total = int(self.entry_mem_total.get().strip())
        pagina = int(self.entry_tam_pagina.get().strip() or "8")
    except (AttributeError, ValueError):
        messagebox.showerror("Dato inválido",
                             "Memoria total y página deben ser enteros.")
        return
    ajuste = self.combo_ajuste_mem.get() if hasattr(self, "combo_ajuste_mem") else "First-Fit"
    try:
        filas = calcular_comparativa(fuente, total, pagina, ajuste)
    except ValueError as e:
        messagebox.showerror("Comparativa inválida", str(e))
        return

    for f in filas:
        try:
            registrar(
                self,
                f"Comparativa {f['esquema']}: {f['admitidos']}/{f['total']} "
                f"admitidos, ocupación {f['ocupacion']}, "
                f"frag. interna {f['frag_interna']} MB, "
                f"frag. externa {f['frag_externa']} MB ({f['estructura']}).")
        except Exception:
            pass

    try:
        ventana = tk.Toplevel(self)
    except Exception:
        return
    ventana.title("Comparativa de esquemas de memoria")
    columnas = ("esquema", "admitidos", "ocupacion", "frag_int",
                "frag_ext", "estructura")
    tree = ttk.Treeview(ventana, columns=columnas, show="headings", height=3)
    for col, ancho, texto in (("esquema", 240, "Esquema"),
                              ("admitidos", 100, "Admitidos"),
                              ("ocupacion", 170, "Ocupación física"),
                              ("frag_int", 110, "Frag. interna"),
                              ("frag_ext", 110, "Frag. externa"),
                              ("estructura", 260, "Estructura")):
        tree.heading(col, text=texto)
        tree.column(col, anchor="center", width=ancho)
    for f in filas:
        tree.insert("", tk.END, values=(
            f["esquema"], f"{f['admitidos']}/{f['total']}", f["ocupacion"],
            f"{f['frag_interna']} MB", f"{f['frag_externa']} MB",
            f["estructura"]))
    tree.pack(fill="both", expand=True, padx=10, pady=10)
