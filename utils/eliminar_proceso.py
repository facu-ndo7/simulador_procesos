import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from copy import deepcopy

from utils.actualizar_tabla import actualizar_tabla

def eliminar_proceso(self):  
    if self.simulacion_activa:
        messagebox.showwarning(
            "Simulación activa",
            "Reinicie la simulación antes de eliminar procesos."
        )
        return


    seleccion = self.tabla.selection()
    if not seleccion: return


    item = self.tabla.item(seleccion[0])
    pid = item["values"][0]
    self.procesos = [p for p in self.procesos if p.pid != pid]
    actualizar_tabla(self, self.procesos)