""" MODULOS PYTHON  """
import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from copy import deepcopy


""" MODULOS DEL SISTEMA  """
import utils.decoradores as decoradores
import controllers.memoriaController as mc # memoria controller.
from views.pantalla_principal import pantalla_principal
from utils.simuladorUtils.actualizar_estado_quantum import actualizar_estado_quantum
from utils.simuladorUtils.registrar import registrar
from utils.simuladorUtils.actualizar_vistas import actualizar_vistas

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



    def _verificar_fin(self):
        if self.alg_cpu == "Round-Robin":
            quedan_pendientes = bool(self.cola_rr)
        else:
            quedan_pendientes = bool(self.listos)
        quedan_pendientes = (quedan_pendientes
                             or bool(getattr(self, "bloqueados", []))
                             or bool(getattr(self, "espera_pagina", [])))


        if not quedan_pendientes:
            limite = getattr(self.memoria, "tamanio_virtual",
                             self.memoria.tamanio_total)
            imposibles = [
                p for p in self.espera_memoria
                if p.memoria > limite
            ]


            if self.espera_memoria and len(imposibles) != len(self.espera_memoria):
                return


            self.simulacion_activa = False
            self.btn_paso.config(state="disabled")
            self.proceso_actual = None


            if hasattr(self, "btn_cambiar_mem"):
                self.btn_cambiar_mem.config(state="disabled")
            self.auto = False
            if hasattr(self, "btn_auto"):
                try:
                    self.btn_auto.config(text="Auto")
                except Exception:
                    pass


            if self.espera_memoria:
                registrar(
                    self,
                    "La simulacion termino, pero algunos procesos no pudieron "
                    "ingresar porque requieren mas memoria que la disponible."
                )
            else:
                registrar(self, "Todos los procesos finalizaron.")
            
            actualizar_vistas(self)