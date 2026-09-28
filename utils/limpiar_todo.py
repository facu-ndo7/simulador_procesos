from utils.reiniciar_simulacion import reiniciar_simulacion
from utils.actualizar_tabla import actualizar_tabla

def limpiar_todo(self):
    reiniciar_simulacion(self)
    self.procesos = []
    actualizar_tabla(self, self.procesos)