"""Asignación contigua con First/Best/Worst-Fit (código original migrado)."""
from utils import decoradores
from controllers.memoria.base import GestorMemoria


class MemoriaContigua(GestorMemoria):
    modo = "contigua"

    def __init__(self, tamanio_total, ajuste="First-Fit"):
        self.tamanio_total = tamanio_total
        self.ajuste = ajuste
        self.nombre = f"Asignación contigua ({ajuste})"
        self.bloques = [decoradores.Bloque(0, tamanio_total)]

    def candidatos(self, tamanio):
        return [
            (i, b)
            for i, b in enumerate(self.bloques)
            if b.libre and b.tamanio >= tamanio
        ]

    def asignar(self, proceso, algoritmo=None):
        ajuste = algoritmo or self.ajuste
        candidatos = self.candidatos(proceso.memoria)
        if not candidatos:
            return False

        if ajuste == "First-Fit":
            indice, bloque = candidatos[0]
        elif ajuste == "Best-Fit":
            indice, bloque = min(candidatos, key=lambda x: x[1].tamanio)
        elif ajuste == "Worst-Fit":
            indice, bloque = max(candidatos, key=lambda x: x[1].tamanio)
        else:
            return False

        sobrante = bloque.tamanio - proceso.memoria
        nuevos = [decoradores.Bloque(bloque.inicio, proceso.memoria, proceso.pid)]

        if sobrante > 0:
            nuevos.append(
                decoradores.Bloque(
                    bloque.inicio + proceso.memoria,
                    sobrante,
                    None,
                )
            )

        self.bloques[indice:indice + 1] = nuevos
        proceso.estado = "Listo"
        return True

    def liberar(self, pid):
        for bloque in self.bloques:
            if bloque.pid == pid:
                bloque.pid = None
        self.reorganizar()

    def reorganizar(self):
        nuevos = []
        for bloque in self.bloques:
            if nuevos and nuevos[-1].libre and bloque.libre:
                nuevos[-1].tamanio += bloque.tamanio
            else:
                nuevos.append(bloque)
        self.bloques = nuevos

    def fragmentacion_externa(self):
        huecos = [b.tamanio for b in self.bloques if b.libre]
        if len(huecos) <= 1:
            return 0
        return sum(huecos) - max(huecos)

    def memoria_libre_total(self):
        return sum(b.tamanio for b in self.bloques if b.libre)

    def info_resumen(self):
        return (
            f"{self.nombre}\n"
            f"Libre total: {self.memoria_libre_total()} MB\n"
            f"Fragmentación externa: {self.fragmentacion_externa()} MB"
        )

    def bloques_visuales(self):
        items = []
        for b in self.bloques:
            if b.libre:
                items.append((None, b.tamanio, f"LIBRE\n{b.tamanio} MB"))
            else:
                items.append((b.pid, b.tamanio, f"{b.pid}\n{b.tamanio} MB"))
        return items
