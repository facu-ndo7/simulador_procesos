"""Paquete de gestores de memoria intercambiables."""
from controllers.memoria.base import GestorMemoria
from controllers.memoria.contigua import MemoriaContigua
from controllers.memoria.paginacion import MemoriaPaginada
from controllers.memoria.segmentacion import MemoriaSegmentada
from controllers.memoria.segmentada_paginada import MemoriaSegmentadaPaginada
from controllers.memoria.virtual import MemoriaVirtual
from controllers.memoria.factory import (
    MODOS_MEMORIA,
    crear_gestor,
    normalizar_modo,
)

__all__ = [
    "GestorMemoria",
    "MemoriaContigua",
    "MemoriaPaginada",
    "MemoriaSegmentada",
    "MemoriaSegmentadaPaginada",
    "MemoriaVirtual",
    "MODOS_MEMORIA",
    "crear_gestor",
    "normalizar_modo",
]
