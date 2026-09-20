import shutil
import tempfile
import unittest
from pathlib import Path

from services.confirmacao_service import (
    ErroConfirmacao,
    confirmar_agendamento,
    preparar_reagendamento,
    recusar_agendamento,
    solicitar_agendamento,
)
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

    def test_solicita_e_atualiza_todos_os_registros(self) -> None:
        resultado = solicitar_agendamento(
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
        self.assertEqual(
            operacao["status"],
            "Aguardando confirmação do terminal",
        )
        self.assertFalse(janela["disponivel"])
        self.assertFalse(transporte["disponivel"])
        self.assertEqual(len(agendamentos), 1)
        self.assertEqual(agendamentos[0]["operacao_id"], "OP-001")
        self.assertEqual(
            agendamentos[0]["status"],
            "Aguardando confirmação do terminal",
        )
        self.assertIsNone(agendamentos[0]["confirmado_em"])

    def test_confirma_solicitacao_apos_resposta_do_terminal(self) -> None:
        solicitacao = solicitar_agendamento(
            "OP-001",
            "JT-001",
            "TR-001",
            self.diretorio_dados,
        )
        resultado = confirmar_agendamento(
            solicitacao["agendamento"]["id"],
            self.diretorio_dados,
        )

        operacao = carregar_operacoes(self.diretorio_dados)[0]
        agendamento = carregar_agendamentos(self.diretorio_dados)[0]

        self.assertEqual(resultado["agendamento"]["id"], "AG-001")
        self.assertEqual(operacao["status"], "Agendamento confirmado")
        self.assertEqual(agendamento["status"], "Agendamento confirmado")
        self.assertIsNotNone(agendamento["confirmado_em"])

    def test_recusa_solicitacao_e_libera_recursos(self) -> None:
        solicitacao = solicitar_agendamento(
            "OP-001",
            "JT-001",
            "TR-001",
            self.diretorio_dados,
        )
        resultado = recusar_agendamento(
            solicitacao["agendamento"]["id"],
            self.diretorio_dados,
        )

        operacao = carregar_operacoes(self.diretorio_dados)[0]
        janela = carregar_janelas_terminal(self.diretorio_dados)[0]
        transporte = carregar_disponibilidades_transporte(
            self.diretorio_dados
        )[0]
        agendamento = carregar_agendamentos(self.diretorio_dados)[0]

        self.assertEqual(
            resultado["agendamento"]["status"],
            "Agendamento recusado pelo terminal",
        )
        self.assertEqual(
            operacao["status"],
            "Agendamento recusado pelo terminal",
        )
        self.assertEqual(
            agendamento["status"],
            "Agendamento recusado pelo terminal",
        )
        self.assertIsNone(agendamento["confirmado_em"])
        self.assertTrue(janela["disponivel"])
        self.assertTrue(transporte["disponivel"])

    def test_impede_nova_solicitacao_da_mesma_operacao(self) -> None:
        solicitar_agendamento(
            "OP-001",
            "JT-001",
            "TR-001",
            self.diretorio_dados,
        )

        with self.assertRaisesRegex(ErroConfirmacao, "já possui"):
            solicitar_agendamento(
                "OP-001",
                "JT-001",
                "TR-001",
                self.diretorio_dados,
            )

    def test_prepara_e_registra_nova_tentativa_apos_recusa(self) -> None:
        solicitacao = solicitar_agendamento(
            "OP-001",
            "JT-001",
            "TR-001",
            self.diretorio_dados,
        )
        recusar_agendamento(
            solicitacao["agendamento"]["id"],
            self.diretorio_dados,
        )

        preparar_reagendamento("AG-001", self.diretorio_dados)
        nova_solicitacao = solicitar_agendamento(
            "OP-001",
            "JT-001",
            "TR-001",
            self.diretorio_dados,
        )
        agendamentos = carregar_agendamentos(self.diretorio_dados)

        self.assertEqual(nova_solicitacao["agendamento"]["id"], "AG-002")
        self.assertEqual(len(agendamentos), 2)
        self.assertEqual(
            agendamentos[0]["status"],
            "Agendamento recusado pelo terminal",
        )
        self.assertEqual(
            agendamentos[1]["status"],
            "Aguardando confirmação do terminal",
        )

    def test_impede_solicitacao_de_operacao_com_pendencia(self) -> None:
        with self.assertRaisesRegex(ErroConfirmacao, "pendências impeditivas"):
            solicitar_agendamento(
                "OP-002",
                "JT-004",
                "TR-004",
                self.diretorio_dados,
            )

        self.assertEqual(carregar_agendamentos(self.diretorio_dados), [])


if __name__ == "__main__":
    unittest.main()
