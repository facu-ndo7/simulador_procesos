import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from copy import deepcopy

from utils.simuladorUtils.actualizar_tabla import actualizar_tabla

def eliminar_proceso(self):
    """
    Permite eliminar un proceso registrado.
    
    Args:
        self (SimuladorSO): Instancia de la clase SimuladorSO.
    """
    
    if self.simulacion_activa:
        messagebox.showwarning(
            "Simulación activa",
            "Reinicie la simulación antes de eliminar procesos."
        )
        return


    seleccion = self.tabla.selection()
    if not seleccion:
        messagebox.showinfo(
            "Sin selección",
            "Seleccione en la tabla el proceso a eliminar."
        )
        return


    pids = set()
    for iid in seleccion:
        valores = self.tabla.item(iid)["values"]
        if valores:
            pids.add(str(valores[0]).strip())
    if not pids:
        return
    # Comparación como texto: el Treeview puede devolver el ID como str
    # aunque el Proceso lo guarde como int (o viceversa con datos legacy).
    self.procesos = [p for p in self.procesos if str(p.pid).strip() not in pids]
    actualizar_tabla(self, self.procesos)