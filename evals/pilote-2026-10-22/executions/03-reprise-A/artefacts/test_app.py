import unittest
from app import priorite


class PrioriteTests(unittest.TestCase):
    def test_attente_inconnue(self):
        self.assertEqual(priorite(None), "inconnue")

    def test_avant_seuil(self):
        for attente in (0, 4, 5, 6.99):
            with self.subTest(attente=attente):
                self.assertEqual(priorite(attente), "normale")

    def test_seuil_sept_minutes(self):
        self.assertEqual(priorite(7), "normale")

    def test_apres_seuil(self):
        for attente in (7.01, 8):
            with self.subTest(attente=attente):
                self.assertEqual(priorite(attente), "prioritaire")


if __name__ == "__main__":
    unittest.main()
