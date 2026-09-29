import tkinter as tk
from tkinter import ttk, messagebox

from utils.simuladorUtils.agregar_proceso import agregar_proceso
from utils.simuladorUtils.eliminar_proceso import eliminar_proceso

def panel_procesos(self, padre):
    """
    Permite visualizar el panel superior para agregar procesos.
    
    Args:
        self (SimuladorSO): Instancia de la clase SimuladorSO.
        padre (Frame): Objeto de la clase Frame, la cual permite organizar la disposición de los componentes visuales.   
    """
    
    marco = ttk.LabelFrame(padre, text="Carga de procesos", padding=10)
    marco.pack(side="left", fill="x", expand=True, padx=(0, 6))
    
    
    ttk.Label(marco, text="ID").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    ttk.Label(marco, text="Ráfaga CPU").grid(row=0, column=1, sticky="w", padx=5, pady=5)
    ttk.Label(marco, text="Memoria (MB)").grid(row=0, column=2, sticky="w", padx=5, pady=5)


    self.var_proximo_pid = tk.StringVar(value=str(getattr(self, 'proximo_pid', 1)))
    self.entry_pid = ttk.Entry(marco, width=15, state="readonly",
                               textvariable=self.var_proximo_pid)
    self.entry_rafaga = ttk.Entry(marco, width=15)
    self.entry_memoria = ttk.Entry(marco, width=15)
    
    
    self.entry_pid.grid(row=1, column=0, padx=5, pady=5)
    self.entry_rafaga.grid(row=1, column=1, padx=5, pady=5)
    self.entry_memoria.grid(row=1, column=2, padx=5, pady=5)
    
    
    ttk.Button(
        marco,
        text="Agregar proceso",
        command= lambda: agregar_proceso(self) # Con el comando lambda la función solo se ejecuta al hacer click en el botón.
    ).grid(row=1, column=3, padx=8, pady=5)
    
    
    ttk.Button(
        marco,
        text="Eliminar seleccionado",
        command= lambda: eliminar_proceso(self)
    ).grid(row=2, column=3, padx=8, pady=5)
    
    
    ttk.Label(
        marco,
        text="Ingrese ráfaga y memoria requerida."
    ).grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=(8, 0))