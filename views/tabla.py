from tkinter import ttk

COLORES_ESTADO = {
    "Nuevo": {"bg": "#e9ecef", "fg": "#495057"},
    "Listo": {"bg": "#d3f9d8", "fg": "#2b8a3e"},
    "Ejecutando": {"bg": "#fff3bf", "fg": "#e67700"},
    "Esperando memoria": {"bg": "#ffe3e3", "fg": "#c92a2a"},
    "Bloqueado": {"bg": "#e5dbff", "fg": "#5f3dc4"},
    "Esperando página": {"bg": "#ffe8cc", "fg": "#d9480f"},
    "Terminado": {"bg": "#d0ebff", "fg": "#1864ab"},
}

def crear_tabla(self, padre):
    """
    Permite visualizar el panel central izquierdo que contiene los procesos agregados.
    
    Args:
        self (SimuladorSO): Instancia de la clase SimuladorSO.
        padre (Frame): Objeto de la clase Frame, la cual permite organizar la disposición de los componentes visuales.   
    """
    marco = ttk.LabelFrame(padre, text="Procesos", padding=8)
    marco.pack(side="left", fill="both", expand=True, padx=(0, 6))


    columnas = ("pid", "rafaga", "memoria", "estado", "restante")
    self.tabla = ttk.Treeview(
        marco,
        columns=columnas,
        show="headings",
        height=12
    )


    scroll_tabla = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
    self.tabla.configure(yscrollcommand=scroll_tabla.set)
    scroll_tabla.pack(side="right", fill="y")


    encabezados = {
        "pid": "ID",
        "rafaga": "Ráfaga",
        "memoria": "Memoria",
        "estado": "Estado",
        "restante": "Restante"
    }


    for col in columnas:
        self.tabla.heading(col, text=encabezados[col])
        self.tabla.column(col, anchor="center", width=95)


    for estado, colores in COLORES_ESTADO.items():
        self.tabla.tag_configure(estado, background=colores["bg"], foreground=colores["fg"])


    self.tabla.pack(fill="both", expand=True)