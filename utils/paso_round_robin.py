from utils.finalizar_proceso import finalizar_proceso
from utils.registrar import registrar

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


    self.tiempo += uso
    p.restante -= uso
    self.historial_cpu.append((p.pid, inicio, self.tiempo))


    if p.restante == 0:
        p.estado = "Finalizado"
        registrar(
            self,
            f"{p.pid} utilizó {uso} unidades y finalizó "
            f"en el tiempo {self.tiempo}."
        )
        finalizar_proceso(self, p)
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