from utils.simuladorUtils.registrar import registrar
from utils.simuladorUtils.actualizar_vistas import actualizar_vistas

def verificar_fin(self):
    if self.alg_cpu == "Round-Robin":
        quedan_pendientes = bool(self.cola_rr)
    else:
        quedan_pendientes = bool(self.listos)
    quedan_pendientes = (quedan_pendientes
                         or bool(getattr(self, "bloqueados", []))
                         or bool(getattr(self, "espera_pagina", [])))


    if not quedan_pendientes:
        limite = getattr(self.memoria, "tamanio_virtual",
                         self.memoria.tamanio_total)
        imposibles = [
            p for p in self.espera_memoria
            if p.memoria > limite
        ]


        if self.espera_memoria and len(imposibles) != len(self.espera_memoria):
            return


        self.simulacion_activa = False
        self.btn_paso.config(state="disabled")
        if hasattr(self, "btn_cambiar_mem"):
            self.btn_cambiar_mem.config(state="disabled")
        self.auto = False
        if hasattr(self, "btn_auto"):
            try:
                self.btn_auto.config(text="Auto")
            except Exception:
                pass
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