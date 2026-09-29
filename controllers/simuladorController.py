""" MODULOS PYTHON  """
import tkinter as tk
from collections import deque


""" MODULOS DEL SISTEMA  """
from views.pantalla_principal import pantalla_principal
from utils.simuladorUtils.actualizar_estado_quantum import actualizar_estado_quantum

COLORES_ESTADO = {
    "Nuevo": {"bg": "#e9ecef", "fg": "#495057"},
    "Listo": {"bg": "#d3f9d8", "fg": "#2b8a3e"},
    "Ejecutando": {"bg": "#fff3bf", "fg": "#e67700"},
    "Esperando memoria": {"bg": "#ffe3e3", "fg": "#c92a2a"},
    "Bloqueado": {"bg": "#e5dbff", "fg": "#5f3dc4"},
    "Esperando página": {"bg": "#ffe8cc", "fg": "#d9480f"},
    "Terminado": {"bg": "#d0ebff", "fg": "#1864ab"},
}

class SimuladorSO(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.procesos = []
        self.procesos_sim = []
        self.proximo_pid = 1
        self.memoria = None
        self.listos = []
        self.espera_memoria = []
        self.bloqueados = []
        self.espera_pagina = []
        self.cola_rr = deque()


        self.tiempo = 0
        self.tiempo_cpu = 0
        self.cambios_contexto = 0
        self.auto = False
        self.proceso_actual = None
        self.simulacion_activa = False
        self.alg_cpu = ""
        self.alg_mem = ""
        self.modo_mem = "Asignación contigua"
        self.ajuste_mem = "First-Fit"
        self.tam_pagina = 8
        self.tam_virtual = 400
        self.reemplazo = "LRU"
        self.quantum = 0
        self.historial_cpu = []


        pantalla_principal(self)
        actualizar_estado_quantum(self)