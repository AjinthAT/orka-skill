import unittest
from app import priorite


class PrioriteTests(unittest.TestCase):
    def test_attente_inconnue(self):
        self.assertEqual(priorite(None), "inconnue")

    def test_avant_seuil(self):
        self.assertEqual(priorite(4), "normale")

    def test_ancien_seuil_reste_normal(self):
        self.assertEqual(priorite(5), "normale")

    def test_seuil_actuel_reste_normal(self):
        self.assertEqual(priorite(7), "normale")

    def test_juste_apres_seuil(self):
        self.assertEqual(priorite(7.01), "prioritaire")

    def test_apres_seuil(self):
        self.assertEqual(priorite(8), "prioritaire")


if __name__ == "__main__":
    unittest.main()
