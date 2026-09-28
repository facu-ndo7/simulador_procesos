"""Memoria virtual con paginación por demanda y área swap simulada.

Modelo pedagógico:
- Memoria física dividida en marcos de tamaño fijo (tamanio_fisica).
- Espacio virtual del sistema mayor que la física (tamanio_virtual).
- Cada proceso reserva N = ceil(memoria / tam_pagina) páginas virtuales.
- Carga bajo demanda: al asignar solo se carga la página 0; el resto
  queda en el área swap (estructura en memoria que representa el disco).
- Acceder a una página no residente produce un fallo de página: se trae
  desde swap y, si no hay marco libre, se expulsa una víctima (FIFO/LRU).
- `tamanio_total` se mantiene como alias de la física para compatibilidad
  con el resto del simulador (verificar_fin, dibujado, hot-swap).
"""
import math
from controllers.memoria.base import GestorMemoria


class MemoriaVirtual(GestorMemoria):
    modo = "virtual"

    def __init__(self, tamanio_fisica, tamanio_virtual=None,
                 tam_pagina=8, reemplazo="LRU"):
        if tamanio_fisica <= 0:
            raise ValueError("La memoria física debe ser mayor que cero.")
        if tam_pagina <= 0:
            raise ValueError("El tamaño de página debe ser mayor que cero.")
        if tamanio_virtual is None:
            tamanio_virtual = tamanio_fisica * 4
        if tamanio_virtual <= 0:
            raise ValueError("La memoria virtual debe ser mayor que cero.")
        if tamanio_virtual < tamanio_fisica:
            raise ValueError("La memoria virtual debe ser >= la física.")
        if reemplazo not in ("LRU", "FIFO"):
            reemplazo = "LRU"
        self.tamanio_fisica = tamanio_fisica
        self.tamanio_virtual = tamanio_virtual
        self.tamanio_total = tamanio_fisica  # compatibilidad
        self.tam_pagina = tam_pagina
        self.reemplazo = reemplazo
        self.nombre = (f"Memoria virtual (fís={tamanio_fisica} MB, "
                       f"virt={tamanio_virtual} MB, pág={tam_pagina} MB, {reemplazo})")
        self._construir_marcos(tamanio_fisica, tam_pagina)
        # pid -> {"tamanio": int, "num_paginas": int, "presente": [...],
        #         "marco": [...], "modificada": [...]}
        self.tabla = {}
        self.swap = set()  # {(pid, pagina)}: páginas solo en disco
        self.fallos = 0
        self.aciertos = 0
        self.swaps = 0  # nº de reemplazos (evicción + carga)
        self.accesos = 0
        self._tick = 0
        self._offset_acceso = {}  # pid -> desplazamiento para localidad

    # -- construcción interna -------------------------------------------
    def _construir_marcos(self, fisica, pagina):
        tamanios = []
        restante = fisica
        while restante > 0:
            t = min(pagina, restante)
            tamanios.append(t)
            restante -= t
        self.tamanios_marco = tamanios
        self.num_marcos = len(tamanios)
        self.marcos = [None] * self.num_marcos  # (pid, pagina) o None
        self._uso_reciente = [0] * self.num_marcos   # LRU
        self._seq_carga = [0] * self.num_marcos      # FIFO

    def _comprometido(self):
        return sum(e["tamanio"] for e in self.tabla.values())

    # -- interfaz GestorMemoria ------------------------------------------
    def paginas_necesarias(self, tamanio):
        return math.ceil(tamanio / self.tam_pagina)

    def asignar(self, proceso) -> bool:
        if proceso.pid in self.tabla:
            return True
        if proceso.memoria > self.tamanio_virtual:
            return False
        if self._comprometido() + proceso.memoria > self.tamanio_virtual:
            return False  # cupo virtual del sistema agotado -> espera
        n = self.paginas_necesarias(proceso.memoria)
        self.tabla[proceso.pid] = {
            "tamanio": proceso.memoria,
            "num_paginas": n,
            "presente": [False] * n,
            "marco": [None] * n,
            "modificada": [False] * n,
        }
        self._offset_acceso.setdefault(proceso.pid, 0)
        for pag in range(n):
            self.swap.add((proceso.pid, pag))
        # Carga bajo demanda: solo la página 0 al ingresar.
        self._traer_pagina(proceso.pid, 0)
        proceso.estado = "Listo"
        return True

    def liberar(self, pid) -> None:
        entrada = self.tabla.pop(pid, None)
        if entrada is None:
            return
        for i, contenido in enumerate(self.marcos):
            if contenido is not None and contenido[0] == pid:
                self.marcos[i] = None
        self.swap = {(p, pg) for (p, pg) in self.swap if p != pid}
        self._offset_acceso.pop(pid, None)

    def memoria_libre_total(self) -> int:
        return sum(
            self.tamanios_marco[i]
            for i, contenido in enumerate(self.marcos)
            if contenido is None
        )

    def memoria_virtual_libre(self) -> int:
        return self.tamanio_virtual - self._comprometido()

    def mayor_bloque_libre(self) -> int:
        libres = [self.tamanios_marco[i] for i, contenido in enumerate(self.marcos)
                  if contenido is None]
        return max(libres or [0])

    def fragmentacion_interna(self) -> int:
        return sum(
            e["num_paginas"] * self.tam_pagina - e["tamanio"]
            for e in self.tabla.values()
        )

    def tasa_fallos(self) -> float:
        """% de accesos que fueron fallos de página (0-100)."""
        if self.accesos <= 0:
            return 0.0
        return 100.0 * self.fallos / self.accesos

    def tmat(self) -> float:
        """Tiempo medio de acceso en ticks: 1 por acceso + 1 por fallo
        (carga) + 1 por swap (write-back de la víctima)."""
        if self.accesos <= 0:
            return 1.0
        return (self.accesos + self.fallos + self.swaps) / self.accesos

    def swap_ocupado_paginas(self) -> int:
        return len(self.swap)

    # -- demanda / fallos / swapping --------------------------------------
    def _elegir_victima(self):
        ocupados = [i for i, c in enumerate(self.marcos) if c is not None]
        if not ocupados:
            return None
        if self.reemplazo == "FIFO":
            return min(ocupados, key=lambda i: self._seq_carga[i])
        return min(ocupados, key=lambda i: self._uso_reciente[i])

    def _traer_pagina(self, pid, pagina):
        """Garantiza la página en física. Devuelve ('hit'|'fault', info)."""
        entrada = self.tabla.get(pid)
        if entrada is None or not (0 <= pagina < entrada["num_paginas"]):
            return ("error", "página fuera de rango")
        self._tick += 1
        self.accesos += 1
        if entrada["presente"][pagina]:
            marco = entrada["marco"][pagina]
            self._uso_reciente[marco] = self._tick
            self.aciertos += 1
            return ("hit", f"M{marco}")
        # Fallo de página: traer desde swap.
        self.fallos += 1
        libres = [i for i, c in enumerate(self.marcos) if c is None]
        victima_info = None
        if libres:
            marco = libres[0]
        else:
            marco = self._elegir_victima()
            vpid, vpag = self.marcos[marco]
            self.tabla[vpid]["presente"][vpag] = False
            self.tabla[vpid]["marco"][vpag] = None
            self.swap.add((vpid, vpag))
            victima_info = f"{vpid}:p{vpag} (M{marco})"
            self.swaps += 1  # un intercambio: evicción + carga
        self.marcos[marco] = (pid, pagina)
        entrada["presente"][pagina] = True
        entrada["marco"][pagina] = marco
        self.swap.discard((pid, pagina))
        self._uso_reciente[marco] = self._tick
        self._seq_carga[marco] = self._tick
        return ("fault", victima_info or f"M{marco} libre")

    def acceder(self, pid, pagina, escritura=False):
        tipo, info = self._traer_pagina(pid, pagina)
        if tipo != "error" and escritura and pid in self.tabla:
            self.tabla[pid]["modificada"][pagina] = True
        return tipo, info

    def simular_ejecucion(self, proceso, unidades):
        """Simula referencias de CPU: recorrido secuencial con wrap.

        Cada unidad de CPU genera un acceso. La página referenciada rota
        sobre el espacio virtual del proceso, por lo que con N páginas >
        marcos disponibles se producen fallos y swapping de forma natural.
        Cada 3er acceso se marca como escritura (página modificada).
        """
        if proceso.pid not in self.tabla or unidades <= 0:
            return {"hits": 0, "faults": 0, "swaps": 0, "detalle": []}
        n = self.tabla[proceso.pid]["num_paginas"]
        base = self._offset_acceso.get(proceso.pid, 0)
        hits = faults = 0
        swaps_antes = self.swaps
        detalle = []
        for k in range(unidades):
            pagina = (base + k) % n
            escritura = (k % 3 == 0)
            tipo, info = self.acceder(proceso.pid, pagina, escritura=escritura)
            if tipo == "hit":
                hits += 1
            else:
                faults += 1
                if len(detalle) < 6:
                    detalle.append(f"fallo p{pagina} <- swap ({info})")
        self._offset_acceso[proceso.pid] = (base + unidades) % n
        return {"hits": hits, "faults": faults,
                "swaps": self.swaps - swaps_antes, "detalle": detalle}

    # -- redimensión en caliente ------------------------------------------
    def redimensionar_fisica(self, nuevo_total):
        """Aumenta la memoria física sin reiniciar (agrega marcos)."""
        if nuevo_total <= self.tamanio_fisica:
            raise ValueError("El nuevo tamaño físico debe ser mayor al actual.")
        extra = nuevo_total - self.tamanio_fisica
        resto = extra
        while resto > 0:
            t = min(self.tam_pagina, resto)
            self.tamanios_marco.append(t)
            self.marcos.append(None)
            self._uso_reciente.append(0)
            self._seq_carga.append(0)
            resto -= t
        self.num_marcos = len(self.marcos)
        self.tamanio_fisica = nuevo_total
        self.tamanio_total = nuevo_total
        self.nombre = (f"Memoria virtual (fís={self.tamanio_fisica} MB, "
                       f"virt={self.tamanio_virtual} MB, pág={self.tam_pagina} MB, "
                       f"{self.reemplazo})")

    def redimensionar_pagina(self, nuevo_tam):
        """Cambia el tamaño de página: re-pagina y recarga páginas 0."""
        if nuevo_tam <= 0:
            raise ValueError("El tamaño de página debe ser mayor que cero.")
        if nuevo_tam > self.tamanio_fisica:
            raise ValueError("La página no puede superar la memoria física.")
        if nuevo_tam == self.tam_pagina:
            return
        pids = list(self.tabla.keys())
        tamanios = {pid: self.tabla[pid]["tamanio"] for pid in pids}
        self.tam_pagina = nuevo_tam
        self._construir_marcos(self.tamanio_fisica, nuevo_tam)
        self.tabla = {}
        self.swap = set()
        self._tick = 0
        for pid in pids:
            n = math.ceil(tamanios[pid] / nuevo_tam)
            self.tabla[pid] = {
                "tamanio": tamanios[pid],
                "num_paginas": n,
                "presente": [False] * n,
                "marco": [None] * n,
                "modificada": [False] * n,
            }
            for pag in range(n):
                self.swap.add((pid, pag))
            self._traer_pagina(pid, 0)
        self.nombre = (f"Memoria virtual (fís={self.tamanio_fisica} MB, "
                       f"virt={self.tamanio_virtual} MB, pág={nuevo_tam} MB, "
                       f"{self.reemplazo})")

    # -- vista --------------------------------------------------------------
    def info_resumen(self):
        ocupados = sum(1 for c in self.marcos if c is not None)
        return (
            f"{self.nombre}\n"
            f"Física: {ocupados}/{self.num_marcos} marcos "
            f"(libre {self.memoria_libre_total()} MB)\n"
            f"Virtual comprometida: {self._comprometido()}/{self.tamanio_virtual} MB\n"
            f"Swap: {self.swap_ocupado_paginas()} págs en disco\n"
            f"Accesos: {self.accesos} (aciertos {self.aciertos}, "
            f"fallos {self.fallos}, swaps {self.swaps})"
        )

    def bloques_visuales(self):
        items = []
        for i, contenido in enumerate(self.marcos):
            tam = self.tamanios_marco[i]
            if contenido is None:
                items.append((None, tam, f"LIBRE\n{tam} MB"))
            else:
                pid, pag = contenido
                items.append((pid, tam, f"{pid}:p{pag}\nM{i}"))
        return items

    def swap_visuales(self, max_items=12):
        items = sorted(self.swap)[:max_items]
        return [f"{pid}:p{pag}" for pid, pag in items]
