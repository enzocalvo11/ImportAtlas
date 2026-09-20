import shutil
import tempfile
import unittest
from pathlib import Path

from services.confirmacao_service import ErroConfirmacao, confirmar_agendamento
from services.data_service import (
    carregar_agendamentos,
    carregar_disponibilidades_transporte,
    carregar_janelas_terminal,
    carregar_operacoes,
)


DIRETORIO_DADOS_ORIGINAL = (
    Path(__file__).resolve().parent.parent / "data" / "base_demo"
)


class ConfirmacaoServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        self.diretorio_dados = Path(self.diretorio_temporario.name)
        for caminho in DIRETORIO_DADOS_ORIGINAL.glob("*.json"):
            shutil.copy2(caminho, self.diretorio_dados / caminho.name)

    def tearDown(self) -> None:
        self.diretorio_temporario.cleanup()

    def test_confirma_e_atualiza_todos_os_registros(self) -> None:
        resultado = confirmar_agendamento(
            "OP-001",
            "JT-001",
            "TR-001",
            self.diretorio_dados,
        )

        operacao = carregar_operacoes(self.diretorio_dados)[0]
        janela = carregar_janelas_terminal(self.diretorio_dados)[0]
        transporte = carregar_disponibilidades_transporte(
            self.diretorio_dados
        )[0]
        agendamentos = carregar_agendamentos(self.diretorio_dados)

        self.assertEqual(resultado["agendamento"]["id"], "AG-001")
        self.assertEqual(operacao["status"], "Agendamento confirmado")
        self.assertFalse(janela["disponivel"])
        self.assertFalse(transporte["disponivel"])
        self.assertEqual(len(agendamentos), 1)
        self.assertEqual(agendamentos[0]["operacao_id"], "OP-001")

    def test_impede_nova_confirmacao_da_mesma_operacao(self) -> None:
        confirmar_agendamento(
            "OP-001",
            "JT-001",
            "TR-001",
            self.diretorio_dados,
        )

        with self.assertRaisesRegex(ErroConfirmacao, "já possui"):
            confirmar_agendamento(
                "OP-001",
                "JT-001",
                "TR-001",
                self.diretorio_dados,
            )

    def test_impede_confirmacao_de_operacao_com_pendencia(self) -> None:
        with self.assertRaisesRegex(ErroConfirmacao, "pendências impeditivas"):
            confirmar_agendamento(
                "OP-002",
                "JT-004",
                "TR-004",
                self.diretorio_dados,
            )

        self.assertEqual(carregar_agendamentos(self.diretorio_dados), [])


if __name__ == "__main__":
    unittest.main()
