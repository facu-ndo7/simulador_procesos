from utils.simuladorUtils.registrar import registrar

def finalizar_proceso(self, proceso):
    self.memoria.liberar(proceso.pid)
    registrar(
        self,
        f"Se libera la memoria de {proceso.pid} ({self.memoria.nombre})."
    )


    nuevos = []


    for p in self.espera_memoria[:]:
        if self.memoria.asignar(p):
            self.espera_memoria.remove(p)
            nuevos.append(p)
            registrar(
                self,
                f"{p.pid} ingresa desde la espera de memoria "
                f"mediante {self.memoria.nombre}."
            )


    if self.alg_cpu == "Round-Robin":
        for p in nuevos:
            self.cola_rr.append(p)
    else:
        self.listos.extend(nuevos)


        if self.alg_cpu == "SJF no apropiativo":
            self.listos.sort(key=lambda p: p.rafaga)
