import shutil
import tempfile
import unittest
from pathlib import Path

from app import create_app


DIRETORIO_DADOS_ORIGINAL = (
    Path(__file__).resolve().parent.parent / "data" / "base_demo"
)


class PaginaInicialTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        self.diretorio_dados = Path(self.diretorio_temporario.name)
        for caminho in DIRETORIO_DADOS_ORIGINAL.glob("*.json"):
            shutil.copy2(caminho, self.diretorio_dados / caminho.name)

        app = create_app(
            {
                "TESTING": True,
                "DIRETORIO_DADOS": self.diretorio_dados,
                "DIRETORIO_BASE_DEMO": DIRETORIO_DADOS_ORIGINAL,
            }
        )
        self.client = app.test_client()

    def tearDown(self) -> None:
        self.diretorio_temporario.cleanup()

    def test_pagina_inicial_aguarda_recebimento_das_operacoes(self) -> None:
        resposta = self.client.get("/")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Painel de operações", conteudo)
        self.assertIn("Simular recebimento das operações", conteudo)
        self.assertNotIn("OP-001", conteudo)
        self.assertNotIn("OP-002", conteudo)
        self.assertNotIn("OP-003", conteudo)

    def test_simula_recebimento_e_exibe_operacoes_com_status(self) -> None:
        resposta = self.client.post(
            "/operacoes/simular-recebimento",
            follow_redirects=True,
        )
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Recebimento simulado com sucesso", conteudo)
        self.assertIn("OP-001", conteudo)
        self.assertIn("OP-002", conteudo)
        self.assertIn("OP-003", conteudo)
        self.assertIn('<span class="status status-alerta">', conteudo)
        self.assertIn("Pronta para agendamento", conteudo)
        self.assertIn("Com pendências", conteudo)
        self.assertIn('class="indicador indicador-alerta"', conteudo)

        novo_acesso = self.client.get("/").get_data(as_text=True)
        self.assertIn("OP-001", novo_acesso)

    def test_atualizacao_externa_conclui_pendencia_e_atualiza_painel(self) -> None:
        self.client.post("/operacoes/simular-recebimento")
        painel_antes = self.client.get("/").get_data(as_text=True)

        self.assertNotIn("Simular atualização externa", painel_antes)

        resposta = self.client.post(
            "/operacoes/OP-002/simular-atualizacao-externa",
            data={"origem": "detalhes"},
            follow_redirects=True,
        )
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Atualização externa simulada com sucesso", conteudo)
        self.assertNotIn("Simular atualização externa", conteudo)

        painel_atualizado = self.client.get("/").get_data(as_text=True)
        self.assertEqual(
            painel_atualizado.count("Pronta para agendamento"),
            3,
        )

    def test_botao_de_atualizacao_aparece_apenas_em_detalhe_pendente(self) -> None:
        operacao_pronta = self.client.get(
            "/operacoes/OP-001"
        ).get_data(as_text=True)
        operacao_pendente = self.client.get(
            "/operacoes/OP-002"
        ).get_data(as_text=True)

        self.assertNotIn("Simular atualização externa", operacao_pronta)
        self.assertIn("Simular atualização externa", operacao_pendente)

    def test_atualizacao_externa_no_assistente_libera_horarios(self) -> None:
        resposta = self.client.post(
            "/operacoes/OP-002/simular-atualizacao-externa",
            data={"origem": "assistente"},
            follow_redirects=True,
        )
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("A busca de horários já foi liberada", conteudo)
        self.assertIn("Horários compatíveis", conteudo)
        self.assertNotIn("Pendências impeditivas", conteudo)

    def test_abre_detalhes_da_operacao(self) -> None:
        resposta = self.client.get("/operacoes/OP-001")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Café Atlântico Ltda.", conteudo)
        self.assertIn("Condições registradas", conteudo)
        self.assertIn("Tudo concluído", conteudo)
        self.assertIn("informacao-valida", conteudo)
        self.assertNotIn("item-pendente", conteudo)

    def test_detalhes_destacam_pendencia_em_vermelho(self) -> None:
        resposta = self.client.get("/operacoes/OP-002")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Requer atenção", conteudo)
        self.assertIn("Documentação concluída", conteudo)
        self.assertIn("item-pendente", conteudo)

    def test_assistente_exibe_recomendacao_e_resumo_para_confirmacao(self) -> None:
        resposta = self.client.get("/operacoes/OP-001/assistente")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Verificação de prontidão", conteudo)
        self.assertIn("Horários compatíveis", conteudo)
        self.assertIn("22/09/2026 às 14:00", conteudo)
        self.assertIn("Resumo para confirmação", conteudo)
        self.assertIn("Confirmar agendamento", conteudo)
        self.assertIn("data-assistente-agendamento", conteudo)
        self.assertIn('data-resumo-horario="inicio"', conteudo)
        self.assertIn('data-campo-horario="transporte_id"', conteudo)
        self.assertIn("Voltar ao painel", conteudo)
        self.assertNotIn("Voltar aos detalhes", conteudo)

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

    def test_confirma_agendamento_e_exibe_resultado(self) -> None:
        self.client.post("/operacoes/simular-recebimento")
        resposta = self.client.post(
            "/operacoes/OP-001/confirmar",
            data={
                "janela_terminal_id": "JT-001",
                "transporte_id": "TR-001",
            },
            follow_redirects=True,
        )
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Agendamento confirmado", conteudo)
        self.assertIn("AG-001", conteudo)
        self.assertIn("Comunicação simulada", conteudo)
        self.assertIn("mensagem não enviada", conteudo)

        painel = self.client.get("/").get_data(as_text=True)
        self.assertIn("Agendamento confirmado", painel)
        self.assertIn("Ver agendamento", painel)

        detalhes = self.client.get("/operacoes/OP-001").get_data(as_text=True)
        self.assertIn("Registro AG-001", detalhes)

    def test_rejeita_confirmacao_repetida(self) -> None:
        dados = {
            "janela_terminal_id": "JT-001",
            "transporte_id": "TR-001",
        }
        primeira_resposta = self.client.post(
            "/operacoes/OP-001/confirmar",
            data=dados,
        )
        segunda_resposta = self.client.post(
            "/operacoes/OP-001/confirmar",
            data=dados,
        )

        self.assertEqual(primeira_resposta.status_code, 303)
        self.assertEqual(segunda_resposta.status_code, 409)

    def test_restaura_os_dados_da_demonstracao(self) -> None:
        self.client.post(
            "/operacoes/OP-001/confirmar",
            data={
                "janela_terminal_id": "JT-001",
                "transporte_id": "TR-001",
            },
        )

        resposta = self.client.post(
            "/demonstracao/restaurar",
            follow_redirects=True,
        )
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Demonstração restaurada", conteudo)
        self.assertNotIn("Ver agendamento", conteudo)
        self.assertNotIn("OP-001", conteudo)
        self.assertIn("Simular recebimento das operações", conteudo)

        assistente = self.client.get(
            "/operacoes/OP-001/assistente"
        ).get_data(as_text=True)
        self.assertIn('method="post"', assistente)

    def test_operacao_inexistente_exibe_erro_compreensivel(self) -> None:
        resposta = self.client.get("/operacoes/OP-999")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 404)
        self.assertIn("Operação não encontrada", conteudo)


if __name__ == "__main__":
    unittest.main()
