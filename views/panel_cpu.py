import tkinter as tk
from tkinter import ttk, messagebox

COLORES_ESTADO = {
    "Nuevo": {"bg": "#e9ecef", "fg": "#495057"},
    "Listo": {"bg": "#d3f9d8", "fg": "#2b8a3e"},
    "Ejecutando": {"bg": "#fff3bf", "fg": "#e67700"},
    "Esperando memoria": {"bg": "#ffe3e3", "fg": "#c92a2a"},
    "Finalizado": {"bg": "#d0ebff", "fg": "#1864ab"},
}

def panel_cpu(self, padre):
    marco = ttk.LabelFrame(padre, text="CPU y cola de listos", padding=10)
    marco.pack(side="left", fill="both", expand=True, padx=6)


    self.lbl_tiempo = ttk.Label(marco, text="Tiempo: 0", font=("Arial", 16, "bold"))
    self.lbl_tiempo.pack(anchor="w", pady=(0, 10))


    ttk.Label(marco, text="Proceso ejecutándose:").pack(anchor="w")
    self.lbl_cpu = tk.Label(
        marco,
        text="Ninguno",
        font=("Arial", 20, "bold"),
        fg=COLORES_ESTADO["Nuevo"]["fg"]
    )
    self.lbl_cpu.pack(anchor="w", pady=(3, 15))


    ttk.Label(marco, text="Cola de listos:").pack(anchor="w")
    self.lbl_cola = tk.Label(
        marco,
        text="Vacía",
        font=("Arial", 13, "bold"),
        fg=COLORES_ESTADO["Listo"]["fg"],
        wraplength=300,
        justify="left"
    )
    self.lbl_cola.pack(anchor="w", pady=(3, 15))


    ttk.Label(marco, text="Esperando memoria:").pack(anchor="w")
    self.lbl_espera = tk.Label(
        marco,
        text="Ninguno",
        font=("Arial", 13, "bold"),
        fg=COLORES_ESTADO["Esperando memoria"]["fg"],
        wraplength=300,
        justify="left"
    )
    self.lbl_espera.pack(anchor="w", pady=(3, 15))


    ttk.Label(marco, text="Historial CPU:").pack(anchor="w")
    self.lbl_historial = ttk.Label(
        marco,
        text="Sin ejecución",
        wraplength=300
    )
    self.lbl_historial.pack(anchor="w", pady=(3, 10))