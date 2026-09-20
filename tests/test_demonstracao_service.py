import shutil
import tempfile
import unittest
from pathlib import Path

from services.confirmacao_service import (
    confirmar_agendamento,
    solicitar_agendamento,
)
from services.data_service import (
    carregar_agendamentos,
    carregar_disponibilidades_transporte,
    carregar_janelas_terminal,
    carregar_operacoes,
)
from services.demonstracao_service import (
    DIRETORIO_BASE_DEMO,
    restaurar_dados_demonstracao,
)


class DemonstracaoServiceTestCase(unittest.TestCase):
    def test_restaura_estado_inicial_apos_confirmacao(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio_temporario:
            diretorio_dados = Path(diretorio_temporario)
            for caminho in DIRETORIO_BASE_DEMO.glob("*.json"):
                shutil.copy2(caminho, diretorio_dados / caminho.name)

            solicitacao = solicitar_agendamento(
                "OP-001",
                "JT-001",
                "TR-001",
                diretorio_dados,
            )
            confirmar_agendamento(
                solicitacao["agendamento"]["id"],
                diretorio_dados,
            )
            restaurar_dados_demonstracao(
                diretorio_dados,
                DIRETORIO_BASE_DEMO,
            )

            self.assertEqual(carregar_agendamentos(diretorio_dados), [])
            self.assertEqual(
                carregar_operacoes(diretorio_dados)[0]["status"],
                "Pronta para agendamento",
            )
            self.assertTrue(
                carregar_janelas_terminal(diretorio_dados)[0]["disponivel"]
            )
            self.assertTrue(
                carregar_disponibilidades_transporte(diretorio_dados)[0][
                    "disponivel"
                ]
            )


if __name__ == "__main__":
    unittest.main()
