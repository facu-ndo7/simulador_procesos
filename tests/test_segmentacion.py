"""Segmentación pura: segmentos variables, tabla base+límite y ajustes.

Analiza: uso de memoria, fragmentación externa y fallos de página
(la segmentación pura no pagina: 0 fallos).
"""
import unittest
from utils.decoradores import Proceso
from controllers.memoriaController import crear_gestor
from controllers.memoria.segmentacion import (
    ViolacionSegmento, dividir_segmentos)


class TestSegmentacion(unittest.TestCase):
    def test_segmentos_variables(self):
        self.assertEqual(dividir_segmentos(2), [2])
        self.assertEqual(dividir_segmentos(5), [3, 2])
        partes = dividir_segmentos(20)
        self.assertEqual(partes, [10, 6, 4])
        self.assertEqual(sum(partes), 20)

    def test_tabla_base_limite(self):
        g = crear_gestor("Segmentación", 100, ajuste="First-Fit")
        g.asignar(Proceso("P1", 5, 20))
        tabla = g.obtener_tabla("P1")
        self.assertEqual([(e.seg, e.nombre, e.base, e.limite) for e in tabla],
                         [(0, "Código", 0, 10), (1, "Datos", 10, 6),
                          (2, "Pila", 16, 4)])

    def test_uso_de_memoria(self):
        g = crear_gestor("Segmentación", 100)
        g.asignar(Proceso("P1", 5, 20))
        self.assertEqual(g.memoria_libre_total(), 80)
        self.assertAlmostEqual(g.porcentaje_ocupacion(), 20.0)

    def test_fragmentacion_externa(self):
        g = crear_gestor("Segmentación", 100)
        g.asignar(Proceso("A", 5, 30))
        g.asignar(Proceso("B", 5, 20))
        g.liberar("A")  # huecos 30 y 50
        self.assertEqual(g.fragmentacion_externa(), 30)
        self.assertEqual(g.mayor_bloque_libre(), 50)

    def test_ajustes_first_best_worst(self):
        """Mismo escenario que contigua: el ajuste decide el hueco."""

        def base(ajuste):
            g = crear_gestor("Segmentación", 100, ajuste=ajuste)
            g.asignar(Proceso("A", 5, 50))
            g.asignar(Proceso("B", 5, 30))
            g.liberar("A")  # huecos [50][B30][20]
            g.asignar(Proceso("C", 5, 2))  # 1 segmento de 2 MB
            return g.obtener_tabla("C")[0].base

        self.assertEqual(base("First-Fit"), 0)
        self.assertEqual(base("Best-Fit"), 80)
        self.assertEqual(base("Worst-Fit"), 0)

    def test_traduccion_y_violacion(self):
        g = crear_gestor("Segmentación", 100)
        g.asignar(Proceso("P1", 5, 20))
        r = g.traducir("P1", 1, 5)
        self.assertEqual(r["direccion_fisica"], 15)
        with self.assertRaises(ViolacionSegmento):
            g.traducir("P1", 1, 6)

    def test_sin_fallos_de_pagina(self):
        g = crear_gestor("Segmentación", 100)
        p = Proceso("P1", 5, 20)
        g.asignar(p)
        res = g.simular_ejecucion(p, 5)
        self.assertEqual((res["hits"], res["faults"], res["swaps"]), (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
