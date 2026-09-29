import tkinter as tk
from tkinter import ttk

from utils.simuladorUtils.traducir_direccion import traducir_direccion

def panel_memoria(self, padre):
    """
    Permite visualizar el panel central derecho que hace seguimiento a la memoria principal.
    
    Args:
        self (SimuladorSO): Instancia de la clase SimuladorSO.
        padre (Frame): Objeto de la clase Frame, la cual permite organizar la disposición de los componentes visuales.   
    """
    marco = ttk.LabelFrame(padre, text="Memoria principal", padding=8)
    marco.pack(side="left", fill="both", expand=True, padx=(6, 0))


    self.canvas_memoria = tk.Canvas(
        marco,
        width=320,
        height=370,
        bg="white",
        highlightthickness=1,
        highlightbackground="#999"
    )
        
    self.canvas_memoria.pack(fill="both", expand=True)


    self.lbl_memoria_info = ttk.Label(
        marco,
        text="Memoria no inicializada",
        justify="left"
    )
    
    self.lbl_memoria_info.pack(anchor="w", pady=(8, 0))


    ttk.Label(marco, text="Tablas páginas/segmentos (tiempo real)").pack(anchor="w", pady=(8, 0))
    columnas = ("proceso", "pagina", "marco", "detalle")
    self.tabla_paginas_view = ttk.Treeview(
        marco, columns=columnas, show="headings", height=5
    )
    for col, ancho, texto in (("proceso", 90, "Proceso"),
                              ("pagina", 70, "Página"),
                              ("marco", 70, "Marco"),
                              ("detalle", 150, "Detalle")):
        self.tabla_paginas_view.heading(col, text=texto)
        self.tabla_paginas_view.column(col, anchor="center", width=ancho)
    self.tabla_paginas_view.pack(fill="x")


    trad = ttk.Frame(marco)
    trad.pack(fill="x", pady=(6, 0))
    ttk.Label(trad, text="PID").pack(side="left", padx=(0, 4))
    self.entry_trad_pid = ttk.Entry(trad, width=8)
    self.entry_trad_pid.pack(side="left", padx=(0, 8))
    ttk.Label(trad, text="Seg").pack(side="left", padx=(0, 4))
    self.entry_trad_seg = ttk.Entry(trad, width=5)
    self.entry_trad_seg.pack(side="left", padx=(0, 8))
    ttk.Label(trad, text="Dir/Desp").pack(side="left", padx=(0, 4))
    self.entry_trad_dir = ttk.Entry(trad, width=8)
    self.entry_trad_dir.pack(side="left", padx=(0, 8))
    ttk.Button(trad, text="Traducir",
               command=lambda: traducir_direccion(self)).pack(side="left")
    self.lbl_traduccion = ttk.Label(marco, text="", wraplength=340,
                                    justify="left")
    self.lbl_traduccion.pack(anchor="w")
