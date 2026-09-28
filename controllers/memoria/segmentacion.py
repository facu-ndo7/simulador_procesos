"""Segmentación: cada proceso se divide en segmentos lógicos contiguos."""
from dataclasses import dataclass
from utils import decoradores
from controllers.memoria.base import GestorMemoria

NOMBRES_SEG = ["Código", "Datos", "Pila"]


class ViolacionSegmento(Exception):
    """Desplazamiento fuera del límite del segmento (desp >= límite)."""

    def __init__(self, pid, segmento, desplazamiento, limite):
        self.pid = pid
        self.segmento = segmento
        self.desplazamiento = desplazamiento
        self.limite = limite
        super().__init__(
            f"Violación de segmento: {pid}:S{segmento} con desplazamiento "
            f"{desplazamiento} excede el límite {limite}."
        )


@dataclass
class EntradaSegmento:
    """Una entrada de la tabla de segmentos: base + límite."""
    seg: int
    nombre: str
    base: int
    limite: int

    @property
    def tamanio(self):
        return self.limite


def dividir_segmentos(tamanio):
    """Partición determinista y documentada del tamaño pedido.

    - <=2 MB: 1 segmento.
    - 3..10 MB: 2 segmentos (60/40).
    - >10 MB: 3 segmentos (50/30/20).
    """
    if tamanio <= 2:
        return [tamanio]
    if tamanio <= 10:
        s0 = max(1, (tamanio * 60) // 100)
        s1 = tamanio - s0
        return [s0, s1]
    s0 = (tamanio * 50) // 100
    s1 = (tamanio * 30) // 100
    s2 = tamanio - s0 - s1
    partes = [s0, s1, s2]
    # Evita segmentos de tamaño 0.
    for i, v in enumerate(partes):
        if v <= 0:
            partes[i] = 1
    ajuste = sum(partes) - tamanio
    partes[-1] -= ajuste
    return partes


class MemoriaSegmentada(GestorMemoria):
    modo = "segmentacion"

    def __init__(self, tamanio_total, ajuste="First-Fit"):
        if ajuste not in ("First-Fit", "Best-Fit", "Worst-Fit"):
            ajuste = "First-Fit"
        self.tamanio_total = tamanio_total
        self.ajuste = ajuste
        self.nombre = f"Segmentación ({ajuste})"
        self.bloques = [decoradores.Bloque(0, tamanio_total)]
        # Tabla de segmentos por proceso: pid -> [EntradaSegmento].
        self.tabla_segmentos = {}

    def obtener_tabla(self, pid):
        """Devuelve la tabla de segmentos del proceso ([EntradaSegmento])."""
        return list(self.tabla_segmentos.get(pid, []))

    def _candidatos(self, tamanio):
        return [(i, b) for i, b in enumerate(self.bloques)
                if b.libre and b.tamanio >= tamanio]

    def _elegir_hueco(self, tamanio):
        candidatos = self._candidatos(tamanio)
        if not candidatos:
            return None
        if self.ajuste == "Best-Fit":
            return min(candidatos, key=lambda x: x[1].tamanio)
        if self.ajuste == "Worst-Fit":
            return max(candidatos, key=lambda x: x[1].tamanio)
        return candidatos[0]  # First-Fit

    def _ocupar(self, indice, tamanio, etiqueta):
        bloque = self.bloques[indice]
        sobrante = bloque.tamanio - tamanio
        nuevos = [decoradores.Bloque(bloque.inicio, tamanio, etiqueta)]
        if sobrante > 0:
            nuevos.append(decoradores.Bloque(bloque.inicio + tamanio, sobrante, None))
        self.bloques[indice:indice + 1] = nuevos
        return nuevos[0].inicio

    def asignar(self, proceso, ajuste=None) -> bool:
        if ajuste is not None:
            self.ajuste = ajuste
        if proceso.pid in self.tabla_segmentos:
            return True
        partes = dividir_segmentos(proceso.memoria)
        # Snapshot para rollback si algún segmento no cabe.
        snapshot = [decoradores.Bloque(b.inicio, b.tamanio, b.pid) for b in self.bloques]
        entradas = []
        for j, tam in enumerate(partes):
            hallado = self._elegir_hueco(tam)
            if hallado is None:
                self.bloques = snapshot
                return False
            indice, _ = hallado
            etiqueta = f"{proceso.pid}:S{j}"
            base = self._ocupar(indice, tam, etiqueta)
            nombre = NOMBRES_SEG[j] if j < len(NOMBRES_SEG) else f"Seg{j}"
            entradas.append(EntradaSegmento(seg=j, nombre=nombre,
                                            base=base, limite=tam))
        self.tabla_segmentos[proceso.pid] = entradas
        proceso.estado = "Listo"
        return True

    def liberar(self, pid) -> None:
        if pid not in self.tabla_segmentos:
            return
        del self.tabla_segmentos[pid]
        for bloque in self.bloques:
            if bloque.pid is not None and bloque.pid.split(":")[0] == pid:
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

    def traducir(self, pid, segmento, desplazamiento):
        """Traduce (segmento, desplazamiento) -> dirección física.

        Verifica 0 <= desplazamiento < límite; si se excede, lanza
        ViolacionSegmento (requisito 4).
        Devuelve {"segmento", "nombre", "desplazamiento", "limite",
                  "base", "direccion_fisica"}.
        """
        if pid not in self.tabla_segmentos:
            raise KeyError(f"El proceso '{pid}' no está en memoria.")
        entradas = self.tabla_segmentos[pid]
        if not isinstance(segmento, int) or not (0 <= segmento < len(entradas)):
            raise ValueError(
                f"Segmento {segmento} inválido en '{pid}' "
                f"(0..{len(entradas) - 1}).")
        if not isinstance(desplazamiento, int):
            raise ValueError("El desplazamiento debe ser un entero.")
        entrada = entradas[segmento]
        if desplazamiento < 0 or desplazamiento >= entrada.limite:
            raise ViolacionSegmento(pid, segmento, desplazamiento,
                                    entrada.limite)
        return {
            "segmento": segmento,
            "nombre": entrada.nombre,
            "desplazamiento": desplazamiento,
            "limite": entrada.limite,
            "base": entrada.base,
            "direccion_fisica": entrada.base + desplazamiento,
        }

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
