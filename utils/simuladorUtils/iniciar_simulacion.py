import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from copy import deepcopy

import controllers.memoriaController as mc # memoria controller.
from utils.simuladorUtils.actualizar_vistas import actualizar_vistas
from utils.simuladorUtils.registrar import registrar

def _leer_entero(self, widget, nombre, obligatorio=False, defecto=None):
    raw = ""
    try:
        raw = widget.get().strip()
    except Exception:
        raw = ""
    if not raw:
        if obligatorio:
            messagebox.showerror(
                "Dato inválido",
                f"{nombre} debe ser un número entero mayor que cero."
            )
            return None
        return defecto
    try:
        valor = int(raw)
    except ValueError:
        messagebox.showerror(
            "Dato inválido",
            f"{nombre} debe ser un número entero."
        )
        return None
    if valor <= 0:
        messagebox.showerror(
            "Dato inválido",
            f"{nombre} debe ser mayor que cero."
        )
        return None
    return valor

def _leer_tam_pagina(self, obligatorio=False):
    if hasattr(self, "entry_tam_pagina"):
        return _leer_entero(self, self.entry_tam_pagina, "El tamaño de página",
                            obligatorio=obligatorio, defecto=8)
    return 8

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
    # Nuevo modelo: modo de gestión + ajuste + tamaño de página.
    # Se mantiene compatibilidad con el combo viejo (First/Best/Worst-Fit).
    if hasattr(self, "combo_modo_mem"):
        modo = self.combo_modo_mem.get()
    else:
        modo = self.combo_mem.get()
    if hasattr(self, "combo_ajuste_mem"):
        ajuste = self.combo_ajuste_mem.get() or "First-Fit"
    elif modo in ("First-Fit", "Best-Fit", "Worst-Fit"):
        ajuste = modo
    else:
        ajuste = getattr(self, "ajuste_mem", "First-Fit") or "First-Fit"

    modo_norm = mc.normalizar_modo(modo)
    necesita_pagina = modo_norm in ("Paginación", "Segmentación paginada",
                                    "Memoria virtual")
    tam_pagina = _leer_tam_pagina(self, obligatorio=necesita_pagina)
    if tam_pagina is None:
        return
    if tam_pagina > tamanio_memoria:
        messagebox.showerror(
            "Página inválida",
            "El tamaño de página no puede superar la memoria total."
        )
        return

    # Parámetros propios de memoria virtual.
    tamanio_virtual = None
    reemplazo = getattr(self, "reemplazo", "LRU")
    if modo_norm == "Memoria virtual":
        if hasattr(self, "combo_reemplazo"):
            reemplazo = self.combo_reemplazo.get() or "LRU"
        if hasattr(self, "entry_mem_virtual"):
            tamanio_virtual = _leer_entero(
                self, self.entry_mem_virtual, "La memoria virtual",
                obligatorio=False, defecto=tamanio_memoria * 4)
            if tamanio_virtual is None:
                return
        else:
            tamanio_virtual = tamanio_memoria * 4
        if tamanio_virtual < tamanio_memoria:
            messagebox.showerror(
                "Memoria inválida",
                "La memoria virtual debe ser mayor o igual que la física."
            )
            return


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
    try:
        self.memoria = mc.crear_gestor(
            modo_norm, tamanio_memoria, ajuste=ajuste, tam_pagina=tam_pagina,
            tamanio_virtual=tamanio_virtual, reemplazo=reemplazo,
        )
    except ValueError as e:
        messagebox.showerror("Memoria inválida", str(e))
        return
    # Estado del gestor actual (permite el cambio en caliente).
    self.modo_mem = modo_norm
    self.ajuste_mem = ajuste
    self.tam_pagina = tam_pagina
    self.tam_virtual = getattr(self.memoria, "tamanio_virtual", tamanio_memoria)
    self.reemplazo = getattr(self.memoria, "reemplazo", reemplazo)
    # Compatibilidad: alg_mem ahora es el nombre descriptivo del gestor.
    self.alg_mem = self.memoria.nombre


    self.listos = []
    self.espera_memoria = []
    self.bloqueados = []
    self.espera_pagina = []
    self.cola_rr = deque()


    self.tiempo = 0
    self.tiempo_cpu = 0
    self.cambios_contexto = 0
    self.proceso_actual = None
    self.historial_cpu = []


    self.text_eventos.delete("1.0", tk.END)
    
    registrar(
        self,
        f"Se inicia la simulación. CPU: {self.alg_cpu}. "
        f"Memoria: {self.memoria.nombre}. Memoria total: {tamanio_memoria} MB."
    )
    if modo_norm == "Memoria virtual":
        registrar(
            self,
            "Carga bajo demanda: solo la página 0 ingresa a física, "
            "el resto queda en swap hasta su primer acceso."
        )
    
    
    limite = getattr(self.memoria, "tamanio_virtual", tamanio_memoria)
    for p in self.procesos_sim:
        if p.memoria > limite:
            p.estado = "Esperando memoria"
            self.espera_memoria.append(p)
            registrar(
                self,
                f"{p.pid} requiere {p.memoria} MB y no puede ingresar "
                f"porque supera la memoria virtual ({limite} MB)."
            )
        elif self.memoria.asignar(p):
            self.listos.append(p)
            registrar(
                self,
                f"{p.pid} fue asignado a memoria mediante {self.memoria.nombre}."
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
    # El modo puede cambiarse en caliente sin reiniciar.
    if hasattr(self, "btn_cambiar_mem"):
        self.btn_cambiar_mem.config(state="normal")
    self.auto = False
    if hasattr(self, "btn_auto"):
        try:
            self.btn_auto.config(state="normal", text="Auto")
        except Exception:
            pass
    actualizar_vistas(self)
