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

    def test_pagina_inicial_abre(self) -> None:
        resposta = self.client.get("/")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Painel de operações", conteudo)
        self.assertIn("OP-001", conteudo)
        self.assertIn("OP-002", conteudo)
        self.assertIn("OP-003", conteudo)
        self.assertIn(
            '<span class="status status-alerta">\n                Pronta para agendamento',
            conteudo,
        )
        self.assertIn('class="indicador indicador-alerta"', conteudo)

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

    def test_assistente_nao_pre_seleciona_nenhuma_opcao(self) -> None:
        resposta = self.client.get("/operacoes/OP-001/assistente")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Verificação de prontidão", conteudo)
        self.assertIn("Horários compatíveis", conteudo)
        self.assertIn("22/09/2026 às 14:00", conteudo)
        self.assertIn("Escolha um horário para continuar", conteudo)
        self.assertNotIn("Resumo para confirmação", conteudo)
        self.assertNotIn("Confirmar agendamento", conteudo)

    def test_assistente_exibe_resumo_apos_selecionar_horario(self) -> None:
        resposta = self.client.get(
            "/operacoes/OP-001/assistente?opcao=JT-001--TR-001"
        )
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
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

    def test_simular_atualizacao_resolve_pendencias_existentes(self) -> None:
        resposta = self.client.post(
            "/operacoes/OP-002/simular-atualizacao",
            follow_redirects=True,
        )
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Tudo concluído", conteudo)
        self.assertIn("Horários compatíveis", conteudo)
        self.assertNotIn("Simular atualização", conteudo)

        painel = self.client.get("/").get_data(as_text=True)
        cartao_op_002 = painel.split("OP-002", 1)[1].split("OP-003", 1)[0]
        self.assertIn("Pronta para agendamento", cartao_op_002)
        self.assertNotIn("Com pendências", cartao_op_002)

    def test_botao_simular_atualizacao_some_quando_ja_esta_tudo_concluido(
        self,
    ) -> None:
        resposta = self.client.get("/operacoes/OP-001/assistente")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Tudo concluído", conteudo)
        self.assertNotIn("Simular atualização", conteudo)

    def test_botao_simular_atualizacao_aparece_quando_ha_pendencia(self) -> None:
        resposta = self.client.get("/operacoes/OP-002/assistente")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Simular atualização", conteudo)

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

        assistente = self.client.get(
            "/operacoes/OP-001/assistente?opcao=JT-001--TR-001"
        ).get_data(as_text=True)
        self.assertIn('method="post"', assistente)

    def test_operacao_inexistente_exibe_erro_compreensivel(self) -> None:
        resposta = self.client.get("/operacoes/OP-999")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 404)
        self.assertIn("Operação não encontrada", conteudo)


if __name__ == "__main__":
    unittest.main()
