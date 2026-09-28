"""Cambio de modo de memoria en caliente, sin reiniciar la simulación."""
from collections import deque
from tkinter import messagebox

import controllers.memoriaController as mc
from utils.simuladorUtils.actualizar_vistas import actualizar_vistas
from utils.simuladorUtils.registrar import registrar


def _leer_entero_optimo(self, nombre_attr, defecto):
    if not hasattr(self, nombre_attr):
        return defecto
    try:
        raw = getattr(self, nombre_attr).get().strip()
    except Exception:
        return defecto
    if not raw:
        return defecto
    try:
        return int(raw)
    except ValueError:
        return None


def cambiar_modo_memoria(self):
    """Reemplaza el gestor actual preservando tiempo, CPU e historial."""
    if not self.simulacion_activa or self.memoria is None:
        messagebox.showwarning(
            "Sin simulación",
            "Inicie una simulación antes de cambiar el modo de memoria."
        )
        return

    modo = self.combo_modo_mem.get() if hasattr(self, "combo_modo_mem") else ""
    ajuste = self.combo_ajuste_mem.get() if hasattr(self, "combo_ajuste_mem") else "First-Fit"
    reemplazo = self.combo_reemplazo.get() if hasattr(self, "combo_reemplazo") else getattr(self, "reemplazo", "LRU")
    tam_pagina = _leer_entero_optimo(self, "entry_tam_pagina", 8)
    if tam_pagina is None:
        messagebox.showerror(
            "Página inválida",
            "El tamaño de página debe ser un número entero."
        )
        return
    if tam_pagina <= 0:
        messagebox.showerror(
            "Página inválida",
            "El tamaño de página debe ser mayor que cero."
        )
        return
    try:
        fisica_ui = int(self.entry_mem_total.get().strip())
    except (ValueError, AttributeError):
        fisica_ui = self.memoria.tamanio_total
    tam_virtual = _leer_entero_optimo(self, "entry_mem_virtual",
                                      getattr(self, "tam_virtual", fisica_ui))
    if tam_virtual is None:
        messagebox.showerror(
            "Memoria inválida",
            "La memoria virtual debe ser un número entero."
        )
        return

    modo_norm = mc.normalizar_modo(modo)
    if modo_norm in ("Paginación", "Segmentación paginada",
                     "Memoria virtual") and tam_pagina > self.memoria.tamanio_total:
        # En virtual la física puede haber crecido en el entry: se valida abajo.
        if not (modo_norm == "Memoria virtual" and tam_pagina <= fisica_ui):
            messagebox.showerror(
                "Página inválida",
                "El tamaño de página no puede superar la memoria total."
            )
            return
    if modo_norm == "Memoria virtual" and tam_virtual < fisica_ui:
        messagebox.showerror(
            "Memoria inválida",
            "La memoria virtual debe ser mayor o igual que la física."
        )
        return

    # Caso especial: resize en caliente dentro de memoria virtual.
    # Se preservan marcos y estadísticas sin recrear el gestor.
    if (modo_norm == "Memoria virtual"
            and getattr(self.memoria, "modo", None) == "virtual"):
        return _redimensionar_virtual_en_caliente(
            self, fisica_ui, tam_virtual, tam_pagina, reemplazo, ajuste)

    # Si nada cambió, no hay nada que migrar.
    if (modo_norm == getattr(self, "modo_mem", None)
            and ajuste == getattr(self, "ajuste_mem", ajuste)
            and tam_pagina == getattr(self, "tam_pagina", tam_pagina)):
        messagebox.showinfo("Sin cambios", "El modo de memoria ya está activo.")
        return

    total = fisica_ui
    try:
        nuevo = mc.crear_gestor(modo_norm, total, ajuste=ajuste,
                                tam_pagina=tam_pagina,
                                tamanio_virtual=tam_virtual,
                                reemplazo=reemplazo)
    except ValueError as e:
        messagebox.showerror("Memoria inválida", str(e))
        return

    # Residentes = todo proceso_sim no finalizado y no en espera.
    # (proceso_actual en RR/FIFO ya está reencolado o finalizado al terminar
    # el paso, pero se incluye por seguridad si quedó en Ejecución).
    residentes = []
    vistos = set()
    candidatos = []
    candidatos.extend(getattr(self, "listos", []))
    candidatos.extend(list(getattr(self, "cola_rr", deque())))
    if getattr(self, "proceso_actual", None) is not None:
        candidatos.append(self.proceso_actual)
    for p in getattr(self, "procesos_sim", []):
        if p.estado in ("Listo", "Ejecutando") and p.pid not in vistos:
            vistos.add(p.pid)
            residentes.append(p)
    # Preserva el orden de llegada original.
    orden = {p.pid: i for i, p in enumerate(getattr(self, "procesos_sim", []))}
    residentes.sort(key=lambda p: orden.get(p.pid, 0))

    limite_nuevo = getattr(nuevo, "tamanio_virtual", total)
    espera_previa = list(getattr(self, "espera_memoria", []))
    nuevos_en_espera = []
    for p in residentes:
        if p.memoria > limite_nuevo or not nuevo.asignar(p):
            p.estado = "Esperando memoria"
            nuevos_en_espera.append(p)
    # Reintenta la espera previa en el nuevo gestor.
    # (Los que ahora sí caben deben entrar a las colas de CPU.)
    for p in espera_previa:
        if p.memoria > limite_nuevo or not nuevo.asignar(p):
            p.estado = "Esperando memoria"

    # Reconstruye colas de CPU con todo lo admitido (residentes + reingresos),
    # en orden de llegada original.
    orden = {p.pid: i for i, p in enumerate(getattr(self, "procesos_sim", []))}
    admitidos = sorted(
        (p for p in getattr(self, "procesos_sim", []) if p.estado == "Listo"),
        key=lambda p: orden.get(p.pid, 0))
    if self.alg_cpu == "Round-Robin":
        self.cola_rr = deque(admitidos)
        self.listos = list(admitidos)
    else:
        self.listos = list(admitidos)
        if self.alg_cpu == "SJF no apropiativo":
            self.listos.sort(key=lambda p: p.rafaga)
    self.espera_memoria = [p for p in getattr(self, "procesos_sim", [])
                           if p.estado == "Esperando memoria"]
    ok_pids = {p.pid for p in admitidos}

    # Si el proceso_actual quedó en espera, se limpia para no mostrarlo.
    if self.proceso_actual is not None and self.proceso_actual.estado == "Esperando memoria":
        self.proceso_actual = None

    self.memoria = nuevo
    self.modo_mem = modo_norm
    self.ajuste_mem = ajuste
    self.tam_pagina = tam_pagina
    self.tam_virtual = getattr(nuevo, "tamanio_virtual", total)
    self.reemplazo = getattr(nuevo, "reemplazo", reemplazo)
    self.alg_mem = nuevo.nombre

    registrar(
        self,
        f"Cambio de memoria en caliente a {nuevo.nombre} "
        f"(tiempo={self.tiempo}, sin reiniciar). "
        f"Residentes reubicados: {len(ok_pids)}; "
        f"en espera: {len(self.espera_memoria)}."
    )
    for p in nuevos_en_espera:
        registrar(self, f"{p.pid} no cupo en {nuevo.nombre} y pasa a espera.")
    actualizar_vistas(self)


def _redimensionar_virtual_en_caliente(self, fisica_ui, tam_virtual,
                                       tam_pagina, reemplazo, ajuste):
    """Aumenta física / cambia página / virtual sin reiniciar."""
    mem = self.memoria
    cambios = []
    # Reemplazo: cambio inmediato, sin mover páginas.
    if reemplazo in ("LRU", "FIFO") and reemplazo != mem.reemplazo:
        mem.reemplazo = reemplazo
        self.reemplazo = reemplazo
        mem.nombre = (f"Memoria virtual (fís={mem.tamanio_fisica} MB, "
                      f"virt={mem.tamanio_virtual} MB, pág={mem.tam_pagina} MB, "
                      f"{reemplazo})")
        cambios.append(f"reemplazo={reemplazo}")
    # Memoria virtual total: solo puede crecer por debajo del compromiso.
    if tam_virtual != mem.tamanio_virtual:
        comprometido = sum(e["tamanio"] for e in mem.tabla.values())
        if tam_virtual < max(comprometido, mem.tamanio_fisica):
            messagebox.showerror(
                "Memoria inválida",
                f"No se puede reducir la virtual a {tam_virtual} MB: "
                f"hay {comprometido} MB comprometidos."
            )
            return
        mem.tamanio_virtual = tam_virtual
        self.tam_virtual = tam_virtual
        mem.nombre = (f"Memoria virtual (fís={mem.tamanio_fisica} MB, "
                      f"virt={tam_virtual} MB, pág={mem.tam_pagina} MB, "
                      f"{mem.reemplazo})")
        cambios.append(f"virtual={tam_virtual} MB")
    # Memoria física: solo aumento (requisito).
    if fisica_ui != mem.tamanio_fisica:
        if fisica_ui < mem.tamanio_fisica:
            messagebox.showerror(
                "Memoria inválida",
                "En caliente solo se puede aumentar la memoria física "
                "(para reducir, reinicie la simulación)."
            )
            return
        previa = mem.tamanio_fisica
        try:
            mem.redimensionar_fisica(fisica_ui)
        except ValueError as e:
            messagebox.showerror("Memoria inválida", str(e))
            return
        cambios.append(f"física={fisica_ui} MB (+{fisica_ui - previa} MB)")
    # Tamaño de página: re-pagina con recarga de páginas 0.
    if tam_pagina != mem.tam_pagina:
        try:
            mem.redimensionar_pagina(tam_pagina)
        except ValueError as e:
            messagebox.showerror("Página inválida", str(e))
            return
        self.tam_pagina = tam_pagina
        cambios.append(f"página={tam_pagina} MB (re-paginado)")
    self.ajuste_mem = ajuste
    self.alg_mem = mem.nombre
    if not cambios:
        messagebox.showinfo("Sin cambios", "El modo de memoria ya está activo.")
        return
    # Tras agrandar la física, reintenta la espera (puede que quepan más
    # páginas, aunque en virtual la admisión depende del cupo virtual).
    reingresos = []
    for p in self.espera_memoria[:]:
        if p.memoria <= mem.tamanio_virtual and mem.asignar(p):
            self.espera_memoria.remove(p)
            reingresos.append(p)
    if self.alg_cpu == "Round-Robin":
        for p in reingresos:
            self.cola_rr.append(p)
        self.listos = [p for p in self.procesos_sim if p.estado == "Listo"]
    else:
        self.listos.extend(reingresos)
        if self.alg_cpu == "SJF no apropiativo":
            self.listos.sort(key=lambda p: p.rafaga)
    registrar(
        self,
        f"Redimensión virtual en caliente (tiempo={self.tiempo}): "
        + ", ".join(cambios) + "."
    )
    for p in reingresos:
        registrar(self, f"{p.pid} ingresa desde la espera tras el resize.")
    actualizar_vistas(self)
