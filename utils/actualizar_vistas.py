from utils.actualizar_tabla import actualizar_tabla
from utils.dibujar_memoria import dibujar_memoria

COLORES_ESTADO = {
    "Nuevo": {"bg": "#e9ecef", "fg": "#495057"},
    "Listo": {"bg": "#d3f9d8", "fg": "#2b8a3e"},
    "Ejecutando": {"bg": "#fff3bf", "fg": "#e67700"},
    "Esperando memoria": {"bg": "#ffe3e3", "fg": "#c92a2a"},
    "Finalizado": {"bg": "#d0ebff", "fg": "#1864ab"},
}

def actualizar_vistas(self):
    self.lbl_tiempo.config(text=f"Tiempo: {self.tiempo}")


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
        actualizar_tabla(self, self.procesos_sim)
    else:
        actualizar_tabla(self, self.procesos)


    dibujar_memoria(self)