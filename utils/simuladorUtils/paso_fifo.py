from utils.simuladorUtils.finalizar_proceso import finalizar_proceso
from utils.simuladorUtils.registrar import registrar
from utils.simuladorUtils.accesos_virtuales import simular_accesos_virtuales

# Penalización por fallo de página: 1u de E/S a swap por página traída.
# Penalización por swapping: 1u adicional por reemplazo (escritura de
# la víctima desalojada a disco).
COSTO_FALLO_PAGINA = 1
COSTO_SWAP = 1

def _contar_contexto(self, p):
    anterior = getattr(self, "proceso_actual", None)
    if anterior is not None and anterior.pid != p.pid:
        self.cambios_contexto = getattr(self, "cambios_contexto", 0) + 1

def paso_fifo(self):
    if not self.listos: return


    p = self.listos.pop(0)
    _contar_contexto(self, p)
    p.estado = "Ejecutando"
    self.proceso_actual = p
    inicio = self.tiempo


    registrar(
        self,
        f"FIFO selecciona {p.pid}, el primer proceso de la cola."
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
        f"{p.pid} ejecuta hasta finalizar en el tiempo {self.tiempo}."
    )


    finalizar_proceso(self, p)
