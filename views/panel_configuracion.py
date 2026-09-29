from tkinter import ttk

from utils.simuladorUtils.iniciar_simulacion import iniciar_simulacion
from utils.simuladorUtils.paso_siguiente import paso_siguiente
from utils.simuladorUtils.reiniciar_simulacion import reiniciar_simulacion
from utils.simuladorUtils.limpiar_todo import limpiar_todo
from utils.simuladorUtils.actualizar_estado_quantum import actualizar_estado_quantum
from utils.simuladorUtils.cambiar_modo_memoria import cambiar_modo_memoria
from utils.simuladorUtils.comparar_esquemas import comparar_esquemas
from utils.simuladorUtils.ejecucion_auto import alternar_auto
import controllers.memoriaController as mc

def actualizar_estado_memoria(self):
    """Habilita ajuste / tamaño de página / campos virtuales según el modo."""
    modo = mc.normalizar_modo(self.combo_modo_mem.get()) if hasattr(self, "combo_modo_mem") else ""
    usa_ajuste = modo in ("Asignación contigua", "Segmentación")
    necesita_pagina = modo in ("Paginación", "Segmentación paginada",
                               "Memoria virtual")
    es_virtual = (modo == "Memoria virtual")
    try:
        self.combo_ajuste_mem.config(state="readonly" if usa_ajuste else "disabled")
    except Exception:
        pass
    try:
        self.entry_tam_pagina.config(state="normal" if necesita_pagina else "disabled")
    except Exception:
        pass
    try:
        self.entry_mem_virtual.config(state="normal" if es_virtual else "disabled")
    except Exception:
        pass
    try:
        self.combo_reemplazo.config(state="readonly" if es_virtual else "disabled")
    except Exception:
        pass
    try:
        self.btn_cambiar_mem.config(
            text="Cambiar / Redimensionar" if es_virtual else "Cambiar memoria")
    except Exception:
        pass

def panel_configuracion(self, padre):
    """
    Permite visualizar el panel superior para establecer las configuraciones del sistema.
        
    Args:
        self (SimuladorSO): Instancia de la clase SimuladorSO.
        padre (Frame): Objeto de la clase Frame, la cual permite organizar la disposición de los componentes visuales.   
    """
    
    marco = ttk.LabelFrame(padre, text="Configuración", padding=10)
    marco.pack(side="left", fill="x", expand=True, padx=(6, 0))
    
    
    ttk.Label(marco, text="Memoria total (MB)").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    self.entry_mem_total = ttk.Entry(marco, width=12)
    self.entry_mem_total.insert(0, "100")
    self.entry_mem_total.grid(row=1, column=0, padx=5, pady=5)
    
    
    ttk.Label(marco, text="Algoritmo CPU").grid(row=0, column=1, sticky="w", padx=5, pady=5)
    self.combo_cpu = ttk.Combobox(
        marco,
        state="readonly",
        values=[
            "FIFO",
            "SJF no apropiativo",
            "Round-Robin",
        ],
        width=22
    )
    
    self.combo_cpu.current(0)
    self.combo_cpu.grid(row=1, column=1, padx=5, pady=5)
    self.combo_cpu.bind("<<ComboboxSelected>>", lambda e: actualizar_estado_quantum(self))
    
    
    ttk.Label(marco, text="Modo de memoria").grid(row=0, column=2, sticky="w", padx=5, pady=5)
    self.combo_modo_mem = ttk.Combobox(
        marco,
        state="readonly",
        values=mc.MODOS_MEMORIA,
        width=22
    )
    self.combo_modo_mem.current(0)
    self.combo_modo_mem.grid(row=1, column=2, padx=5, pady=5)
    self.combo_modo_mem.bind("<<ComboboxSelected>>", lambda e: actualizar_estado_memoria(self))
    
    
    ttk.Label(marco, text="Quantum").grid(row=0, column=3, sticky="w", padx=5, pady=5)
    self.entry_quantum = ttk.Entry(marco, width=10)
    self.entry_quantum.insert(0, "2")
    self.entry_quantum.grid(row=1, column=3, padx=5, pady=5)


    ttk.Label(marco, text="Ajuste (contigua/seg.)").grid(row=2, column=2, sticky="w", padx=5, pady=5)
    self.combo_ajuste_mem = ttk.Combobox(
        marco,
        state="readonly",
        values=["First-Fit", "Best-Fit", "Worst-Fit"],
        width=22
    )
    self.combo_ajuste_mem.current(0)
    self.combo_ajuste_mem.grid(row=3, column=2, padx=5, pady=5)
    # Compatibilidad: código viejo que lea combo_mem obtiene el ajuste.
    self.combo_mem = self.combo_ajuste_mem


    ttk.Label(marco, text="Tamaño página (MB)").grid(row=2, column=3, sticky="w", padx=5, pady=5)
    self.entry_tam_pagina = ttk.Entry(marco, width=10)
    self.entry_tam_pagina.insert(0, "8")
    self.entry_tam_pagina.grid(row=3, column=3, padx=5, pady=5)


    ttk.Label(marco, text="Memoria virtual (MB)").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    self.entry_mem_virtual = ttk.Entry(marco, width=12)
    self.entry_mem_virtual.insert(0, "400")
    self.entry_mem_virtual.grid(row=3, column=0, padx=5, pady=5)


    ttk.Label(marco, text="Reemplazo (virtual)").grid(row=2, column=1, sticky="w", padx=5, pady=5)
    self.combo_reemplazo = ttk.Combobox(
        marco,
        state="readonly",
        values=["LRU", "FIFO"],
        width=22
    )
    self.combo_reemplazo.current(0)
    self.combo_reemplazo.grid(row=3, column=1, padx=5, pady=5)

    # Valores por defecto del gestor activo.
    self.modo_mem = mc.MODOS_MEMORIA[0]
    self.ajuste_mem = "First-Fit"
    self.tam_pagina = 8
    self.tam_virtual = 400
    self.reemplazo = "LRU"
    
    
    ttk.Button(
        marco,
        text="Iniciar simulación",
        command= lambda: iniciar_simulacion(self)
    ).grid(row=4, column=0, padx=5, pady=10)
    
    
    self.btn_paso = ttk.Button(
        marco,
        text="Paso siguiente",
        command=lambda: paso_siguiente(self),
        state="disabled"
    )
    self.btn_paso.grid(row=4, column=1, padx=5, pady=10)


    self.btn_cambiar_mem = ttk.Button(
        marco,
        text="Cambiar memoria",
        command=lambda: cambiar_modo_memoria(self),
        state="disabled"
    )
    self.btn_cambiar_mem.grid(row=4, column=2, padx=5, pady=10)


    ttk.Button(
        marco,
        text="Comparar esquemas",
        command=lambda: comparar_esquemas(self)
    ).grid(row=4, column=3, padx=5, pady=10)
    
    
    ttk.Button(
        marco,
        text="Reiniciar",
        command=lambda: reiniciar_simulacion(self)
    ).grid(row=5, column=0, padx=5, pady=10)
    
    
    ttk.Button(
        marco,
        text="Limpiar todo",
        command=lambda: limpiar_todo(self)
    ).grid(row=5, column=1, padx=5, pady=10)


    self.btn_auto = ttk.Button(
        marco,
        text="Auto",
        command=lambda: alternar_auto(self),
        state="disabled"
    )
    self.btn_auto.grid(row=5, column=2, padx=5, pady=10)

    actualizar_estado_memoria(self)
