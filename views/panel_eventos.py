import tkinter as tk
from tkinter import ttk

def panel_eventos(self, padre):
    """
    Permite visualizar el panel inferior que registra el paso a paso de los procesos.
    
    Args:
        self (SimuladorSO): Instancia de la clase SimuladorSO.
        padre (Frame): Objeto de la clase Frame, la cual permite organizar la disposición de los componentes visuales.   
    """
    
    marco = ttk.LabelFrame(padre, text="Registro paso a paso", padding=8)
    marco.pack(fill="x")
    # Altura contenida + scrollbar: el registro crece hacia abajo sin
    # empujar al resto del layout fuera de la ventana.
    cuerpo = ttk.Frame(marco)
    cuerpo.pack(fill="x", expand=True)

    scroll = ttk.Scrollbar(cuerpo, orient="vertical")
    scroll.pack(side="right", fill="y")

    self.text_eventos = tk.Text(cuerpo, height=6, wrap="word",
                                font=("Arial", 11),
                                yscrollcommand=scroll.set)
    self.text_eventos.pack(side="left", fill="both", expand=True)
    scroll.config(command=self.text_eventos.yview)