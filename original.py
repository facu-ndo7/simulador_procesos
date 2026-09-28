import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field
from collections import deque
from copy import deepcopy


COLORES_ESTADO = {
    "Nuevo": {"bg": "#e9ecef", "fg": "#495057"},
    "Listo": {"bg": "#d3f9d8", "fg": "#2b8a3e"},
    "Ejecutando": {"bg": "#fff3bf", "fg": "#e67700"},
    "Esperando memoria": {"bg": "#ffe3e3", "fg": "#c92a2a"},
    "Finalizado": {"bg": "#d0ebff", "fg": "#1864ab"},
}


@dataclass
class Proceso:
    pid: str
    rafaga: int
    memoria: int
    estado: str = "Nuevo"
    restante: int = field(init=False)


    def __post_init__(self):
        self.restante = self.rafaga


@dataclass
class Bloque:
    inicio: int
    tamanio: int
    pid: str | None = None


    @property
    def libre(self):
        return self.pid is None


    @property
    def fin(self):
        return self.inicio + self.tamanio - 1


class Memoria:
    def __init__(self, tamanio_total):
        self.tamanio_total = tamanio_total
        self.bloques = [Bloque(0, tamanio_total)]


    def candidatos(self, tamanio):
        return [
            (i, b)
            for i, b in enumerate(self.bloques)
            if b.libre and b.tamanio >= tamanio
        ]


    def asignar(self, proceso, algoritmo):
        candidatos = self.candidatos(proceso.memoria)
        if not candidatos:
            return False


        if algoritmo == "First-Fit":
            indice, bloque = candidatos[0]
        elif algoritmo == "Best-Fit":
            indice, bloque = min(candidatos, key=lambda x: x[1].tamanio)
        elif algoritmo == "Worst-Fit":
            indice, bloque = max(candidatos, key=lambda x: x[1].tamanio)
        else:
            return False


        sobrante = bloque.tamanio - proceso.memoria
        nuevos = [Bloque(bloque.inicio, proceso.memoria, proceso.pid)]


        if sobrante > 0:
            nuevos.append(
                Bloque(
                    bloque.inicio + proceso.memoria,
                    sobrante,
                    None
                )
            )


        self.bloques[indice:indice + 1] = nuevos
        proceso.estado = "Listo"
        return True


    def liberar(self, pid):
        for bloque in self.bloques:
            if bloque.pid == pid:
                bloque.pid = None
        self.reorganizar()


    def reorganizar(self):
        nuevos = []
        for bloque in self.bloques:
            if nuevos and nuevos[-1].libre and bloque.libre:
                nuevos[-1].tamanio += bloque.tamanio
            else:
                nuevos.append(bloque)
        self.bloques = nuevos


    def fragmentacion_externa(self):
        huecos = [b.tamanio for b in self.bloques if b.libre]
        if len(huecos) <= 1:
            return 0
        return sum(huecos) - max(huecos)


    def memoria_libre_total(self):
        return sum(b.tamanio for b in self.bloques if b.libre)


class SimuladorSO(tk.Tk):
    def __init__(self):
        super().__init__()


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


        self._crear_interfaz()
        self._actualizar_estado_quantum()


    def _crear_interfaz(self):
        contenedor = ttk.Frame(self, padding=12)
        contenedor.pack(fill="both", expand=True)


        # Panel superior
        superior = ttk.Frame(contenedor)
        superior.pack(side="top", fill="x", pady=(0, 10))


        self._crear_panel_procesos(superior)
        self._crear_panel_configuracion(superior)


        inferior = ttk.Frame(contenedor)
        inferior.pack(side="bottom", fill="x", pady=(10, 0))
        self._crear_panel_eventos(inferior)


        central = ttk.Frame(contenedor)
        central.pack(side="top", fill="both", expand=True)


        self._crear_tabla(central)
        self._crear_panel_cpu(central)
        self._crear_panel_memoria(central)


    def _crear_panel_procesos(self, padre):
        marco = ttk.LabelFrame(padre, text="Carga de procesos", padding=10)
        marco.pack(side="left", fill="x", expand=True, padx=(0, 6))


        ttk.Label(marco, text="ID").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(marco, text="Ráfaga CPU").grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(marco, text="Memoria (MB)").grid(row=0, column=2, sticky="w", padx=5, pady=5)


        self.entry_pid = ttk.Entry(marco, width=15)
        self.entry_rafaga = ttk.Entry(marco, width=15)
        self.entry_memoria = ttk.Entry(marco, width=15)


        self.entry_pid.grid(row=1, column=0, padx=5, pady=5)
        self.entry_rafaga.grid(row=1, column=1, padx=5, pady=5)
        self.entry_memoria.grid(row=1, column=2, padx=5, pady=5)


        ttk.Button(
            marco,
            text="Agregar proceso",
            command=self.agregar_proceso
        ).grid(row=1, column=3, padx=8, pady=5)


        ttk.Button(
            marco,
            text="Eliminar seleccionado",
            command=self.eliminar_proceso
        ).grid(row=2, column=3, padx=8, pady=5)


        ttk.Label(
            marco,
            text="Ingresar por teclado: ID, ráfaga y memoria requerida."
        ).grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=(8, 0))


    def _crear_panel_configuracion(self, padre):
        marco = ttk.LabelFrame(padre, text="Configuración", padding=10)
        marco.pack(side="left", fill="x", expand=True, padx=(6, 0))


        ttk.Label(marco, text="Memoria total (MB)").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_mem_total = ttk.Entry(marco, width=12)
        self.entry_mem_total.insert(0, "100")
        self.entry_mem_total.grid(row=1, column=0, padx=5, pady=5)


        ttk.Label(marco, text="Algoritmo CPU").grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.combo_cpu = ttk.Combobox(
            marco,
            state="readonly",
            values=[
                "FIFO",
                "SJF no apropiativo",
                "Round-Robin",
            ],
            width=22
        )
        self.combo_cpu.current(0)
        self.combo_cpu.grid(row=1, column=1, padx=5, pady=5)
        self.combo_cpu.bind("<<ComboboxSelected>>", lambda e: self._actualizar_estado_quantum())


        ttk.Label(marco, text="Algoritmo memoria").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.combo_mem = ttk.Combobox(
            marco,
            state="readonly",
            values=["First-Fit", "Best-Fit", "Worst-Fit"],
            width=16
        )
        self.combo_mem.current(0)
        self.combo_mem.grid(row=1, column=2, padx=5, pady=5)


        ttk.Label(marco, text="Quantum").grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.entry_quantum = ttk.Entry(marco, width=10)
        self.entry_quantum.insert(0, "2")
        self.entry_quantum.grid(row=1, column=3, padx=5, pady=5)


        ttk.Button(
            marco,
            text="Iniciar simulación",
            command=self.iniciar_simulacion
        ).grid(row=2, column=0, padx=5, pady=10)


        self.btn_paso = ttk.Button(
            marco,
            text="Paso siguiente",
            command=self.paso_siguiente,
            state="disabled"
        )
        self.btn_paso.grid(row=2, column=1, padx=5, pady=10)


        ttk.Button(
            marco,
            text="Reiniciar",
            command=self.reiniciar_simulacion
        ).grid(row=2, column=2, padx=5, pady=10)


        ttk.Button(
            marco,
            text="Limpiar todo",
            command=self.limpiar_todo
        ).grid(row=2, column=3, padx=5, pady=10)


    def _crear_tabla(self, padre):
        marco = ttk.LabelFrame(padre, text="Procesos", padding=8)
        marco.pack(side="left", fill="both", expand=True, padx=(0, 6))


        columnas = ("pid", "rafaga", "memoria", "estado", "restante")
        self.tabla = ttk.Treeview(
            marco,
            columns=columnas,
            show="headings",
            height=12
        )


        scroll_tabla = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_tabla.set)
        scroll_tabla.pack(side="right", fill="y")


        encabezados = {
            "pid": "ID",
            "rafaga": "Ráfaga",
            "memoria": "Memoria",
            "estado": "Estado",
            "restante": "Restante"
        }


        for col in columnas:
            self.tabla.heading(col, text=encabezados[col])
            self.tabla.column(col, anchor="center", width=95)


        for estado, colores in COLORES_ESTADO.items():
            self.tabla.tag_configure(estado, background=colores["bg"], foreground=colores["fg"])


        self.tabla.pack(fill="both", expand=True)


    def _crear_panel_cpu(self, padre):
        marco = ttk.LabelFrame(padre, text="CPU y cola de listos", padding=10)
        marco.pack(side="left", fill="both", expand=True, padx=6)


        self.lbl_tiempo = ttk.Label(marco, text="Tiempo: 0", font=("Arial", 16, "bold"))
        self.lbl_tiempo.pack(anchor="w", pady=(0, 10))


        ttk.Label(marco, text="Proceso ejecutándose:").pack(anchor="w")
        self.lbl_cpu = tk.Label(
            marco,
            text="Ninguno",
            font=("Arial", 20, "bold"),
            fg=COLORES_ESTADO["Nuevo"]["fg"]
        )
        self.lbl_cpu.pack(anchor="w", pady=(3, 15))


        ttk.Label(marco, text="Cola de listos:").pack(anchor="w")
        self.lbl_cola = tk.Label(
            marco,
            text="Vacía",
            font=("Arial", 13, "bold"),
            fg=COLORES_ESTADO["Listo"]["fg"],
            wraplength=300,
            justify="left"
        )
        self.lbl_cola.pack(anchor="w", pady=(3, 15))


        ttk.Label(marco, text="Esperando memoria:").pack(anchor="w")
        self.lbl_espera = tk.Label(
            marco,
            text="Ninguno",
            font=("Arial", 13, "bold"),
            fg=COLORES_ESTADO["Esperando memoria"]["fg"],
            wraplength=300,
            justify="left"
        )
        self.lbl_espera.pack(anchor="w", pady=(3, 15))


        ttk.Label(marco, text="Historial CPU:").pack(anchor="w")
        self.lbl_historial = ttk.Label(
            marco,
            text="Sin ejecución",
            wraplength=300
        )
        self.lbl_historial.pack(anchor="w", pady=(3, 10))


    def _crear_panel_memoria(self, padre):
        marco = ttk.LabelFrame(padre, text="Memoria principal", padding=8)
        marco.pack(side="left", fill="both", expand=True, padx=(6, 0))


        self.canvas_memoria = tk.Canvas(
            marco,
            width=320,
            height=370,
            bg="white",
            highlightthickness=1,
            highlightbackground="#999"
        )
        self.canvas_memoria.pack(fill="both", expand=True)


        self.lbl_memoria_info = ttk.Label(
            marco,
            text="Memoria no inicializada",
            justify="left"
        )
        self.lbl_memoria_info.pack(anchor="w", pady=(8, 0))


    def _crear_panel_eventos(self, padre):
        marco = ttk.LabelFrame(padre, text="Registro paso a paso", padding=8)
        marco.pack(fill="x")


        self.text_eventos = tk.Text(marco, height=8, wrap="word", font=("Arial", 11))
        self.text_eventos.pack(fill="x")


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


        self.procesos.append(Proceso(pid, rafaga, memoria))
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
        self.memoria = Memoria(tamanio_memoria)


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


if __name__ == "__main__":
    app = SimuladorSO()
    app.mainloop()

