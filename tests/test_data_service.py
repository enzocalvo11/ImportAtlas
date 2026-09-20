import json
import tempfile
import unittest
from pathlib import Path

from services.data_service import (
    ErroDados,
    carregar_disponibilidades_transporte,
    carregar_janelas_terminal,
    carregar_operacoes,
)
from services.demonstracao_service import DIRETORIO_BASE_DEMO


class DadosSimuladosTestCase(unittest.TestCase):
    def test_carrega_os_tres_cenarios_obrigatorios(self) -> None:
        operacoes = carregar_operacoes(DIRETORIO_BASE_DEMO)
        operacoes_por_id = {operacao["id"]: operacao for operacao in operacoes}

        self.assertEqual(set(operacoes_por_id), {"OP-001", "OP-002", "OP-003"})
        self.assertTrue(operacoes_por_id["OP-001"]["documentacao_concluida"])
        self.assertFalse(operacoes_por_id["OP-002"]["documentacao_concluida"])
        self.assertTrue(operacoes_por_id["OP-003"]["documentacao_concluida"])

    def test_carrega_disponibilidades_deterministicas(self) -> None:
        janelas = carregar_janelas_terminal(DIRETORIO_BASE_DEMO)
        transportes = carregar_disponibilidades_transporte(
            DIRETORIO_BASE_DEMO
        )

        self.assertEqual(len(janelas), 5)
        self.assertEqual(len(transportes), 5)
        self.assertEqual(janelas[0]["id"], "JT-001")
        self.assertEqual(transportes[0]["id"], "TR-001")

    def test_rejeita_operacao_com_campo_ausente(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio_temporario:
            diretorio = Path(diretorio_temporario)
            dados_incompletos = [{"id": "OP-TESTE"}]
            (diretorio / "operacoes.json").write_text(
                json.dumps(dados_incompletos),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ErroDados, "não possui"):
                carregar_operacoes(diretorio)


if __name__ == "__main__":
    unittest.main()
