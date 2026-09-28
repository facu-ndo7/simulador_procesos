def actualizar_estado_quantum(self):
    if self.combo_cpu.get() == "Round-Robin":
        self.entry_quantum.config(state="normal")
    else:
        self.entry_quantum.config(state="disabled")