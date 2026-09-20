import unittest
from copy import deepcopy

from services.data_service import carregar_operacoes
from services.demonstracao_service import DIRETORIO_BASE_DEMO
from services.prontidao_service import verificar_prontidao


class ProntidaoServiceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.operacoes = {
            operacao["id"]: operacao
            for operacao in carregar_operacoes(DIRETORIO_BASE_DEMO)
        }

    def test_operacao_pronta_pode_avancar(self) -> None:
        resultado = verificar_prontidao(self.operacoes["OP-001"])

        self.assertTrue(resultado["pronta"])
        self.assertEqual(resultado["status"], "Pronta para agendamento")
        self.assertEqual(resultado["pendencias"], [])

    def test_operacao_com_documentacao_pendente_nao_pode_avancar(self) -> None:
        resultado = verificar_prontidao(self.operacoes["OP-002"])

        self.assertFalse(resultado["pronta"])
        self.assertEqual(resultado["status"], "Com pendências")
        self.assertEqual(len(resultado["pendencias"]), 1)
        self.assertEqual(
            resultado["pendencias"][0]["descricao"],
            "Documentação incompleta",
        )
        self.assertEqual(
            resultado["pendencias"][0]["responsavel"],
            "Despachante aduaneiro",
        )

    def test_operacao_com_bloqueio_impeditivo_nao_pode_avancar(self) -> None:
        operacao_bloqueada = deepcopy(self.operacoes["OP-001"])
        operacao_bloqueada["possui_bloqueio"] = True

        resultado = verificar_prontidao(operacao_bloqueada)

        self.assertFalse(resultado["pronta"])
        self.assertEqual(len(resultado["pendencias"]), 1)
        self.assertEqual(
            resultado["pendencias"][0]["campo"],
            "possui_bloqueio",
        )
        self.assertIn(
            "antes de buscar horários",
            resultado["pendencias"][0]["proxima_acao"],
        )

    def test_retorna_todas_as_pendencias_impeditivas(self) -> None:
        operacao_bloqueada = deepcopy(self.operacoes["OP-001"])
        operacao_bloqueada.update(
            {
                "liberacao_aduaneira": False,
                "documentacao_concluida": False,
                "tributos_regularizados": False,
                "liberacao_terminal": False,
                "possui_bloqueio": True,
            }
        )

        resultado = verificar_prontidao(operacao_bloqueada)
        campos_pendentes = {
            pendencia["campo"] for pendencia in resultado["pendencias"]
        }

        self.assertFalse(resultado["pronta"])
        self.assertEqual(
            campos_pendentes,
            {
                "liberacao_aduaneira",
                "documentacao_concluida",
                "tributos_regularizados",
                "liberacao_terminal",
                "possui_bloqueio",
            },
        )


if __name__ == "__main__":
    unittest.main()
