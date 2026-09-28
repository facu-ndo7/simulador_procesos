"""Segmentación paginada: segmentos lógicos divididos en páginas sobre marcos."""
import math
from dataclasses import dataclass, field
from controllers.memoria.base import GestorMemoria
from controllers.memoria.segmentacion import (
    dividir_segmentos,
    NOMBRES_SEG,
    ViolacionSegmento,
)


@dataclass
class EntradaPaginaSP:
    """Entrada de la tabla de páginas de un segmento: página -> marco."""
    pagina: int
    marco: int


@dataclass
class EntradaSegmentoSP:
    """Entrada de la tabla de segmentos: apunta a su tabla de páginas."""
    seg: int
    nombre: str
    limite: int
    tabla_paginas: list = field(default_factory=list)

    @property
    def tamanio(self):
        return self.limite


class MemoriaSegmentadaPaginada(GestorMemoria):
    modo = "segmentada_paginada"

    def __init__(self, tamanio_total, tam_pagina=8):
        if tam_pagina <= 0:
            raise ValueError("El tamaño de página debe ser mayor que cero.")
        self.tamanio_total = tamanio_total
        self.tam_pagina = tam_pagina
        self.nombre = f"Segmentación paginada (pág={tam_pagina} MB)"
        self.tamanios_marco = []
        restante = tamanio_total
        while restante > 0:
            t = min(tam_pagina, restante)
            self.tamanios_marco.append(t)
            restante -= t
        self.num_marcos = len(self.tamanios_marco)
        self.offsets_marco = []
        base = 0
        for t in self.tamanios_marco:
            self.offsets_marco.append(base)
            base += t
        self.marcos = [None] * self.num_marcos  # "PID:Sj" o None
        # Tabla de segmentos por proceso: pid -> [EntradaSegmentoSP],
        # cada una con su propia tabla de páginas.
        self.tabla = {}

    def obtener_tabla(self, pid):
        """Devuelve la tabla de segmentos del proceso."""
        return list(self.tabla.get(pid, []))

    def asignar(self, proceso) -> bool:
        if proceso.pid in self.tabla:
            return True
        partes = dividir_segmentos(proceso.memoria)
        # Páginas necesarias por segmento y total.
        paginas_por_seg = [math.ceil(t / self.tam_pagina) for t in partes]
        total = sum(paginas_por_seg)
        libres = [i for i, v in enumerate(self.marcos) if v is None]
        if len(libres) < total:
            return False
        entradas = []
        k = 0
        for j, tam in enumerate(partes):
            n = paginas_por_seg[j]
            marcos_seg = libres[k:k + n]
            k += n
            etiqueta = f"{proceso.pid}:S{j}"
            for i in marcos_seg:
                self.marcos[i] = etiqueta
            nombre = NOMBRES_SEG[j] if j < len(NOMBRES_SEG) else f"Seg{j}"
            entradas.append(EntradaSegmentoSP(
                seg=j, nombre=nombre, limite=tam,
                tabla_paginas=[EntradaPaginaSP(pagina=q, marco=m)
                               for q, m in enumerate(marcos_seg)]))
        self.tabla[proceso.pid] = entradas
        proceso.estado = "Listo"
        return True

    def liberar(self, pid) -> None:
        entradas = self.tabla.pop(pid, None)
        if not entradas:
            return
        for e in entradas:
            for ep in e.tabla_paginas:
                self.marcos[ep.marco] = None

    def traducir(self, pid, segmento, desplazamiento):
        """Traducción en dos niveles: segmento -> página -> marco.

        Verifica 0 <= desplazamiento < límite del segmento; si se excede,
        lanza ViolacionSegmento.
        Devuelve {"segmento", "nombre", "desplazamiento", "limite",
                  "pagina_en_seg", "desplazamiento_pagina", "marco",
                  "direccion_fisica"}.
        """
        if pid not in self.tabla:
            raise KeyError(f"El proceso '{pid}' no está en memoria.")
        entradas = self.tabla[pid]
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
        pagina_en_seg = desplazamiento // self.tam_pagina
        desp_en_pag = desplazamiento % self.tam_pagina
        if pagina_en_seg >= len(entrada.tabla_paginas):
            raise ValueError(
                f"La página {pagina_en_seg} no existe en '{pid}:S{segmento}'.")
        marco = entrada.tabla_paginas[pagina_en_seg].marco
        return {
            "segmento": segmento,
            "nombre": entrada.nombre,
            "desplazamiento": desplazamiento,
            "limite": entrada.limite,
            "pagina_en_seg": pagina_en_seg,
            "desplazamiento_pagina": desp_en_pag,
            "marco": marco,
            "direccion_fisica": self.offsets_marco[marco] + desp_en_pag,
        }

    def memoria_libre_total(self) -> int:
        return sum(
            self.tamanios_marco[i]
            for i, v in enumerate(self.marcos)
            if v is None
        )

    def fragmentacion_interna(self) -> int:
        return sum(
            len(e.tabla_paginas) * self.tam_pagina - e.limite
            for entradas in self.tabla.values()
            for e in entradas
        )

    def info_resumen(self):
        ocupados = sum(1 for v in self.marcos if v is not None)
        return (
            f"{self.nombre}\n"
            f"Marcos: {ocupados}/{self.num_marcos} ocupados\n"
            f"Libre total: {self.memoria_libre_total()} MB\n"
            f"Fragmentación externa: 0 MB (paginada)\n"
            f"Fragmentación interna: {self.fragmentacion_interna()} MB"
        )

    def bloques_visuales(self):
        items = []
        for i, etiqueta in enumerate(self.marcos):
            tam = self.tamanios_marco[i]
            if etiqueta is None:
                items.append((None, tam, f"LIBRE\n{tam} MB"))
            else:
                items.append((etiqueta, tam, f"{etiqueta}\nM{i}"))
        return items
