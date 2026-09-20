import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

from services.data_service import carregar_operacoes
from services.demonstracao_service import DIRETORIO_BASE_DEMO
from services.prontidao_service import verificar_prontidao
from services.simulacao_service import ErroSimulacao, simular_atualizacao_prontidao


DIRETORIO_DADOS_ORIGINAL = DIRETORIO_BASE_DEMO


class SimulacaoServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        self.diretorio_dados = Path(self.diretorio_temporario.name)
        for caminho in DIRETORIO_DADOS_ORIGINAL.glob("*.json"):
            shutil.copy2(caminho, self.diretorio_dados / caminho.name)

    def tearDown(self) -> None:
        self.diretorio_temporario.cleanup()

    def _buscar_operacao(self, operacao_id: str) -> dict[str, Any]:
        return next(
            item
            for item in carregar_operacoes(self.diretorio_dados)
            if item["id"] == operacao_id
        )

    def test_resolve_todas_as_pendencias_quando_existem(self) -> None:
        # OP-002 nasce com uma pendência de documentação.
        self.assertFalse(
            verificar_prontidao(self._buscar_operacao("OP-002"))["pronta"]
        )

        simular_atualizacao_prontidao("OP-002", self.diretorio_dados)

        operacao_depois = self._buscar_operacao("OP-002")
        self.assertTrue(verificar_prontidao(operacao_depois)["pronta"])
        self.assertEqual(operacao_depois["status"], "Pronta para agendamento")

    def test_nao_altera_nada_quando_ja_esta_tudo_concluido(self) -> None:
        # OP-001 nasce pronta, sem nenhuma pendência.
        operacao_antes = dict(self._buscar_operacao("OP-001"))

        resultado = simular_atualizacao_prontidao("OP-001", self.diretorio_dados)

        self.assertEqual(resultado, operacao_antes)
        self.assertTrue(
            verificar_prontidao(self._buscar_operacao("OP-001"))["pronta"]
        )

    def test_rejeita_operacao_inexistente(self) -> None:
        with self.assertRaisesRegex(ErroSimulacao, "não existe"):
            simular_atualizacao_prontidao("OP-999", self.diretorio_dados)


if __name__ == "__main__":
    unittest.main()
