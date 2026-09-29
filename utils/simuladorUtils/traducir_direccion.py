"""Traductor interactivo de direcciones (requisitos 4 en la UI)."""
from controllers.memoria.segmentacion import ViolacionSegmento
from utils.simuladorUtils.registrar import registrar


def traducir_direccion(self):
    """Traduce según el modo activo y reporta violaciones.

    - Paginación: PID + dirección lógica -> (pág,desp)->(marco,desp).
    - Segmentación: PID + segmento + desplazamiento -> dirección física,
      verificando desplazamiento < límite; cada violación se registra
      en el panel de eventos además de mostrarse en el resultado.
    - Segmentación paginada: igual que segmentación pero en dos niveles
      (segmento -> página -> marco).
    """
    lbl = getattr(self, "lbl_traduccion", None)
    mem = getattr(self, "memoria", None)

    def mostrar(texto):
        if lbl is not None:
            try:
                lbl.config(text=texto)
            except Exception:
                pass

    if mem is None:
        mostrar("Inicie una simulación para traducir direcciones.")
        return
    modo = getattr(mem, "modo", "")
    if modo not in ("paginacion", "segmentacion", "segmentada_paginada"):
        mostrar("Traducción disponible en Paginación, Segmentación y "
                "Segmentación paginada.")
        return
    try:
        pid_raw = self.entry_trad_pid.get().strip()
    except AttributeError:
        mostrar("Ingrese el PID del proceso.")
        return
    if not pid_raw:
        mostrar("Ingrese el PID del proceso.")
        return
    try:
        pid = int(pid_raw)
    except ValueError:
        pid = pid_raw

    if modo in ("segmentacion", "segmentada_paginada"):
        try:
            seg = int(self.entry_trad_seg.get().strip())
            desp = int(self.entry_trad_dir.get().strip())
        except (AttributeError, ValueError):
            mostrar("En segmentación ingrese segmento y desplazamiento enteros.")
            return
        try:
            r = mem.traducir(pid, seg, desp)
        except KeyError as e:
            mostrar(f"Error: {e}")
            return
        except ValueError as e:
            mostrar(f"Error: {e}")
            return
        except ViolacionSegmento as e:
            try:
                registrar(self, f"Violación de segmento: {e}")
            except Exception:
                pass
            mostrar(f"Violación de segmento: {e}")
            return
        if modo == "segmentada_paginada":
            mostrar(
                f"{pid}:S{r['segmento']} ({r['nombre']}) desp {r['desplazamiento']} "
                f"< límite {r['limite']} -> página p{r['pagina_en_seg']} "
                f"-> marco M{r['marco']} (física {r['direccion_fisica']})"
            )
            return
        mostrar(
            f"{pid}:S{r['segmento']} ({r['nombre']}) desp {r['desplazamiento']} "
            f"< límite {r['limite']} -> base {r['base']} "
            f"(física {r['direccion_fisica']})"
        )
        return

    try:
        direccion = int(self.entry_trad_dir.get().strip())
    except (AttributeError, ValueError):
        mostrar("Ingrese PID y dirección lógica entera (ej: 1, 20).")
        return
    try:
        r = mem.traducir(pid, direccion)
    except (KeyError, ValueError) as e:
        mostrar(f"Error: {e}")
        return
    mostrar(
        f"{pid}[{direccion}] -> página {r['pagina']}, desp {r['desplazamiento']} "
        f"-> marco M{r['marco']}, desp {r['desplazamiento']} "
        f"(física {r['direccion_fisica']})"
    )
