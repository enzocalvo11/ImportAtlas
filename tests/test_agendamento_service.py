import unittest
from copy import deepcopy

from services.agendamento_service import buscar_horarios_compativeis
from services.data_service import (
    carregar_disponibilidades_transporte,
    carregar_janelas_terminal,
    carregar_operacoes,
)
from services.demonstracao_service import DIRETORIO_BASE_DEMO


class AgendamentoServiceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.operacoes = {
            operacao["id"]: operacao
            for operacao in carregar_operacoes(DIRETORIO_BASE_DEMO)
        }
        cls.janelas = carregar_janelas_terminal(DIRETORIO_BASE_DEMO)
        cls.transportes = carregar_disponibilidades_transporte(
            DIRETORIO_BASE_DEMO
        )

    def test_recomenda_primeiro_horario_e_retorna_duas_alternativas(self) -> None:
        resultado = buscar_horarios_compativeis(
            self.operacoes["OP-001"],
            self.janelas,
            self.transportes,
        )

        self.assertEqual(resultado["status"], "Aguardando confirmação")
        self.assertEqual(resultado["total_opcoes"], 3)
        self.assertEqual(
            resultado["recomendacao"]["janela_terminal_id"],
            "JT-001",
        )
        self.assertEqual(resultado["recomendacao"]["transporte_id"], "TR-001")
        self.assertEqual(
            [opcao["janela_terminal_id"] for opcao in resultado["alternativas"]],
            ["JT-002", "JT-003"],
        )

    def test_operacao_com_pendencia_nao_busca_horarios(self) -> None:
        resultado = buscar_horarios_compativeis(
            self.operacoes["OP-002"],
            self.janelas,
            self.transportes,
        )

        self.assertEqual(resultado["status"], "Com pendências")
        self.assertIsNone(resultado["recomendacao"])
        self.assertEqual(resultado["alternativas"], [])
        self.assertEqual(resultado["total_opcoes"], 0)
        self.assertEqual(len(resultado["pendencias"]), 1)

    def test_informa_quando_nao_existe_horario_compativel(self) -> None:
        resultado = buscar_horarios_compativeis(
            self.operacoes["OP-003"],
            self.janelas,
            self.transportes,
        )

        self.assertEqual(resultado["status"], "Sem horário compatível")
        self.assertIsNone(resultado["recomendacao"])
        self.assertEqual(resultado["alternativas"], [])
        self.assertIn("não coincidem", resultado["mensagem"])

    def test_ignora_janelas_e_transportes_indisponiveis(self) -> None:
        janelas = deepcopy(self.janelas)
        transportes = deepcopy(self.transportes)
        janelas[0]["disponivel"] = False
        transportes[1]["disponivel"] = False

        resultado = buscar_horarios_compativeis(
            self.operacoes["OP-001"],
            janelas,
            transportes,
        )

        self.assertEqual(resultado["total_opcoes"], 1)
        self.assertEqual(
            resultado["recomendacao"]["janela_terminal_id"],
            "JT-003",
        )

    def test_rejeita_duracao_invalida(self) -> None:
        with self.assertRaisesRegex(ValueError, "maior que zero"):
            buscar_horarios_compativeis(
                self.operacoes["OP-001"],
                self.janelas,
                self.transportes,
                duracao_minutos=0,
            )


if __name__ == "__main__":
    unittest.main()
