"""Hook de memoria virtual: simula accesos durante la ráfaga ejecutada."""
from utils.simuladorUtils.registrar import registrar


def simular_accesos_virtuales(self, proceso, unidades):
    """Ejecuta referencias por demanda y registra fallos/swaps.

    No-op para gestores no virtuales (devuelven ceros).
    Devuelve el dict {"hits", "faults", "swaps", "detalle"} o None.
    """
    mem = getattr(self, "memoria", None)
    if mem is None or unidades <= 0:
        return None
    simular = getattr(mem, "simular_ejecucion", None)
    if simular is None:
        return None
    try:
        res = simular(proceso, int(unidades))
    except Exception:
        return None
    if not res or (not res.get("faults") and not res.get("hits")):
        return res
    detalle = ""
    if res.get("detalle"):
        detalle = " (" + "; ".join(res["detalle"]) + ")"
        if res["faults"] > len(res["detalle"]):
            detalle = detalle[:-1] + f"; ... +{res['faults'] - len(res['detalle'])} más)"
    registrar(
        self,
        f"{proceso.pid}: {unidades}u CPU -> memoria virtual: "
        f"{res.get('hits', 0)} aciertos, {res.get('faults', 0)} fallos, "
        f"{res.get('swaps', 0)} swaps{detalle}."
    )
    return res
