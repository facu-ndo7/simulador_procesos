"""Paginación: memoria física dividida en marcos de tamaño fijo."""
import math
from dataclasses import dataclass
from controllers.memoria.base import GestorMemoria


@dataclass
class EntradaPagina:
    """Una entrada de la tabla de páginas: página virtual -> marco físico."""
    pagina: int
    marco: int


class MemoriaPaginada(GestorMemoria):
    modo = "paginacion"

    def __init__(self, tamanio_total, tam_pagina=8):
        if tam_pagina <= 0:
            raise ValueError("El tamaño de página debe ser mayor que cero.")
        self.tamanio_total = tamanio_total
        self.tam_pagina = tam_pagina
        self.nombre = f"Paginación (pág={tam_pagina} MB)"
        # Marcos de tamaño fijo; si el total no es múltiplo, el último
        # marco cubre el resto (se informa, no se pierde memoria).
        self.tamanios_marco = []
        restante = tamanio_total
        while restante > 0:
            t = min(tam_pagina, restante)
            self.tamanios_marco.append(t)
            restante -= t
        self.num_marcos = len(self.tamanios_marco)
        # Dirección física base de cada marco (para traducción).
        self.offsets_marco = []
        base = 0
        for t in self.tamanios_marco:
            self.offsets_marco.append(base)
            base += t
        # (pid, pagina) o None: el marco sabe qué página guarda.
        self.marcos = [None] * self.num_marcos
        # Tabla de páginas por proceso: pid -> [EntradaPagina].
        # El índice de la lista es la página virtual; cada entrada guarda
        # el marco físico asignado (todas residentes en paginación simple).
        self.tabla_paginas = {}
        # Tamaño lógico pedido por proceso (para traducción y fragmentación).
        self.tamanios_pedidos = {}

    def paginas_necesarias(self, tamanio):
        return math.ceil(tamanio / self.tam_pagina)

    def marcos_libres(self):
        return [i for i, contenido in enumerate(self.marcos) if contenido is None]

    def asignar(self, proceso) -> bool:
        if proceso.pid in self.tabla_paginas:
            return True
        necesarias = self.paginas_necesarias(proceso.memoria)
        libres = self.marcos_libres()
        if len(libres) < necesarias:
            return False
        elegidos = libres[:necesarias]
        for j, i in enumerate(elegidos):
            self.marcos[i] = (proceso.pid, j)
        self.tabla_paginas[proceso.pid] = [
            EntradaPagina(pagina=j, marco=m) for j, m in enumerate(elegidos)
        ]
        self.tamanios_pedidos[proceso.pid] = proceso.memoria
        proceso.estado = "Listo"
        return True

    def liberar(self, pid) -> None:
        entradas = self.tabla_paginas.pop(pid, [])
        for e in entradas:
            self.marcos[e.marco] = None
        self.tamanios_pedidos.pop(pid, None)

    def obtener_tabla(self, pid):
        """Devuelve la tabla de páginas del proceso ([EntradaPagina])."""
        return list(self.tabla_paginas.get(pid, []))

    def traducir(self, pid, direccion_logica):
        """Traduce dirección lógica -> física.

        (página, desplazamiento) -> (marco, desplazamiento).
        Devuelve {"pagina", "desplazamiento", "marco", "direccion_fisica"}.
        """
        if pid not in self.tabla_paginas:
            raise KeyError(f"El proceso '{pid}' no está en memoria.")
        tamanio = self.tamanios_pedidos.get(pid, 0)
        if not isinstance(direccion_logica, int) or direccion_logica < 0:
            raise ValueError("La dirección lógica debe ser un entero >= 0.")
        if direccion_logica >= tamanio:
            raise ValueError(
                f"Dirección {direccion_logica} fuera del espacio lógico "
                f"de '{pid}' (0..{tamanio - 1})."
            )
        pagina = direccion_logica // self.tam_pagina
        desplazamiento = direccion_logica % self.tam_pagina
        entradas = self.tabla_paginas[pid]
        if pagina >= len(entradas):
            raise ValueError(f"La página {pagina} no existe en '{pid}'.")
        marco = entradas[pagina].marco
        direccion_fisica = self.offsets_marco[marco] + desplazamiento
        return {
            "pagina": pagina,
            "desplazamiento": desplazamiento,
            "marco": marco,
            "direccion_fisica": direccion_fisica,
        }

    def memoria_libre_total(self) -> int:
        return sum(
            self.tamanios_marco[i]
            for i, contenido in enumerate(self.marcos)
            if contenido is None
        )

    def mayor_bloque_libre(self) -> int:
        libres = [self.tamanios_marco[i] for i, contenido in enumerate(self.marcos)
                  if contenido is None]
        return max(libres or [0])

    def fragmentacion_interna_de(self, pid) -> int:
        """Desperdicio por redondeo en la última página del proceso."""
        if pid not in self.tabla_paginas:
            return 0
        n = len(self.tabla_paginas[pid])
        return n * self.tam_pagina - self.tamanios_pedidos.get(pid, 0)

    def fragmentacion_interna(self) -> int:
        return sum(self.fragmentacion_interna_de(pid)
                   for pid in self.tabla_paginas)

    def fragmentacion_interna_procesos(self, procesos) -> int:
        total = 0
        for p in procesos:
            if p.pid in self.tabla_paginas:
                n = len(self.tabla_paginas[p.pid])
                total += n * self.tam_pagina - p.memoria
        return total

    def info_resumen(self):
        ocupados = sum(1 for contenido in self.marcos if contenido is not None)
        return (
            f"{self.nombre}\n"
            f"Marcos: {ocupados}/{self.num_marcos} ocupados\n"
            f"Libre total: {self.memoria_libre_total()} MB\n"
            f"Fragmentación externa: 0 MB (paginación)\n"
            f"Fragmentación interna: {self.fragmentacion_interna()} MB"
        )

    def bloques_visuales(self):
        items = []
        for i, contenido in enumerate(self.marcos):
            tam = self.tamanios_marco[i]
            if contenido is None:
                items.append((None, tam, f"LIBRE\n{tam} MB"))
            else:
                pid, pagina = contenido
                items.append((pid, tam, f"{pid}:p{pagina}\nM{i}"))
        return items
