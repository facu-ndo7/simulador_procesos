import tkinter as tk
from tkinter import ttk, messagebox

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
