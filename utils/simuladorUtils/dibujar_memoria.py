def dibujar_memoria(self):
    c = self.canvas_memoria
    c.delete("all")


    if not self.memoria:
        c.create_text(
            160,
            210,
            text="Inicie una simulación\npara visualizar la memoria",
            justify="center"
        )
        self.lbl_memoria_info.config(text="Memoria no inicializada")
        return

    # Vista polimórfica: cada gestor describe sus bloques/marcos en orden.
    if hasattr(self.memoria, "bloques_visuales"):
        items = self.memoria.bloques_visuales()
        total = getattr(self.memoria, "tamanio_total", 0) or 0
    else:  # Compatibilidad con gestores legacy con atributo .bloques.
        items = []
        for bloque in self.memoria.bloques:
            if bloque.libre:
                items.append((None, bloque.tamanio, f"LIBRE\n{bloque.tamanio} MB"))
            else:
                items.append((bloque.pid, bloque.tamanio, f"{bloque.pid}\n{bloque.tamanio} MB"))
        total = self.memoria.tamanio_total


    ancho = max(c.winfo_width(), 300)
    alto = max(c.winfo_height(), 400)


    x1 = 45
    x2 = ancho - 45
    y = 20
    alto_util = alto - 40


    colores = [
        "#8ecae6",
        "#ffb703",
        "#90be6d",
        "#f28482",
        "#cdb4db",
        "#84a59d"
    ]
    mapa_colores = {}


    for pid, tamanio, texto in items:
        proporcion = (tamanio / total) if total else 0
        h = max(24, alto_util * proporcion)


        if pid is None:
            color = "#eeeeee"
        else:
            clave = str(pid).split(":")[0]
            if clave not in mapa_colores:
                mapa_colores[clave] = colores[len(mapa_colores) % len(colores)]
            color = mapa_colores[clave]


        c.create_rectangle(
            x1, y, x2, y + h,
            fill=color,
            outline="#444"
        )
        c.create_text(
            (x1 + x2) / 2,
            y + h / 2,
            text=texto,
            justify="center",
            font=("Arial", 11, "bold")
        )

        y += h


    c.create_text(
        x1 - 8,
        min(y, alto - 10),
        text=str(total),
        anchor="e"
    )


    if hasattr(self.memoria, "info_resumen"):
        resumen = self.memoria.info_resumen()
    else:
        resumen = (
            f"Libre total: {self.memoria.memoria_libre_total()} MB\n"
            f"Fragmentación externa: "
            f"{self.memoria.fragmentacion_externa()} MB"
        )
    # Fragmentación interna: la paginación simple ya la incluye en su
    # info_resumen (calculada por el propio gestor); aquí solo se agrega
    # para gestores que no la informan por sí mismos.
    try:
        from controllers.memoria.virtual import MemoriaVirtual
        from controllers.memoria.segmentada_paginada import MemoriaSegmentadaPaginada
        if isinstance(self.memoria, MemoriaVirtual):
            en_swap = self.memoria.swap_visuales()
            resumen += (
                f"\nSwap (disco): {self.memoria.swap_ocupado_paginas()} págs"
            )
            if en_swap:
                resumen += " [" + ", ".join(en_swap) + "]"
        elif isinstance(self.memoria, MemoriaSegmentadaPaginada):
            resumen += (f"\nFragmentación interna: "
                        f"{self.memoria.fragmentacion_interna()} MB")
    except Exception:
        pass
    self.lbl_memoria_info.config(text=resumen)
