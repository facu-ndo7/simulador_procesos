import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from copy import deepcopy

from utils.actualizar_vistas import actualizar_vistas
from utils.actualizar_tabla import actualizar_tabla

def reiniciar_simulacion(self):
    self.simulacion_activa = False
    self.memoria = None
    self.procesos_sim = []
    self.listos = []
    self.espera_memoria = []
    self.cola_rr = deque()
    self.tiempo = 0
    self.proceso_actual = None
    self.historial_cpu = []
    self.btn_paso.config(state="disabled")
    self.text_eventos.delete("1.0", tk.END)
    actualizar_tabla(self, self.procesos)
    actualizar_vistas(self)