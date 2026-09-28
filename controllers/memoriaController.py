"""Fachada de compatibilidad + fábrica de gestores intercambiables.

Se mantiene `Memoria` como alias de `MemoriaContigua` para no romper
imports existentes (`controllers.memoriaController as mc`).
El código nuevo debe usar `crear_gestor(...)`.
"""
from controllers.memoria.base import GestorMemoria
from controllers.memoria.contigua import MemoriaContigua
from controllers.memoria.paginacion import MemoriaPaginada
from controllers.memoria.segmentacion import MemoriaSegmentada
from controllers.memoria.segmentada_paginada import MemoriaSegmentadaPaginada
from controllers.memoria.virtual import MemoriaVirtual
from controllers.memoria.factory import MODOS_MEMORIA, crear_gestor, normalizar_modo

# Alias histórico: antes `Memoria` era la única (contigua).
Memoria = MemoriaContigua

__all__ = [
    "GestorMemoria",
    "Memoria",
    "MemoriaContigua",
    "MemoriaPaginada",
    "MemoriaSegmentada",
    "MemoriaSegmentadaPaginada",
    "MemoriaVirtual",
    "MODOS_MEMORIA",
    "crear_gestor",
    "normalizar_modo",
]
