from utils.simuladorUtils.reiniciar_simulacion import reiniciar_simulacion
from utils.simuladorUtils.actualizar_tabla import actualizar_tabla

def limpiar_todo(self):
    reiniciar_simulacion(self)
    self.procesos = []
    self.proximo_pid = 1
    if hasattr(self, "var_proximo_pid"):
        try:
            self.var_proximo_pid.set("1")
        except Exception:
            pass
    actualizar_tabla(self, self.procesos)