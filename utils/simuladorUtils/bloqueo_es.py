"""Bloqueo de procesos: solicitud de E/S o espera de un recurso."""
from tkinter import messagebox
from collections import deque
from utils.simuladorUtils.actualizar_vistas import actualizar_vistas
from utils.simuladorUtils.registrar import registrar


def solicitar_es(self):
    """Pasa el primer proceso listo a 'Bloqueado' (conserva su memoria)."""
    if not getattr(self, "simulacion_activa", False):
        messagebox.showwarning("Sin simulación",
                               "Inicie una simulación antes de bloquear.")
        return
    if not hasattr(self, "bloqueados") or self.bloqueados is None:
        self.bloqueados = []
    p = None
    if self.alg_cpu == "Round-Robin":
        if getattr(self, "cola_rr", None):
            p = self.cola_rr.popleft()
            self.listos = [q for q in getattr(self, "listos", []) if q.pid != p.pid]
    else:
        if getattr(self, "listos", None):
            p = self.listos.pop(0)
    if p is None:
        messagebox.showwarning("Sin procesos listos",
                               "No hay procesos en Listo para bloquear.")
        return
    p.estado = "Bloqueado"
    self.bloqueados.append(p)
    if getattr(self, "proceso_actual", None) is not None and self.proceso_actual.pid == p.pid:
        self.proceso_actual = None
    registrar(self, f"{p.pid} solicita E/S: pasa a 'Bloqueado' (conserva su memoria).")
    actualizar_vistas(self)


def fin_es(self):
    """Completa la E/S: el primer bloqueado vuelve a Listo."""
    if not getattr(self, "simulacion_activa", False):
        messagebox.showwarning("Sin simulación",
                               "Inicie una simulación antes de desbloquear.")
        return
    if not getattr(self, "bloqueados", None):
        messagebox.showwarning("Sin bloqueados",
                               "No hay procesos en 'Bloqueado'.")
        return
    p = self.bloqueados.pop(0)
    p.estado = "Listo"
    if self.alg_cpu == "Round-Robin":
        if not hasattr(self, "cola_rr") or self.cola_rr is None:
            self.cola_rr = deque()
        self.cola_rr.append(p)
        if p not in getattr(self, "listos", []):
            self.listos.append(p)
    else:
        self.listos.append(p)
        if self.alg_cpu == "SJF no apropiativo":
            self.listos.sort(key=lambda p: p.rafaga)
    registrar(self, f"{p.pid} completa su E/S: vuelve a Listo.")
    actualizar_vistas(self)
