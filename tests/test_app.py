import unittest

from app import create_app


class PaginaInicialTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app()
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_pagina_inicial_abre(self) -> None:
        resposta = self.client.get("/")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Painel de operações", conteudo)
        self.assertIn("OP-001", conteudo)
        self.assertIn("OP-002", conteudo)
        self.assertIn("OP-003", conteudo)

    def test_abre_detalhes_da_operacao(self) -> None:
        resposta = self.client.get("/operacoes/OP-001")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Café Atlântico Ltda.", conteudo)
        self.assertIn("Condições registradas", conteudo)

    def test_assistente_exibe_recomendacao_e_resumo_para_confirmacao(self) -> None:
        resposta = self.client.get("/operacoes/OP-001/assistente")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Verificação de prontidão", conteudo)
        self.assertIn("Horários compatíveis", conteudo)
        self.assertIn("22/09/2026 às 14:00", conteudo)
        self.assertIn("Resumo para confirmação", conteudo)
        self.assertIn("Confirmar agendamento", conteudo)

    def test_assistente_permite_selecionar_alternativa(self) -> None:
        resposta = self.client.get(
            "/operacoes/OP-001/assistente?opcao=JT-002--TR-002"
        )
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("22/09/2026 às 17:00", conteudo)
        self.assertIn("EFG4H56", conteudo)

    def test_assistente_interrompe_operacao_com_pendencia(self) -> None:
        resposta = self.client.get("/operacoes/OP-002/assistente")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Pendências impeditivas", conteudo)
        self.assertIn("Documentação incompleta", conteudo)
        self.assertNotIn("Confirmar agendamento", conteudo)

    def test_assistente_exibe_resultado_sem_compatibilidade(self) -> None:
        resposta = self.client.get("/operacoes/OP-003/assistente")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Nenhum horário compatível", conteudo)
        self.assertNotIn("Confirmar agendamento", conteudo)

    def test_assistente_rejeita_opcao_desconhecida(self) -> None:
        resposta = self.client.get(
            "/operacoes/OP-001/assistente?opcao=JT-999--TR-999"
        )

        self.assertEqual(resposta.status_code, 400)

    def test_operacao_inexistente_exibe_erro_compreensivel(self) -> None:
        resposta = self.client.get("/operacoes/OP-999")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 404)
        self.assertIn("Operação não encontrada", conteudo)


if __name__ == "__main__":
    unittest.main()
