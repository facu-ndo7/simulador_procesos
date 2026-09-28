"""Interfaz común para todos los gestores de memoria."""
from abc import ABC, abstractmethod


class GestorMemoria(ABC):
    """Contrato mínimo que debe cumplir cada modo de gestión.

    Todos los gestores son intercambiables en tiempo de ejecución:
    el simulador solo usa estos métodos, nunca detalles internos.
    """

    tamanio_total: int
    modo: str = "base"
    nombre: str = "Gestor base"

    @abstractmethod
    def asignar(self, proceso) -> bool:
        """Intenta cargar el proceso. Devuelve True si lo logra."""
        raise NotImplementedError

    @abstractmethod
    def liberar(self, pid) -> None:
        """Libera todo lo ocupado por el pid."""
        raise NotImplementedError

    @abstractmethod
    def memoria_libre_total(self) -> int:
        raise NotImplementedError

    def fragmentacion_externa(self) -> int:
        """Compatibilidad con la vista original. Por defecto 0."""
        return 0

    def info_resumen(self) -> str:
        return (
            f"{self.nombre}\n"
            f"Libre total: {self.memoria_libre_total()} MB"
        )

    @abstractmethod
    def bloques_visuales(self):
        """Lista ordenada de (pid_o_None, tamanio, etiqueta) para dibujar.

        Permite que un único dibujador genérico visualice cualquier modo:
        - contigua/segmentación: un item por bloque/segmento/hueco.
        - paginación/seg-paginada: un item por marco.
        """
        raise NotImplementedError

    def simular_ejecucion(self, proceso, unidades):
        """Hook de memoria virtual. Resto de gestores: sin efecto."""
        return {"hits": 0, "faults": 0, "swaps": 0, "detalle": []}
