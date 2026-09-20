import shutil
import tempfile
import unittest
from pathlib import Path

from services.atualizacao_externa_service import (
    ErroAtualizacaoExterna,
    simular_atualizacao_externa,
)
from services.data_service import carregar_operacoes
from services.demonstracao_service import DIRETORIO_BASE_DEMO


class AtualizacaoExternaServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        self.diretorio_dados = Path(self.diretorio_temporario.name)
        for caminho in DIRETORIO_BASE_DEMO.glob("*.json"):
            shutil.copy2(caminho, self.diretorio_dados / caminho.name)

    def tearDown(self) -> None:
        self.diretorio_temporario.cleanup()

    def test_conclui_pendencias_e_atualiza_status(self) -> None:
        resultado = simular_atualizacao_externa(
            "OP-002",
            self.diretorio_dados,
        )

        self.assertEqual(
            resultado["campos_atualizados"],
            ["liberacao_terminal"],
        )
        self.assertTrue(resultado["prontidao"]["pronta"])
        self.assertEqual(
            resultado["operacao"]["status"],
            "Pronta para agendamento",
        )

        operacoes = {
            operacao["id"]: operacao
            for operacao in carregar_operacoes(self.diretorio_dados)
        }
        self.assertTrue(operacoes["OP-002"]["liberacao_terminal"])
        self.assertEqual(
            operacoes["OP-002"]["status"],
            "Pronta para agendamento",
        )

    def test_rejeita_operacao_sem_pendencias(self) -> None:
        with self.assertRaisesRegex(
            ErroAtualizacaoExterna,
            "não possui pendências",
        ):
            simular_atualizacao_externa("OP-001", self.diretorio_dados)

    def test_rejeita_operacao_inexistente(self) -> None:
        with self.assertRaisesRegex(
            ErroAtualizacaoExterna,
            "não existe",
        ):
            simular_atualizacao_externa("OP-999", self.diretorio_dados)


if __name__ == "__main__":
    unittest.main()
