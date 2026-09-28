"""Segmentación paginada: segmentos divididos en páginas, dos niveles.

Analiza: uso de memoria, fragmentación interna y fallos de página
(carga total al asignar: 0 fallos por demanda).
"""
import unittest
from utils.decoradores import Proceso
from controllers.memoriaController import crear_gestor
from controllers.memoria.segmentacion import ViolacionSegmento


class TestSegmentadaPaginada(unittest.TestCase):
    def test_segmentos_en_paginas(self):
        g = crear_gestor("Segmentación paginada", 100, tam_pagina=8)
        g.asignar(Proceso("P1", 5, 20))  # segs [10, 6, 4]
        tabla = g.obtener_tabla("P1")
        self.assertEqual([e.limite for e in tabla], [10, 6, 4])
        self.assertEqual([(ep.pagina, ep.marco) for ep in tabla[0].tabla_paginas],
                         [(0, 0), (1, 1)])
        self.assertEqual([(ep.pagina, ep.marco) for ep in tabla[1].tabla_paginas],
                         [(0, 2)])

    def test_uso_de_memoria(self):
        g = crear_gestor("Segmentación paginada", 100, tam_pagina=8)
        g.asignar(Proceso("P1", 5, 20))  # 4 páginas
        self.assertEqual(g.memoria_libre_total(), 100 - 4 * 8)
        self.assertAlmostEqual(g.porcentaje_ocupacion(), 32.0)
        self.assertEqual(g.mayor_bloque_libre(), 8)

    def test_fragmentacion_interna_y_externa(self):
        g = crear_gestor("Segmentación paginada", 100, tam_pagina=8)
        g.asignar(Proceso("P1", 5, 20))  # (16-10)+(8-6)+(8-4) = 12
        self.assertEqual(g.fragmentacion_interna(), 12)
        self.assertEqual(g.fragmentacion_externa(), 0)

    def test_traduccion_dos_niveles(self):
        g = crear_gestor("Segmentación paginada", 100, tam_pagina=8)
        g.asignar(Proceso("P1", 5, 20))
        r = g.traducir("P1", 1, 5)  # seg Datos: p0 desp5 -> M2 base16
        self.assertEqual((r["pagina_en_seg"], r["marco"], r["direccion_fisica"]),
                         (0, 2, 21))
        with self.assertRaises(ViolacionSegmento):
            g.traducir("P1", 1, 6)

    def test_sin_fallos_por_demanda(self):
        """Carga total al asignar: el hook no genera fallos."""
        g = crear_gestor("Segmentación paginada", 100, tam_pagina=8)
        p = Proceso("P1", 5, 20)
        g.asignar(p)
        res = g.simular_ejecucion(p, 5)
        self.assertEqual((res["hits"], res["faults"], res["swaps"]), (0, 0, 0))

    def test_no_cabe_si_faltan_marcos(self):
        g = crear_gestor("Segmentación paginada", 16, tam_pagina=8)  # 2 marcos
        self.assertFalse(g.asignar(Proceso("P1", 5, 20)))  # necesita 4 págs


if __name__ == "__main__":
    unittest.main()
