"""Vista en tiempo real de las tablas de páginas (requisito 5)."""


def actualizar_tabla_paginas(self):
    """Refresca el visor página -> marco tras cada evento.

    - Paginación: una fila por entrada (proceso, página, marco, base física).
    - Memoria virtual: agrega estado residente/en swap.
    - Otros modos o sin simulación: fila informativa.
    Es tolerante a objetos sin widgets (tests sin GUI).
    """
    vista = getattr(self, "tabla_paginas_view", None)
    if vista is None:
        return
    try:
        for item in vista.get_children():
            vista.delete(item)
    except Exception:
        return

    mem = getattr(self, "memoria", None)
    if mem is None:
        vista.insert("", "end", values=("Sin simulación", "", "", ""))
        return

    modo = getattr(mem, "modo", "")
    if modo == "segmentada_paginada":
        filas = 0
        for pid, entradas in mem.tabla.items():
            for e in entradas:
                vista.insert("", "end", values=(
                    pid, f"S{e.seg} {e.nombre} (lím {e.limite})", "", ""))
                filas += 1
                for ep in e.tabla_paginas:
                    vista.insert("", "end", values=(
                        "", f"  p{ep.pagina}", f"M{ep.marco}",
                        f"{pid}:S{e.seg}"))
                    filas += 1
        if not filas:
            vista.insert("", "end", values=("Sin procesos residentes", "", "", ""))
    elif modo == "segmentacion":
        filas = 0
        for pid, entradas in mem.tabla_segmentos.items():
            for e in entradas:
                vista.insert("", "end", values=(
                    pid, f"S{e.seg} {e.nombre}", f"base {e.base}",
                    f"límite {e.limite}"))
                filas += 1
        if not filas:
            vista.insert("", "end", values=("Sin procesos residentes", "", "", ""))
    elif modo == "paginacion":
        filas = 0
        for pid, entradas in mem.tabla_paginas.items():
            for e in entradas:
                base = mem.offsets_marco[e.marco]
                vista.insert("", "end", values=(
                    pid, f"p{e.pagina}", f"M{e.marco}",
                    f"física base {base}"))
                filas += 1
        if not filas:
            vista.insert("", "end", values=("Sin procesos residentes", "", "", ""))
    elif modo == "virtual":
        filas = 0
        for pid, entrada in mem.tabla.items():
            for pag in range(entrada["num_paginas"]):
                if entrada["presente"][pag]:
                    marco = entrada["marco"][pag]
                    vista.insert("", "end", values=(
                        pid, f"p{pag}", f"M{marco}", "residente"))
                else:
                    vista.insert("", "end", values=(
                        pid, f"p{pag}", "-", "en swap"))
                filas += 1
        if not filas:
            vista.insert("", "end", values=("Sin procesos residentes", "", "", ""))
    else:
        vista.insert("", "end",
                     values=("No aplica al modo actual", "", "", ""))
