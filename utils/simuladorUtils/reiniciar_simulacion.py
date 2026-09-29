import tkinter as tk
from collections import deque

from utils.simuladorUtils.actualizar_vistas import actualizar_vistas
from utils.simuladorUtils.actualizar_tabla import actualizar_tabla

def reiniciar_simulacion(self):
    self.simulacion_activa = False
    self.memoria = None
    self.procesos_sim = []
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
    self.historial_cpu = []
    self.btn_paso.config(state="disabled")
    if hasattr(self, "btn_auto"):
        try:
            self.btn_auto.config(state="disabled", text="Auto")
        except Exception:
            pass
    if hasattr(self, "btn_cambiar_mem"):
        self.btn_cambiar_mem.config(state="disabled")
    self.text_eventos.delete("1.0", tk.END)
    actualizar_tabla(self, self.procesos)
    actualizar_vistas(self)