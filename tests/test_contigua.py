"""Comparativa de asignación contigua: First/Best/Worst-Fit.

Analiza en cada ajuste: uso de memoria, fragmentación externa y
admitidos. Escenario con huecos de distinto tamaño para que los
ajustes decidan diferente.
"""
import unittest
from utils.decoradores import Proceso
from controllers.memoriaController import crear_gestor


def escenario_huecos(ajuste):
    """100 MB: A50 + B30, se libera A -> huecos [50][B30][20]."""
    g = crear_gestor("Asignación contigua", 100, ajuste=ajuste)
    a, b = Proceso("A", 5, 50), Proceso("B", 5, 30)
    assert g.asignar(a) and g.asignar(b)
    g.liberar("A")
    return g


class TestContiguaFits(unittest.TestCase):
    def test_decision_difiere_por_ajuste(self):
        """C=15 cabe en huecos de 50 y 20: cada ajuste elige distinto."""
        bases = {}
        for ajuste in ("First-Fit", "Best-Fit", "Worst-Fit"):
            g = escenario_huecos(ajuste)
            c = Proceso("C", 5, 15)
            self.assertTrue(g.asignar(c))
            # La base real de C se lee del bloque ocupado por C.
            bases[ajuste] = next(b.inicio for b in g.bloques if b.pid == "C")
        self.assertEqual(bases["First-Fit"], 0)   # primer hueco
        self.assertEqual(bases["Best-Fit"], 80)   # hueco más chico que cabe
        self.assertEqual(bases["Worst-Fit"], 0)   # hueco más grande

    def test_uso_de_memoria_identico(self):
        """Con el mismo workload, el libre total no depende del ajuste."""
        for ajuste in ("First-Fit", "Best-Fit", "Worst-Fit"):
            g = escenario_huecos(ajuste)
            g.asignar(Proceso("C", 5, 15))
            self.assertEqual(g.memoria_libre_total(), 100 - 30 - 15)
            self.assertAlmostEqual(g.porcentaje_ocupacion(), 45.0)

    def test_fragmentacion_externa_difiere(self):
        """Best-Fit deja el hueco grande intacto (menos fragmentación)."""
        ext = {}
        for ajuste in ("First-Fit", "Best-Fit", "Worst-Fit"):
            g = escenario_huecos(ajuste)
            g.asignar(Proceso("C", 5, 15))
            ext[ajuste] = g.fragmentacion_externa()
        self.assertEqual(ext["First-Fit"], 20)   # huecos 35 y 20
        self.assertEqual(ext["Best-Fit"], 5)     # huecos 50 y 5
        self.assertEqual(ext["Worst-Fit"], 20)
        self.assertLess(ext["Best-Fit"], ext["First-Fit"])

    def test_mayor_bloque_libre(self):
        g = escenario_huecos("Best-Fit")
        g.asignar(Proceso("C", 5, 15))
        self.assertEqual(g.mayor_bloque_libre(), 50)

    def test_sin_fallos_de_pagina(self):
        """La contigua no pagina: hook sin efecto, 0 fallos."""
        g = crear_gestor("Asignación contigua", 100)
        p = Proceso("A", 5, 30)
        g.asignar(p)
        res = g.simular_ejecucion(p, 5)
        self.assertEqual((res["hits"], res["faults"], res["swaps"]), (0, 0, 0))

    def test_no_cabe_retorna_false(self):
        g = crear_gestor("Asignación contigua", 100)
        self.assertFalse(g.asignar(Proceso("BIG", 5, 101)))

    def test_liberar_fusiona_huecos(self):
        g = crear_gestor("Asignación contigua", 100)
        a, b = Proceso("A", 5, 30), Proceso("B", 5, 20)
        g.asignar(a)
        g.asignar(b)
        g.liberar("A")
        g.liberar("B")
        self.assertEqual(len(g.bloques), 1)
        self.assertEqual(g.memoria_libre_total(), 100)


if __name__ == "__main__":
    unittest.main()
