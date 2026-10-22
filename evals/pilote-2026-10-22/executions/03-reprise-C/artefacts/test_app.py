import unittest
from app import priorite


class PrioriteTests(unittest.TestCase):
    def test_attente_inconnue(self):
        self.assertEqual(priorite(None), "inconnue")

    def test_attente_nulle(self):
        self.assertEqual(priorite(0), "normale")

    def test_ancien_seuil_reste_normal(self):
        for attente in (4, 5, 5.1, 6):
            with self.subTest(attente=attente):
                self.assertEqual(priorite(attente), "normale")

    def test_juste_avant_seuil(self):
        self.assertEqual(priorite(6.999), "normale")

    def test_seuil_exact_reste_normal(self):
        self.assertEqual(priorite(7), "normale")

    def test_strictement_apres_seuil(self):
        for attente in (7.001, 8):
            with self.subTest(attente=attente):
                self.assertEqual(priorite(attente), "prioritaire")


if __name__ == "__main__":
    unittest.main()
