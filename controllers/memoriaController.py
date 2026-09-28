from utils import decoradores

class Memoria:
    def __init__(self, tamanio_total):
        self.tamanio_total = tamanio_total
        self.bloques = [decoradores.Bloque(0, tamanio_total)]


    def candidatos(self, tamanio):
        return [
            (i, b)
            for i, b in enumerate(self.bloques)
            if b.libre and b.tamanio >= tamanio
        ]


    def asignar(self, proceso, algoritmo):
        candidatos = self.candidatos(proceso.memoria)
        if not candidatos:
            return False


        if algoritmo == "First-Fit":
            indice, bloque = candidatos[0]
        elif algoritmo == "Best-Fit":
            indice, bloque = min(candidatos, key=lambda x: x[1].tamanio)
        elif algoritmo == "Worst-Fit":
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
                    None
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