import tkinter as tk
from tkinter import ttk, messagebox

from utils.agregar_proceso import agregar_proceso

def panel_procesos(self, padre):
    marco = ttk.LabelFrame(padre, text="Carga de procesos", padding=10)
    marco.pack(side="left", fill="x", expand=True, padx=(0, 6))
    
    
    ttk.Label(marco, text="ID").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    ttk.Label(marco, text="Ráfaga CPU").grid(row=0, column=1, sticky="w", padx=5, pady=5)
    ttk.Label(marco, text="Memoria (MB)").grid(row=0, column=2, sticky="w", padx=5, pady=5)
    
    
    self.entry_pid = ttk.Entry(marco, width=15)
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
        command=self.eliminar_proceso
    ).grid(row=2, column=3, padx=8, pady=5)
    
    
    ttk.Label(
        marco,
        text="Ingresar por teclado: ID, ráfaga y memoria requerida."
    ).grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=(8, 0))