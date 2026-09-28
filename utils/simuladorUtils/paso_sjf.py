from utils.simuladorUtils.finalizar_proceso import finalizar_proceso
from utils.simuladorUtils.registrar import registrar
from utils.simuladorUtils.accesos_virtuales import simular_accesos_virtuales

def paso_sjf(self):
    if not self.listos: return


    p = min(self.listos, key=lambda x: x.rafaga)
    self.listos.remove(p)


    p.estado = "Ejecutando"
    self.proceso_actual = p
    inicio = self.tiempo


    registrar(
        self,
        f"SJF selecciona {p.pid} porque tiene la ráfaga más corta "
        f"entre los procesos listos ({p.rafaga})."
    )


    unidades = p.restante
    simular_accesos_virtuales(self, p, unidades)
    self.tiempo += p.restante
    p.restante = 0
    p.estado = "Finalizado"


    self.historial_cpu.append((p.pid, inicio, self.tiempo))
    registrar(
        self,
        f"{p.pid} finaliza en el tiempo {self.tiempo}."
    )


    finalizar_proceso(self, p)
