import tkinter as tk
from tkinter import ttk, messagebox

from utils.simuladorUtils.bloqueo_es import solicitar_es, fin_es

COLORES_ESTADO = {
    "Nuevo": {"bg": "#e9ecef", "fg": "#495057"},
    "Listo": {"bg": "#d3f9d8", "fg": "#2b8a3e"},
    "Ejecutando": {"bg": "#fff3bf", "fg": "#e67700"},
    "Esperando memoria": {"bg": "#ffe3e3", "fg": "#c92a2a"},
    "Bloqueado": {"bg": "#e5dbff", "fg": "#5f3dc4"},
    "Esperando página": {"bg": "#ffe8cc", "fg": "#d9480f"},
    "Terminado": {"bg": "#d0ebff", "fg": "#1864ab"},
}

def panel_cpu(self, padre):
    """
    Permite visualizar el panel central medio que hace seguimiento a los procesos ejecutandose.
    
    Args:
        self (SimuladorSO): Instancia de la clase SimuladorSO.
        padre (Frame): Objeto de la clase Frame, la cual permite organizar la disposición de los componentes visuales.   
    """
    marco = ttk.LabelFrame(padre, text="CPU y cola de listos", padding=10)
    marco.pack(side="left", fill="both", expand=True, padx=6)


    self.lbl_tiempo = ttk.Label(marco, text="Tiempo: 0", font=("Arial", 16, "bold"))
    self.lbl_tiempo.pack(anchor="w", pady=(0, 10))


    self.lbl_uso_cpu = ttk.Label(marco, text="Uso CPU: —")
    self.lbl_uso_cpu.pack(anchor="w", pady=(0, 10))


    self.lbl_contexto = ttk.Label(marco, text="Cambios de contexto: 0")
    self.lbl_contexto.pack(anchor="w", pady=(0, 10))


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


    ttk.Label(marco, text="Cola de nuevos:").pack(anchor="w")
    self.lbl_nuevos = tk.Label(
        marco,
        text="Ninguno",
        font=("Arial", 13, "bold"),
        fg=COLORES_ESTADO["Nuevo"]["fg"],
        wraplength=300,
        justify="left"
    )
    self.lbl_nuevos.pack(anchor="w", pady=(3, 15))


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


    ttk.Label(marco, text="Bloqueados (E/S):").pack(anchor="w")
    self.lbl_bloqueados = tk.Label(
        marco,
        text="Ninguno",
        font=("Arial", 13, "bold"),
        fg=COLORES_ESTADO["Bloqueado"]["fg"],
        wraplength=300,
        justify="left"
    )
    self.lbl_bloqueados.pack(anchor="w", pady=(3, 8))


    ttk.Label(marco, text="Esperando página:").pack(anchor="w")
    self.lbl_espera_pagina = tk.Label(
        marco,
        text="Ninguno",
        font=("Arial", 13, "bold"),
        fg=COLORES_ESTADO["Esperando página"]["fg"],
        wraplength=300,
        justify="left"
    )
    self.lbl_espera_pagina.pack(anchor="w", pady=(3, 8))


    fila_es = ttk.Frame(marco)
    fila_es.pack(anchor="w", pady=(0, 10))
    ttk.Button(fila_es, text="Solicitar E/S",
               command=lambda: solicitar_es(self)).pack(side="left", padx=(0, 6))
    ttk.Button(fila_es, text="Fin E/S",
               command=lambda: fin_es(self)).pack(side="left")


    ttk.Label(marco, text="Historial CPU:").pack(anchor="w")
    self.lbl_historial = ttk.Label(
        marco,
        text="Sin ejecución",
        wraplength=300
    )
    self.lbl_historial.pack(anchor="w", pady=(3, 10))