import tkinter as tk
from tkinter import ttk, messagebox

from views.panel_procesos import panel_procesos
from views.panel_configuracion import panel_configuracion
from views.panel_eventos import panel_eventos
from views.tabla import crear_tabla
from views.panel_cpu import panel_cpu
from views.panel_memoria import panel_memoria

def pantalla_principal(self):
    self.title("Simulador de CPU y Memoria - Sistemas Operativos")
    self.geometry("1280x840")
    self.minsize(1050, 680)
    
    
    self.option_add("*Font", ("Arial", 12))
    
    
    estilo = ttk.Style(self)
    estilo.configure("TLabel", font=("Arial", 12))
    estilo.configure("TButton", font=("Arial", 12))
    estilo.configure("TEntry", font=("Arial", 12))
    estilo.configure("TCombobox", font=("Arial", 12))
    estilo.configure("TLabelframe.Label", font=("Arial", 13, "bold"))
    estilo.configure("Treeview", font=("Arial", 11), rowheight=26)
    estilo.configure("Treeview.Heading", font=("Arial", 13, "bold"))
    
    contenedor = ttk.Frame(self, padding=12)
    contenedor.pack(fill="both", expand=True)
    
    
    # Panel superior
    superior = ttk.Frame(contenedor)
    superior.pack(side="top", fill="x", pady=(0, 10))
    panel_procesos(self, superior)
    panel_configuracion(self, superior)
    
    
    # Panel inferior
    inferior = ttk.Frame(contenedor)
    inferior.pack(side="bottom", fill="x", pady=(10, 0))
    panel_eventos(self, inferior)
    
    
    # Panel central?
    central = ttk.Frame(contenedor)
    central.pack(side="top", fill="both", expand=True)
    
    crear_tabla(self, central)
    
    panel_cpu(self, central)
    
    panel_memoria(self, central)