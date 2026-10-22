import unittest
from app import priorite


class PrioriteTests(unittest.TestCase):
    def test_attente_inconnue(self):
        self.assertEqual(priorite(None), "inconnue")

    def test_avant_seuil(self):
        self.assertEqual(priorite(4), "normale")

    def test_seuil_ancien(self):
        self.assertEqual(priorite(5), "prioritaire")


if __name__ == "__main__":
    unittest.main()
