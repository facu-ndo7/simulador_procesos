from utils.simuladorUtils.finalizar_proceso import finalizar_proceso
from utils.simuladorUtils.registrar import registrar
from utils.simuladorUtils.accesos_virtuales import simular_accesos_virtuales

# Penalización por fallo de página: 1u de E/S a swap por página traída.
COSTO_FALLO_PAGINA = 1

def paso_round_robin(self):
    if not self.cola_rr: return


    p = self.cola_rr.popleft()
    p.estado = "Ejecutando"
    self.proceso_actual = p


    inicio = self.tiempo
    uso = min(self.quantum, p.restante)


    registrar(
        self,
        f"Round-Robin asigna la CPU a {p.pid}. "
        f"Quantum = {self.quantum}."
    )


    res = simular_accesos_virtuales(self, p, uso)
    fallos = res.get("faults", 0) if res else 0
    if fallos:
        self.tiempo += fallos * COSTO_FALLO_PAGINA
    self.tiempo += uso
    p.restante -= uso
    self.historial_cpu.append((p.pid, inicio, self.tiempo))


    if p.restante == 0:
        if fallos:
            registrar(
                self,
                f"{p.pid} pasó por 'Esperando página' "
                f"(+{fallos * COSTO_FALLO_PAGINA}u de E/S a swap)."
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
            f"{p.pid} utilizó {uso} unidades pero sufrió {fallos} fallo(s): "
            f"pasa a 'Esperando página' y retomará en el próximo paso."
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
