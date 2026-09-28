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


    for bloque in self.memoria.bloques:
        proporcion = bloque.tamanio / self.memoria.tamanio_total
        h = max(24, alto_util * proporcion)


        if bloque.libre:
            color = "#eeeeee"
            texto = f"LIBRE\n{bloque.tamanio} MB"
        else:
            if bloque.pid not in mapa_colores:
                mapa_colores[bloque.pid] = colores[len(mapa_colores) % len(colores)]
            color = mapa_colores[bloque.pid]
            texto = f"{bloque.pid}\n{bloque.tamanio} MB"


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
        c.create_text(
            x1 - 8,
            y,
            text=str(bloque.inicio),
            anchor="e"
        )


        y += h


    c.create_text(
        x1 - 8,
        min(y, alto - 10),
        text=str(self.memoria.tamanio_total),
        anchor="e"
    )


    self.lbl_memoria_info.config(
        text=(
            f"Libre total: {self.memoria.memoria_libre_total()} MB\n"
            f"Fragmentación externa: "
            f"{self.memoria.fragmentacion_externa()} MB"
        )
    )