from utils.simuladorUtils.finalizar_proceso import finalizar_proceso
from utils.simuladorUtils.registrar import registrar

def paso_fifo(self):
    if not self.listos: return


    p = self.listos.pop(0)
    p.estado = "Ejecutando"
    self.proceso_actual = p
    inicio = self.tiempo


    registrar(
        self,
        f"FIFO selecciona {p.pid}, el primer proceso de la cola."
    )


    self.tiempo += p.restante
    p.restante = 0
    p.estado = "Finalizado"


    self.historial_cpu.append((p.pid, inicio, self.tiempo))
    registrar(
        self,
        f"{p.pid} ejecuta hasta finalizar en el tiempo {self.tiempo}."
    )


    finalizar_proceso(self, p)