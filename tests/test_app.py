import unittest

from app import create_app


class PaginaInicialTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app()
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_pagina_inicial_abre(self) -> None:
        resposta = self.client.get("/")

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"ImportAtlas", resposta.data)


if __name__ == "__main__":
    unittest.main()
