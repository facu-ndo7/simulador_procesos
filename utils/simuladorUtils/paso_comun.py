"""Helpers compartidos por los pasos de CPU (FIFO / SJF / Round-Robin)."""

# Penalización por fallo de página: 1u de E/S a swap por página traída.
# Penalización por swapping: 1u adicional por reemplazo (escritura de
# la víctima desalojada a disco).
COSTO_FALLO_PAGINA = 1
COSTO_SWAP = 1


def contar_contexto(self, p):
    anterior = getattr(self, "proceso_actual", None)
    if anterior is not None and anterior.pid != p.pid:
        self.cambios_contexto = getattr(self, "cambios_contexto", 0) + 1
