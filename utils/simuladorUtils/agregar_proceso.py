import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from copy import deepcopy

import utils.decoradores as decoradores
from utils.simuladorUtils.actualizar_tabla import actualizar_tabla

def agregar_proceso(self):
    """
    Permite agregar un nuevo proceso al atributo SimuladorSo.procesos (array).
    
    Args:
        self (SimuladorSO): Instancia de la clase SimuladorSO.  
    """
    
    if self.simulacion_activa:
        messagebox.showwarning(
        "Simulación activa",
        "Reinicie la simulación antes de modificar los procesos."
    )
        return


    pid = self.entry_pid.get().strip()


    try:
        rafaga = int(self.entry_rafaga.get())
        memoria = int(self.entry_memoria.get())
    except ValueError:
        messagebox.showerror(
        "Datos inválidos",
        "Ráfaga y memoria deben ser números enteros."
    )
        return


    if not pid:
        messagebox.showerror("Dato faltante", "Debe ingresar un ID.")
        return


    if rafaga <= 0 or memoria <= 0:
        messagebox.showerror(
            "Datos inválidos",
            "Ráfaga y memoria deben ser mayores que cero."
        )
        return


    if any(p.pid == pid for p in self.procesos):
        messagebox.showerror(
            "ID repetido",
            "Ya existe un proceso con ese ID."
        )
        return


    try:
        memoria_total_actual = int(self.entry_mem_total.get())
    except ValueError:
        memoria_total_actual = None


    # Comparo la memoria del proceso con la memoria del sistema.
    if memoria_total_actual is not None and memoria > memoria_total_actual:
        messagebox.showwarning(
            "Memoria insuficiente",
            f"El proceso '{pid}' requiere {memoria} MB, pero la memoria "
            f"total configurada es de {memoria_total_actual} MB.\n\n"
            f"El proceso se cargará igual, pero quedará indefinidamente "
            f"'Esperando memoria' durante la simulación."
        )


    self.procesos.append(decoradores.Proceso(pid, rafaga, memoria)) # Agrego un nuevo objeto Proceso.
    actualizar_tabla(self, self.procesos)

    # Vacío los campos de entrada de datos del panel.
    self.entry_pid.delete(0, tk.END)
    self.entry_rafaga.delete(0, tk.END)
    self.entry_memoria.delete(0, tk.END)
    
    # Coloco el cursor en el campo de entrada de datos 'ID'.
    self.entry_pid.focus()