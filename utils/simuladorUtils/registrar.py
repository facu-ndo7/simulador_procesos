import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from copy import deepcopy

def registrar(self, mensaje):
    self.text_eventos.insert(tk.END, f"• {mensaje}\n")
    self.text_eventos.see(tk.END)