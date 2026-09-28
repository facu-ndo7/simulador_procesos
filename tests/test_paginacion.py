"""Paginación simple + comparativa FIFO vs LRU en paginación por demanda.

Analiza: uso de memoria, fragmentación interna y fallos de página.
La paginación simple no sufre fallos (todo residente); la demanda
(MemoriaVirtual) sí, y allí FIFO y LRU divergen con la misma
secuencia de referencias.
"""
import unittest
from utils.decoradores import Proceso
from controllers.memoriaController import crear_gestor

# Secuencia donde FIFO y LRU reemplazan distinto (3 marcos, 5 páginas).
SECUENCIA = [0, 1, 2, 3, 0, 1, 4, 0, 1, 2, 3, 4]


def accesos_con_politica(reemplazo):
    g = crear_gestor("Memoria virtual", 24, tam_pagina=8,
                     tamanio_virtual=256, reemplazo=reemplazo)
    p = Proceso("P", 12, 40)  # 5 páginas, 3 marcos físicos
    g.asignar(p)
    for pagina in SECUENCIA:
        g.acceder("P", pagina)
    return g


class TestPaginacionSimple(unittest.TestCase):
    def test_marcos_fijos_y_tabla(self):
        g = crear_gestor("Paginación", 100, tam_pagina=8)
        self.assertEqual(g.num_marcos, 13)
        p = Proceso("A", 5, 20)
        self.assertTrue(g.asignar(p))
        tabla = g.obtener_tabla("A")
        self.assertEqual([(e.pagina, e.marco) for e in tabla],
                         [(0, 0), (1, 1), (2, 2)])

    def test_uso_de_memoria(self):
        g = crear_gestor("Paginación", 100, tam_pagina=8)
        g.asignar(Proceso("A", 5, 20))
        self.assertEqual(g.memoria_libre_total(), 100 - 3 * 8)
        self.assertAlmostEqual(g.porcentaje_ocupacion(), 24.0)
        self.assertEqual(g.mayor_bloque_libre(), 8)

    def test_fragmentacion_interna_y_externa(self):
        g = crear_gestor("Paginación", 100, tam_pagina=8)
        g.asignar(Proceso("A", 5, 20))  # 3 págs -> desperdicio 4
        g.asignar(Proceso("B", 5, 30))  # 4 págs -> desperdicio 2
        self.assertEqual(g.fragmentacion_interna(), 6)
        self.assertEqual(g.fragmentacion_externa(), 0)

    def test_sin_fallos_todo_residente(self):
        g = crear_gestor("Paginación", 100, tam_pagina=8)
        p = Proceso("A", 5, 20)
        g.asignar(p)
        res = g.simular_ejecucion(p, 8)
        self.assertEqual((res["hits"], res["faults"], res["swaps"]), (0, 0, 0))

    def test_traduccion(self):
        g = crear_gestor("Paginación", 100, tam_pagina=8)
        g.asignar(Proceso("A", 5, 20))
        r = g.traducir("A", 19)
        self.assertEqual((r["pagina"], r["marco"], r["direccion_fisica"]),
                         (2, 2, 19))


class TestDemandaFifoVsLru(unittest.TestCase):
    def test_mismo_uso_distintos_fallos(self):
        """Igual ocupación, pero LRU falla más que FIFO aquí."""
        gf = accesos_con_politica("FIFO")
        gl = accesos_con_politica("LRU")
        # Uso idéntico: 3 marcos ocupados, 0 libres.
        self.assertEqual(gf.memoria_libre_total(), 0)
        self.assertEqual(gl.memoria_libre_total(), 0)
        self.assertEqual(gf.porcentaje_ocupacion(), 100.0)
        # Fallos: 1 de carga inicial + secuencia (FIFO 8, LRU 9).
        self.assertEqual(gf.fallos, 9)
        self.assertEqual(gl.fallos, 10)
        self.assertEqual(gf.accesos, gl.accesos)
        self.assertNotEqual(gf.fallos, gl.fallos)

    def test_swaps_y_tasa(self):
        gf = accesos_con_politica("FIFO")
        gl = accesos_con_politica("LRU")
        self.assertEqual((gf.swaps, gl.swaps), (6, 7))
        self.assertLess(gf.tasa_fallos(), gl.tasa_fallos())
        self.assertLess(gf.tmat(), gl.tmat())

    def test_fragmentacion_interna_nula_ajuste_exacto(self):
        gf = accesos_con_politica("FIFO")
        self.assertEqual(gf.fragmentacion_interna(), 5 * 8 - 40)


if __name__ == "__main__":
    unittest.main()
