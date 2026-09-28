from utils.paso_fifo import paso_fifo
from utils.paso_sjf import paso_sjf
from utils.paso_round_robin import paso_round_robin
from utils.actualizar_vistas import actualizar_vistas
from utils.verificar_fin import verificar_fin

def paso_siguiente(self):
    if not self.simulacion_activa: return


    if self.alg_cpu == "FIFO":
        paso_fifo(self)
    elif self.alg_cpu == "SJF no apropiativo":
        paso_sjf(self)
    else:
        paso_round_robin(self)


    actualizar_vistas(self)
    verificar_fin(self)