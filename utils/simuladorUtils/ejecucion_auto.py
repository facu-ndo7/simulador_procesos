"""Ejecución automática con pausa (controles iniciar/pausar)."""
from tkinter import messagebox
from utils.simuladorUtils.paso_siguiente import paso_siguiente
from utils.simuladorUtils.registrar import registrar

INTERVALO_MS = 400


def alternar_auto(self):
    """Alterna entre ejecución automática y pausa."""
    if not getattr(self, "simulacion_activa", False):
        messagebox.showwarning("Sin simulación",
                               "Inicie una simulación antes del modo auto.")
        return
    self.auto = not getattr(self, "auto", False)
    if hasattr(self, "btn_auto"):
        try:
            self.btn_auto.config(text="Pausar" if self.auto else "Auto")
        except Exception:
            pass
    if self.auto:
        registrar(self, "Ejecución automática iniciada (Auto).")
        self.after(INTERVALO_MS, lambda: _paso_auto(self))
    else:
        registrar(self, f"Ejecución pausada en tiempo {self.tiempo}.")


def _paso_auto(self):
    if not getattr(self, "auto", False):
        return
    if not getattr(self, "simulacion_activa", False):
        detener_auto(self)
        return
    paso_siguiente(self)
    if getattr(self, "simulacion_activa", False) and getattr(self, "auto", False):
        self.after(INTERVALO_MS, lambda: _paso_auto(self))
    else:
        detener_auto(self)


def detener_auto(self):
    self.auto = False
    if hasattr(self, "btn_auto"):
        try:
            self.btn_auto.config(text="Auto")
        except Exception:
            pass
