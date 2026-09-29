from utils.simuladorUtils.finalizar_proceso import finalizar_proceso
from utils.simuladorUtils.registrar import registrar
from utils.simuladorUtils.accesos_virtuales import simular_accesos_virtuales
from utils.simuladorUtils.paso_comun import (
    COSTO_FALLO_PAGINA,
    COSTO_SWAP,
    contar_contexto as _contar_contexto,
)

def _quantum_vigente(self):
    """Lee el quantum del entry si es válido (cambio en caliente)."""
    entry = getattr(self, "entry_quantum", None)
    if entry is not None:
        try:
            valor = int(entry.get().strip())
        except (ValueError, AttributeError):
            return getattr(self, "quantum", 0)
        if valor > 0:
            self.quantum = valor
    return getattr(self, "quantum", 0)

def paso_round_robin(self):
    if not self.cola_rr: return


    p = self.cola_rr.popleft()
    _contar_contexto(self, p)
    p.estado = "Ejecutando"
    self.proceso_actual = p


    inicio = self.tiempo
    # Quantum en caliente: si el entry trae un valor válido, se aplica
    # desde este paso sin reiniciar.
    quantum = _quantum_vigente(self)
    uso = min(quantum, p.restante)


    registrar(
        self,
        f"Round-Robin asigna la CPU a {p.pid}. "
        f"Quantum = {quantum}."
    )


    res = simular_accesos_virtuales(self, p, uso)
    fallos = res.get("faults", 0) if res else 0
    swaps = res.get("swaps", 0) if res else 0
    stall = fallos * COSTO_FALLO_PAGINA + swaps * COSTO_SWAP
    if stall:
        self.tiempo += stall
    self.tiempo += uso
    self.tiempo_cpu = getattr(self, "tiempo_cpu", 0) + uso
    p.restante -= uso
    self.historial_cpu.append((p.pid, inicio, self.tiempo))


    if p.restante == 0:
        if fallos:
            registrar(
                self,
                f"{p.pid} pasó por 'Esperando página' "
                f"({fallos} fallos, {swaps} swaps, +{stall}u de E/S a swap)."
            )
        p.estado = "Terminado"
        registrar(
            self,
            f"{p.pid} utilizó {uso} unidades y finalizó "
            f"en el tiempo {self.tiempo}."
        )
        finalizar_proceso(self, p)
    elif fallos:
        # Con fallos y ráfaga restante, el proceso espera la carga desde
        # swap: queda en 'Esperando página' y vuelve a Listo en el paso
        # siguiente (ver paso_siguiente).
        p.estado = "Esperando página"
        if not hasattr(self, "espera_pagina"):
            self.espera_pagina = []
        self.espera_pagina.append(p)
        registrar(
            self,
            f"{p.pid} utilizó {uso} unidades pero sufrió {fallos} fallo(s) "
            f"y {swaps} swap(s): pasa a 'Esperando página' (+{stall}u) "
            f"y retomará en el próximo paso."
        )
    else:
        p.estado = "Listo"
        self.cola_rr.append(p)


        siguiente = self.cola_rr[0].pid if self.cola_rr else "ninguno"
        registrar(
            self,
            f"{p.pid} utilizó {uso} unidades. Restante: {p.restante}. "
            f"Terminó su quantum y vuelve a la cola."
        )
        registrar(
            self,
            f"Cambio de contexto: {p.pid} -> {siguiente}."
        )
