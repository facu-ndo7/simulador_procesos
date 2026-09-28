"""Fábrica de gestores intercambiables."""
from controllers.memoria.contigua import MemoriaContigua
from controllers.memoria.paginacion import MemoriaPaginada
from controllers.memoria.segmentacion import MemoriaSegmentada
from controllers.memoria.segmentada_paginada import MemoriaSegmentadaPaginada
from controllers.memoria.virtual import MemoriaVirtual

MODOS_MEMORIA = [
    "Asignación contigua",
    "Paginación",
    "Segmentación",
    "Segmentación paginada",
    "Memoria virtual",
]

_ALIAS = {
    "asignación contigua": "Asignación contigua",
    "asignacion contigua": "Asignación contigua",
    "contigua": "Asignación contigua",
    "paginación": "Paginación",
    "paginacion": "Paginación",
    "segmentación": "Segmentación",
    "segmentacion": "Segmentación",
    "segmentación paginada": "Segmentación paginada",
    "segmentacion paginada": "Segmentación paginada",
    "memoria virtual": "Memoria virtual",
    "virtual": "Memoria virtual",
    # Compatibilidad con valores viejos del combo (First/Best/Worst-Fit).
    "first-fit": "Asignación contigua",
    "best-fit": "Asignación contigua",
    "worst-fit": "Asignación contigua",
}


def normalizar_modo(modo):
    if not modo:
        return MODOS_MEMORIA[0]
    clave = str(modo).strip().lower()
    return _ALIAS.get(clave, str(modo).strip())


def crear_gestor(modo, tamanio_total, ajuste="First-Fit", tam_pagina=8,
                 tamanio_virtual=None, reemplazo="LRU"):
    modo = normalizar_modo(modo)
    if tamanio_total <= 0:
        raise ValueError("La memoria total debe ser mayor que cero.")
    if modo == "Memoria virtual":
        if tamanio_virtual is None:
            tamanio_virtual = tamanio_total * 4
        return MemoriaVirtual(
            tamanio_fisica=tamanio_total,
            tamanio_virtual=tamanio_virtual,
            tam_pagina=tam_pagina,
            reemplazo=reemplazo,
        )
    if modo == "Paginación":
        return MemoriaPaginada(tamanio_total, tam_pagina=tam_pagina)
    if modo == "Segmentación":
        return MemoriaSegmentada(tamanio_total, ajuste=ajuste)
    if modo == "Segmentación paginada":
        return MemoriaSegmentadaPaginada(tamanio_total, tam_pagina=tam_pagina)
    # Por defecto: asignación contigua.
    if ajuste not in ("First-Fit", "Best-Fit", "Worst-Fit"):
        ajuste = "First-Fit"
    return MemoriaContigua(tamanio_total, ajuste=ajuste)
