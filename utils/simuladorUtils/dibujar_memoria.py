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


    ancho_real = c.winfo_width()
    alto_real = c.winfo_height()
    # Usar el tamaño real del canvas: el anterior max(..., 400) dibujaba
    # más alto que el canvas visible y los últimos bloques quedaban
    # aplastados/cortados abajo.
    ancho = ancho_real if ancho_real > 50 else 320
    alto = alto_real if alto_real > 50 else 370


    x1 = 45
    # Margen derecho reservado para etiquetar bloques muy pequeños fuera
    # del rectángulo sin superponer textos.
    x2 = ancho - 110
    if x2 < x1 + 80:
        x2 = ancho - 45
    y0 = 20
    alto_util = max(alto - 40, 60)


    colores = [
        "#8ecae6",
        "#ffb703",
        "#90be6d",
        "#f28482",
        "#cdb4db",
        "#84a59d"
    ]
    mapa_colores = {}


    # Alturas proporcionales al tamaño, escaladas para que la suma
    # encaje EXACTO en alto_util. El anterior max(24, ...) hacía que N
    # bloques pequeños sumaran más que el canvas y se amontonaran abajo.
    brutos = [(alto_util * tamanio / total) if total else 0
              for _, tamanio, _ in items]
    MIN_H = 6.0
    alturas = [max(MIN_H, b) if t > 0 else 0.0
               for b, (_, t, _) in zip(brutos, items)]
    suma = sum(alturas)
    if suma > alto_util and suma > 0:
        factor = alto_util / suma
        alturas = [h * factor for h in alturas]

    y = y0
    ultimo_y_etiqueta = -100.0
    for (pid, tamanio, texto), h in zip(items, alturas):


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
        # Etiquetas sin amontonar: dentro si hay lugar, fuera (y con
        # anti-colisión) si el bloque es muy bajo.
        primera_linea = str(texto).split("\n")[0] if texto else ""
        if h >= 30:
            c.create_text(
                (x1 + x2) / 2,
                y + h / 2,
                text=texto,
                justify="center",
                font=("Arial", 10, "bold")
            )
        elif h >= 15:
            c.create_text(
                (x1 + x2) / 2,
                y + h / 2,
                text=primera_linea,
                justify="center",
                font=("Arial", 9, "bold")
            )
        elif primera_linea:
            yc = y + h / 2
            if yc - ultimo_y_etiqueta >= 12:
                c.create_text(
                    x2 + 6,
                    yc,
                    text=primera_linea,
                    anchor="w",
                    font=("Arial", 8)
                )
                ultimo_y_etiqueta = yc

        y += h


    c.create_text(x1 - 8, y0, text="0", anchor="e")
    c.create_text(
        x1 - 8,
        min(y, alto - 10),
        text=str(total),
        anchor="e"
    )
    c.configure(scrollregion=c.bbox("all"))


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
            resumen += (f"\nTasa de fallos: {self.memoria.tasa_fallos():.1f}% "
                        f"({self.memoria.fallos}/{self.memoria.accesos})")
            resumen += f"\nTMAT: {self.memoria.tmat():.2f} ticks"
        elif isinstance(self.memoria, MemoriaSegmentadaPaginada):
            resumen += (f"\nFragmentación interna: "
                        f"{self.memoria.fragmentacion_interna()} MB")
    except Exception:
        pass
    # Bloque de métricas común a todos los modos (tiempo real).
    try:
        total = getattr(self.memoria, "tamanio_total", 0) or 0
        libre = self.memoria.memoria_libre_total()
        usado = total - libre
        ocup = self.memoria.porcentaje_ocupacion()
        mayor = self.memoria.mayor_bloque_libre()
        ext = self.memoria.fragmentacion_externa()
        frag_int = getattr(self.memoria, "fragmentacion_interna", None)
        intra = frag_int() if callable(frag_int) else 0
        resumen += (f"\nOcupación física: {ocup:.0f}% ({usado}/{total} MB)")
        resumen += f"\nMayor bloque libre: {mayor} MB"
        resumen += (f"\nFragmentación: externa {100.0 * ext / total:.0f}% "
                    f"({ext} MB) · interna {100.0 * intra / total:.0f}% "
                    f"({intra} MB)" if total > 0 else "")
    except Exception:
        pass
    self.lbl_memoria_info.config(text=resumen)
