import tkinter as tk
from tkinter import ttk, messagebox

def panel_eventos(self, padre):
    """
    Permite visualizar el panel inferior que registra el paso a paso de los procesos.
    
    Args:
        self (SimuladorSO): Instancia de la clase SimuladorSO.
        padre (Frame): Objeto de la clase Frame, la cual permite organizar la disposición de los componentes visuales.   
    """
    
    marco = ttk.LabelFrame(padre, text="Registro paso a paso", padding=8)
    marco.pack(fill="x")
    
    
    self.text_eventos = tk.Text(marco, height=8, wrap="word", font=("Arial", 11))
    self.text_eventos.pack(fill="x")