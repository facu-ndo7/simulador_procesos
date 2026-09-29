from utils.simuladorUtils.finalizar_proceso import finalizar_proceso
from utils.simuladorUtils.registrar import registrar
from utils.simuladorUtils.accesos_virtuales import simular_accesos_virtuales
from utils.simuladorUtils.paso_comun import (
    COSTO_FALLO_PAGINA,
    COSTO_SWAP,
    contar_contexto as _contar_contexto,
)

def paso_sjf(self):
    if not self.listos: return


    p = min(self.listos, key=lambda x: x.rafaga)
    self.listos.remove(p)


    _contar_contexto(self, p)
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
        stall = (res["faults"] * COSTO_FALLO_PAGINA
                 + res.get("swaps", 0) * COSTO_SWAP)
        registrar(
            self,
            f"{p.pid} sufre {res['faults']} fallo(s) de página "
            f"({res.get('swaps', 0)} swaps): pasa a "
            f"'Esperando página' (+{stall}u de E/S a swap) y luego continúa."
        )
        self.tiempo += stall
        p.estado = "Ejecutando"
    self.tiempo += p.restante
    self.tiempo_cpu = getattr(self, "tiempo_cpu", 0) + unidades
    p.restante = 0
    p.estado = "Terminado"


    self.historial_cpu.append((p.pid, inicio, self.tiempo))
    registrar(
        self,
        f"{p.pid} finaliza en el tiempo {self.tiempo}."
    )


    finalizar_proceso(self, p)
