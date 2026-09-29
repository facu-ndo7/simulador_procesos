import tkinter as tk

def registrar(self, mensaje):
    self.text_eventos.insert(tk.END, f"• {mensaje}\n")
    self.text_eventos.see(tk.END)