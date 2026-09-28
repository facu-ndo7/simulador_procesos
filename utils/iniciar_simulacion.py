import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from copy import deepcopy

import controllers.memoriaController as mc # memoria controller.
from utils.actualizar_vistas import actualizar_vistas
from utils.registrar import registrar

def iniciar_simulacion(self):
    if not self.procesos:
        messagebox.showwarning(
            "Sin procesos",
            "Debe cargar al menos un proceso."
        )
        return


    try:
        tamanio_memoria = int(self.entry_mem_total.get())
    except ValueError:
        messagebox.showerror(
            "Memoria inválida",
            "El tamaño de memoria debe ser un número entero."
        )
        return


    if tamanio_memoria <= 0:
        messagebox.showerror(
            "Memoria inválida",
            "La memoria total debe ser mayor que cero."
        )
        return


    self.alg_cpu = self.combo_cpu.get()
    self.alg_mem = self.combo_mem.get()


    if self.alg_cpu == "Round-Robin":
        try:
            self.quantum = int(self.entry_quantum.get())
        except ValueError:
            messagebox.showerror(
                "Quantum inválido",
                "El quantum debe ser un número entero."
            )
            return


    if self.quantum <= 0:
        messagebox.showerror(
            "Quantum inválido",
            "El quantum debe ser mayor que cero."
        )
        return


    self.procesos_sim = deepcopy(self.procesos)
    self.memoria = mc(tamanio_memoria)


    self.listos = []
    self.espera_memoria = []
    self.cola_rr = deque()


    self.tiempo = 0
    self.proceso_actual = None
    self.historial_cpu = []


    self.text_eventos.delete("1.0", tk.END)
    
    registrar(
        self,
        f"Se inicia la simulación. CPU: {self.alg_cpu}. "
        f"Memoria: {self.alg_mem}. Memoria total: {tamanio_memoria} MB."
    )
    
    
    for p in self.procesos_sim:
        if p.memoria > tamanio_memoria:
            p.estado = "Esperando memoria"
            self.espera_memoria.append(p)
            registrar(
                self,
                f"{p.pid} requiere {p.memoria} MB y no puede ingresar "
                f"porque supera la memoria total."
            )
        elif self.memoria.asignar(p, self.alg_mem):
            self.listos.append(p)
            registrar(
                self,
                f"{p.pid} fue asignado a memoria mediante {self.alg_mem}."
            )
        else:
            p.estado = "Esperando memoria"
            self.espera_memoria.append(p)
            registrar(
                self,
                f"{p.pid} queda esperando memoria."
            )
    
    
        if self.alg_cpu == "SJF no apropiativo":
            self.listos.sort(key=lambda p: p.rafaga)
    
    
        if self.alg_cpu == "Round-Robin":
            self.cola_rr = deque(self.listos)
    
    
        self.simulacion_activa = True
        self.btn_paso.config(state="normal")
        actualizar_vistas(self)