import tkinter as tk

def actualizar_tabla(self, procesos):
    """
    Permite refrescar la tabla de procesos.
    
    Args:
        self (SimuladorSO): Instancia de la clase SimuladorSO.
        procesos (array): Una lista con los procesos agregados en el sistema.  
    """
    
    for item in self.tabla.get_children():
        self.tabla.delete(item)


    for p in procesos:
        self.tabla.insert(
            "",
            tk.END,
            values=(
                p.pid,
                p.rafaga,
                f"{p.memoria} MB",
                p.estado,
                p.restante
            ),
            tags=(p.estado,)
        )