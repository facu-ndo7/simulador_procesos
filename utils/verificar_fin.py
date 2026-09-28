from utils.registrar import registrar
from utils.actualizar_vistas import actualizar_vistas

def verificar_fin(self):
    if self.alg_cpu == "Round-Robin":
        quedan_pendientes = bool(self.cola_rr)
    else:
        quedan_pendientes = bool(self.listos)


    if not quedan_pendientes:
        imposibles = [
            p for p in self.espera_memoria
            if p.memoria > self.memoria.tamanio_total
        ]


        if self.espera_memoria and len(imposibles) != len(self.espera_memoria):
            return


        self.simulacion_activa = False
        self.btn_paso.config(state="disabled")
        self.proceso_actual = None


        if self.espera_memoria:
            registrar(
                self,
                "La simulacion termino, pero algunos procesos no pudieron "
                "ingresar porque requieren mas memoria que la disponible."
            )
        else:
            registrar(self, "Todos los procesos finalizaron.")
            
            
        actualizar_vistas(self)