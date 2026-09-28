import tkinter as tk
from tkinter import ttk, messagebox

def panel_configuracion(self, padre):
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
    self.combo_cpu.bind("<<ComboboxSelected>>", lambda e: self._actualizar_estado_quantum())
    
    
    ttk.Label(marco, text="Algoritmo memoria").grid(row=0, column=2, sticky="w", padx=5, pady=5)
    self.combo_mem = ttk.Combobox(
        marco,
            state="readonly",
            values=["First-Fit", "Best-Fit", "Worst-Fit"],
            width=16
    )
    self.combo_mem.current(0)
    self.combo_mem.grid(row=1, column=2, padx=5, pady=5)
    
    
    ttk.Label(marco, text="Quantum").grid(row=0, column=3, sticky="w", padx=5, pady=5)
    self.entry_quantum = ttk.Entry(marco, width=10)
    self.entry_quantum.insert(0, "2")
    self.entry_quantum.grid(row=1, column=3, padx=5, pady=5)
    
    
    ttk.Button(
        marco,
        text="Iniciar simulación",
        command=self.iniciar_simulacion
    ).grid(row=2, column=0, padx=5, pady=10)
    
    
    self.btn_paso = ttk.Button(
        marco,
        text="Paso siguiente",
        command=self.paso_siguiente,
        state="disabled"
    )
    self.btn_paso.grid(row=2, column=1, padx=5, pady=10)
    
    
    ttk.Button(
        marco,
        text="Reiniciar",
        command=self.reiniciar_simulacion
    ).grid(row=2, column=2, padx=5, pady=10)
    
    
    ttk.Button(
        marco,
        text="Limpiar todo",
        command=self.limpiar_todo
    ).grid(row=2, column=3, padx=5, pady=10)