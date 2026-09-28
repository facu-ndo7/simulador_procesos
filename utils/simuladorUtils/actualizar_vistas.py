from utils.simuladorUtils.actualizar_tabla import actualizar_tabla
from utils.simuladorUtils.dibujar_memoria import dibujar_memoria
from utils.simuladorUtils.actualizar_tabla_paginas import actualizar_tabla_paginas

COLORES_ESTADO = {
    "Nuevo": {"bg": "#e9ecef", "fg": "#495057"},
    "Listo": {"bg": "#d3f9d8", "fg": "#2b8a3e"},
    "Ejecutando": {"bg": "#fff3bf", "fg": "#e67700"},
    "Esperando memoria": {"bg": "#ffe3e3", "fg": "#c92a2a"},
    "Bloqueado": {"bg": "#e5dbff", "fg": "#5f3dc4"},
    "Esperando página": {"bg": "#ffe8cc", "fg": "#d9480f"},
    "Terminado": {"bg": "#d0ebff", "fg": "#1864ab"},
}

def actualizar_vistas(self):
    self.lbl_tiempo.config(text=f"Tiempo: {self.tiempo}")


    tcpu = getattr(self, "tiempo_cpu", 0)
    if self.tiempo > 0:
        self.lbl_uso_cpu.config(
            text=f"Uso CPU: {100.0 * tcpu / self.tiempo:.0f}% ({tcpu}/{self.tiempo} u)")
    else:
        self.lbl_uso_cpu.config(text="Uso CPU: —")


    self.lbl_contexto.config(
        text=f"Cambios de contexto: {getattr(self, 'cambios_contexto', 0)}")


    if self.proceso_actual:
        self.lbl_cpu.config(
            text=f"{self.proceso_actual.pid} "f"(restante: {self.proceso_actual.restante})",
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


    if self.simulacion_activa:
        fuente_nuevos = self.procesos_sim
    else:
        fuente_nuevos = self.procesos
    nuevos = [p.pid for p in fuente_nuevos if p.estado == "Nuevo"]
    self.lbl_nuevos.config(
        text=" -> ".join(nuevos) if nuevos else "Ninguno"
    )


    self.lbl_espera.config(
        text=" -> ".join(p.pid for p in self.espera_memoria)
        if self.espera_memoria else "Ninguno"
    )


    bloqueados = getattr(self, "bloqueados", []) or []
    self.lbl_bloqueados.config(
        text=" -> ".join(p.pid for p in bloqueados)
        if bloqueados else "Ninguno"
    )


    espera_pagina = getattr(self, "espera_pagina", []) or []
    self.lbl_espera_pagina.config(
        text=" -> ".join(p.pid for p in espera_pagina)
        if espera_pagina else "Ninguno"
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
        actualizar_tabla(self, self.procesos_sim)
    else:
        actualizar_tabla(self, self.procesos)


    dibujar_memoria(self)
    actualizar_tabla_paginas(self)