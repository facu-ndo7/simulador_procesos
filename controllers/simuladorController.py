""" MODULOS PYTHON  """
import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from copy import deepcopy


""" MODULOS DEL SISTEMA  """
import utils.decoradores as decoradores
import controllers.memoriaController as mc # memoria controller.
from views.pantalla_principal import pantalla_principal


COLORES_ESTADO = {
    "Nuevo": {"bg": "#e9ecef", "fg": "#495057"},
    "Listo": {"bg": "#d3f9d8", "fg": "#2b8a3e"},
    "Ejecutando": {"bg": "#fff3bf", "fg": "#e67700"},
    "Esperando memoria": {"bg": "#ffe3e3", "fg": "#c92a2a"},
    "Finalizado": {"bg": "#d0ebff", "fg": "#1864ab"},
}

class SimuladorSO(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.procesos = []
        self.procesos_sim = []
        self.memoria = None
        self.listos = []
        self.espera_memoria = []
        self.cola_rr = deque()


        self.tiempo = 0
        self.proceso_actual = None
        self.simulacion_activa = False
        self.alg_cpu = ""
        self.alg_mem = ""
        self.quantum = 0
        self.historial_cpu = []


        pantalla_principal(self)
        #self._actualizar_estado_quantum()

    def agregar_proceso(self):
        if self.simulacion_activa:
            messagebox.showwarning(
                "Simulación activa",
                "Reinicie la simulación antes de modificar los procesos."
            )
            return


        pid = self.entry_pid.get().strip()


        try:
            rafaga = int(self.entry_rafaga.get())
            memoria = int(self.entry_memoria.get())
        except ValueError:
            messagebox.showerror(
                "Datos inválidos",
                "Ráfaga y memoria deben ser números enteros."
            )
            return


        if not pid:
            messagebox.showerror("Dato faltante", "Debe ingresar un ID.")
            return


        if rafaga <= 0 or memoria <= 0:
            messagebox.showerror(
                "Datos inválidos",
                "Ráfaga y memoria deben ser mayores que cero."
            )
            return


        if any(p.pid == pid for p in self.procesos):
            messagebox.showerror(
                "ID repetido",
                "Ya existe un proceso con ese ID."
            )
            return


        try:
            memoria_total_actual = int(self.entry_mem_total.get())
        except ValueError:
            memoria_total_actual = None


        if memoria_total_actual is not None and memoria > memoria_total_actual:
            messagebox.showwarning(
                "Memoria insuficiente",
                f"El proceso '{pid}' requiere {memoria} MB, pero la memoria "
                f"total configurada es de {memoria_total_actual} MB.\n\n"
                f"El proceso se cargará igual, pero quedará indefinidamente "
                f"'Esperando memoria' durante la simulación."
            )


        self.procesos.append(decoradores.Proceso(pid, rafaga, memoria))
        self._actualizar_tabla(self.procesos)


        self.entry_pid.delete(0, tk.END)
        self.entry_rafaga.delete(0, tk.END)
        self.entry_memoria.delete(0, tk.END)
        self.entry_pid.focus()


    def eliminar_proceso(self):
        if self.simulacion_activa:
            messagebox.showwarning(
                "Simulación activa",
                "Reinicie la simulación antes de eliminar procesos."
            )
            return


        seleccion = self.tabla.selection()
        if not seleccion:
            return


        item = self.tabla.item(seleccion[0])
        pid = item["values"][0]
        self.procesos = [p for p in self.procesos if p.pid != pid]
        self._actualizar_tabla(self.procesos)


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


        self._registrar(
            f"Se inicia la simulación. CPU: {self.alg_cpu}. "
            f"Memoria: {self.alg_mem}. Memoria total: {tamanio_memoria} MB."
        )


        for p in self.procesos_sim:
            if p.memoria > tamanio_memoria:
                p.estado = "Esperando memoria"
                self.espera_memoria.append(p)
                self._registrar(
                    f"{p.pid} requiere {p.memoria} MB y no puede ingresar "
                    f"porque supera la memoria total."
                )
            elif self.memoria.asignar(p, self.alg_mem):
                self.listos.append(p)
                self._registrar(
                    f"{p.pid} fue asignado a memoria mediante {self.alg_mem}."
                )
            else:
                p.estado = "Esperando memoria"
                self.espera_memoria.append(p)
                self._registrar(
                    f"{p.pid} queda esperando memoria."
                )


        if self.alg_cpu == "SJF no apropiativo":
            self.listos.sort(key=lambda p: p.rafaga)


        if self.alg_cpu == "Round-Robin":
            self.cola_rr = deque(self.listos)


        self.simulacion_activa = True
        self.btn_paso.config(state="normal")
        self._actualizar_vistas()


    def paso_siguiente(self):
        if not self.simulacion_activa:
            return


        if self.alg_cpu == "FIFO":
            self._paso_fifo()
        elif self.alg_cpu == "SJF no apropiativo":
            self._paso_sjf()
        else:
            self._paso_round_robin()


        self._actualizar_vistas()
        self._verificar_fin()


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
        self._actualizar_tabla(self.procesos)
        self._actualizar_vistas()


    def limpiar_todo(self):
        self.reiniciar_simulacion()
        self.procesos = []
        self._actualizar_tabla(self.procesos)


    def _paso_fifo(self):
        if not self.listos:
            return


        p = self.listos.pop(0)
        p.estado = "Ejecutando"
        self.proceso_actual = p
        inicio = self.tiempo


        self._registrar(
            f"FIFO selecciona {p.pid}, el primer proceso de la cola."
        )


        self.tiempo += p.restante
        p.restante = 0
        p.estado = "Finalizado"


        self.historial_cpu.append((p.pid, inicio, self.tiempo))
        self._registrar(
            f"{p.pid} ejecuta hasta finalizar en el tiempo {self.tiempo}."
        )


        self._finalizar_proceso(p)


    def _paso_sjf(self):
        if not self.listos:
            return


        p = min(self.listos, key=lambda x: x.rafaga)
        self.listos.remove(p)


        p.estado = "Ejecutando"
        self.proceso_actual = p
        inicio = self.tiempo


        self._registrar(
            f"SJF selecciona {p.pid} porque tiene la ráfaga más corta "
            f"entre los procesos listos ({p.rafaga})."
        )


        self.tiempo += p.restante
        p.restante = 0
        p.estado = "Finalizado"


        self.historial_cpu.append((p.pid, inicio, self.tiempo))
        self._registrar(
            f"{p.pid} finaliza en el tiempo {self.tiempo}."
        )


        self._finalizar_proceso(p)


    def _paso_round_robin(self):
        if not self.cola_rr:
            return


        p = self.cola_rr.popleft()
        p.estado = "Ejecutando"
        self.proceso_actual = p


        inicio = self.tiempo
        uso = min(self.quantum, p.restante)


        self._registrar(
            f"Round-Robin asigna la CPU a {p.pid}. "
            f"Quantum = {self.quantum}."
        )


        self.tiempo += uso
        p.restante -= uso
        self.historial_cpu.append((p.pid, inicio, self.tiempo))


        if p.restante == 0:
            p.estado = "Finalizado"
            self._registrar(
                f"{p.pid} utilizó {uso} unidades y finalizó "
                f"en el tiempo {self.tiempo}."
            )
            self._finalizar_proceso(p)
        else:
            p.estado = "Listo"
            self.cola_rr.append(p)


            siguiente = self.cola_rr[0].pid if self.cola_rr else "ninguno"
            self._registrar(
                f"{p.pid} utilizó {uso} unidades. Restante: {p.restante}. "
                f"Terminó su quantum y vuelve a la cola."
            )
            self._registrar(
                f"Cambio de contexto: {p.pid} -> {siguiente}."
            )


    def _finalizar_proceso(self, proceso):
        self.memoria.liberar(proceso.pid)
        self._registrar(
            f"Se libera la memoria de {proceso.pid}. "
            f"Los huecos contiguos libres se reorganizan."
        )


        nuevos = []


        for p in self.espera_memoria[:]:
            if self.memoria.asignar(p, self.alg_mem):
                self.espera_memoria.remove(p)
                nuevos.append(p)
                self._registrar(
                    f"{p.pid} ingresa desde la espera de memoria "
                    f"mediante {self.alg_mem}."
                )


        if self.alg_cpu == "Round-Robin":
            for p in nuevos:
                self.cola_rr.append(p)
        else:
            self.listos.extend(nuevos)


            if self.alg_cpu == "SJF no apropiativo":
                self.listos.sort(key=lambda p: p.rafaga)


    def _actualizar_vistas(self):
        self.lbl_tiempo.config(text=f"Tiempo: {self.tiempo}")


        if self.proceso_actual:
            self.lbl_cpu.config(
                text=f"{self.proceso_actual.pid} "
                     f"(restante: {self.proceso_actual.restante})",
                fg=COLORES_ESTADO["Ejecutando"]["fg"]
            )
        else:
            self.lbl_cpu.config(text="Ninguno", fg=COLORES_ESTADO["Nuevo"]["fg"])


        if self.alg_cpu == "Round-Robin" and self.simulacion_activa:
            cola = list(self.cola_rr)
        else:
            cola = self.listos


        self.lbl_cola.config(
            text=" -> ".join(p.pid for p in cola) if cola else "Vacía"
        )


        self.lbl_espera.config(
            text=" -> ".join(p.pid for p in self.espera_memoria)
            if self.espera_memoria else "Ninguno"
        )


        if self.historial_cpu:
            partes = [
                f"{pid}[{ini}-{fin}]"
                for pid, ini, fin in self.historial_cpu
            ]
            self.lbl_historial.config(text=" | ".join(partes))
        else:
            self.lbl_historial.config(text="Sin ejecución")


        if self.simulacion_activa:
            self._actualizar_tabla(self.procesos_sim)
        else:
            self._actualizar_tabla(self.procesos)


        self._dibujar_memoria()


    def _actualizar_tabla(self, procesos):
        for item in self.tabla.get_children():
            self.tabla.delete(item)


        for p in procesos:
            self.tabla.insert(
                "",
                tk.END,
                values=(
                    p.pid,
                    p.rafaga,
                    f"{p.memoria} MB",
                    p.estado,
                    p.restante
                ),
                tags=(p.estado,)
            )


    def _dibujar_memoria(self):
        c = self.canvas_memoria
        c.delete("all")


        if not self.memoria:
            c.create_text(
                160,
                210,
                text="Inicie una simulación\npara visualizar la memoria",
                justify="center"
            )
            self.lbl_memoria_info.config(text="Memoria no inicializada")
            return


        ancho = max(c.winfo_width(), 300)
        alto = max(c.winfo_height(), 400)


        x1 = 45
        x2 = ancho - 45
        y = 20
        alto_util = alto - 40


        colores = [
            "#8ecae6",
            "#ffb703",
            "#90be6d",
            "#f28482",
            "#cdb4db",
            "#84a59d"
        ]
        mapa_colores = {}


        for bloque in self.memoria.bloques:
            proporcion = bloque.tamanio / self.memoria.tamanio_total
            h = max(24, alto_util * proporcion)


            if bloque.libre:
                color = "#eeeeee"
                texto = f"LIBRE\n{bloque.tamanio} MB"
            else:
                if bloque.pid not in mapa_colores:
                    mapa_colores[bloque.pid] = colores[len(mapa_colores) % len(colores)]
                color = mapa_colores[bloque.pid]
                texto = f"{bloque.pid}\n{bloque.tamanio} MB"


            c.create_rectangle(
                x1, y, x2, y + h,
                fill=color,
                outline="#444"
            )
            c.create_text(
                (x1 + x2) / 2,
                y + h / 2,
                text=texto,
                justify="center",
                font=("Arial", 11, "bold")
            )
            c.create_text(
                x1 - 8,
                y,
                text=str(bloque.inicio),
                anchor="e"
            )


            y += h


        c.create_text(
            x1 - 8,
            min(y, alto - 10),
            text=str(self.memoria.tamanio_total),
            anchor="e"
        )


        self.lbl_memoria_info.config(
            text=(
                f"Libre total: {self.memoria.memoria_libre_total()} MB\n"
                f"Fragmentación externa: "
                f"{self.memoria.fragmentacion_externa()} MB"
            )
        )


    def _registrar(self, mensaje):
        self.text_eventos.insert(tk.END, f"• {mensaje}\n")
        self.text_eventos.see(tk.END)


    def _actualizar_estado_quantum(self):
        if self.combo_cpu.get() == "Round-Robin":
            self.entry_quantum.config(state="normal")
        else:
            self.entry_quantum.config(state="disabled")


    def _verificar_fin(self):
        if self.alg_cpu == "Round-Robin":
            quedan_pendientes = bool(self.cola_rr)
        else:
            quedan_pendientes = bool(self.listos)


        if not quedan_pendientes:
            imposibles = [
                p for p in self.espera_memoria
                if p.memoria > self.memoria.tamanio_total
            ]


            if self.espera_memoria and len(imposibles) != len(self.espera_memoria):
                return


            self.simulacion_activa = False
            self.btn_paso.config(state="disabled")
            self.proceso_actual = None


            if self.espera_memoria:
                self._registrar(
                    "La simulacion termino, pero algunos procesos no pudieron "
                    "ingresar porque requieren mas memoria que la disponible."
                )
            else:
                self._registrar("Todos los procesos finalizaron.")


            self._actualizar_vistas()