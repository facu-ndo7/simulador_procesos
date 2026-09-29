""" MODULOS PYTHON  """
import tkinter as tk
from collections import deque


""" MODULOS DEL SISTEMA  """
from views.pantalla_principal import pantalla_principal
from utils.simuladorUtils.actualizar_estado_quantum import actualizar_estado_quantum

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