from utils.simuladorUtils.paso_fifo import paso_fifo
from utils.simuladorUtils.paso_sjf import paso_sjf
from utils.simuladorUtils.paso_round_robin import paso_round_robin
from utils.simuladorUtils.actualizar_vistas import actualizar_vistas
from utils.simuladorUtils.verificar_fin import verificar_fin
from utils.simuladorUtils.registrar import registrar
from collections import deque

def paso_siguiente(self):
    if not self.simulacion_activa: return


    # Retorno de la espera de página: la carga desde swap ya terminó,
    # los procesos vuelven a Listo antes de planificar.
    espera_pagina = getattr(self, "espera_pagina", []) or []
    if espera_pagina:
        reingresos = list(espera_pagina)
        self.espera_pagina = []
        for p in reingresos:
            p.estado = "Listo"
            registrar(
                self,
                f"{p.pid} completa la carga desde swap: vuelve a Listo."
            )
        if self.alg_cpu == "Round-Robin":
            if not hasattr(self, "cola_rr") or self.cola_rr is None:
                self.cola_rr = deque()
            for p in reingresos:
                self.cola_rr.append(p)
        else:
            self.listos.extend(reingresos)
            if self.alg_cpu == "SJF no apropiativo":
                self.listos.sort(key=lambda p: p.rafaga)


    if self.alg_cpu == "FIFO":
        paso_fifo(self)
    elif self.alg_cpu == "SJF no apropiativo":
        paso_sjf(self)
    else:
        paso_round_robin(self)


    actualizar_vistas(self)
    verificar_fin(self)
