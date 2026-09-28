from utils.simuladorUtils.finalizar_proceso import finalizar_proceso
from utils.simuladorUtils.registrar import registrar
from utils.simuladorUtils.accesos_virtuales import simular_accesos_virtuales

# Penalización por fallo de página: 1u de E/S a swap por página traída.
COSTO_FALLO_PAGINA = 1

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
    res = simular_accesos_virtuales(self, p, unidades)
    if res and res.get("faults"):
        p.estado = "Esperando página"
        registrar(
            self,
            f"{p.pid} sufre {res['faults']} fallo(s) de página: pasa a "
            f"'Esperando página' (+{res['faults'] * COSTO_FALLO_PAGINA}u "
            f"de E/S a swap) y luego continúa."
        )
        self.tiempo += res["faults"] * COSTO_FALLO_PAGINA
        p.estado = "Ejecutando"
    self.tiempo += p.restante
    p.restante = 0
    p.estado = "Terminado"


    self.historial_cpu.append((p.pid, inicio, self.tiempo))
    registrar(
        self,
        f"{p.pid} finaliza en el tiempo {self.tiempo}."
    )


    finalizar_proceso(self, p)
