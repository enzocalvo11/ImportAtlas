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
        self.assertIn('<span class="status status-informativo">', conteudo)
        self.assertIn("Pronta para agendamento", conteudo)
        self.assertIn("Com pendências", conteudo)
        self.assertIn('class="indicador indicador-informativo"', conteudo)
        self.assertIn('class="indicador indicador-alerta"', conteudo)
        self.assertIn('class="indicador indicador-sucesso"', conteudo)
        self.assertIn("cartao-operacao-status-informativo", conteudo)
        self.assertIn("cartao-operacao-status-alerta", conteudo)

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
        self.assertIn("2 opções encontradas", conteudo)
        self.assertIn("23/09/2026 às 16:30", conteudo)
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
        self.assertIn('<span class="status status-informativo">', conteudo)

    def test_detalhes_destacam_despesas_portuarias_pendentes(self) -> None:
        resposta = self.client.get("/operacoes/OP-002")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Requer atenção", conteudo)
        self.assertIn(
            "Despesas portuárias e armazenagem regularizadas",
            conteudo,
        )
        self.assertIn("item-pendente", conteudo)
        self.assertIn('<span class="status status-alerta">', conteudo)

    def test_assistente_nao_pre_seleciona_nenhuma_opcao(self) -> None:
        resposta = self.client.get("/operacoes/OP-001/assistente")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Verificação de prontidão", conteudo)
        self.assertIn("Horários compatíveis", conteudo)
        self.assertIn("22/09/2026 às 14:00", conteudo)
        self.assertIn("Escolha um horário para continuar", conteudo)
        self.assertIn("data-resumo-confirmacao", conteudo)
        self.assertIn("data-resumo-confirmacao\n      hidden", conteudo)

    def test_assistente_exibe_recomendacao_e_resumo_para_solicitacao(self) -> None:
        resposta = self.client.get(
            "/operacoes/OP-001/assistente?opcao=JT-001--TR-001"
        )
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Verificação de prontidão", conteudo)
        self.assertIn("Horários compatíveis", conteudo)
        self.assertIn("22/09/2026 às 14:00", conteudo)
        self.assertIn("Resumo da solicitação", conteudo)
        self.assertIn("Solicitar agendamento", conteudo)
        self.assertIn("ainda precisará confirmar", conteudo)
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

    def test_assistente_permite_desmarcar_horario_selecionado(self) -> None:
        resposta = self.client.get(
            "/operacoes/OP-001/assistente?opcao=JT-001--TR-001"
        )
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Desmarcar horário", conteudo)
        self.assertIn(
            'href="/operacoes/OP-001/assistente?opcao="',
            conteudo,
        )

        resposta_sem_selecao = self.client.get(
            "/operacoes/OP-001/assistente?opcao="
        )
        self.assertNotIn(
            'class="cartao-horario cartao-recomendado cartao-selecionado"',
            resposta_sem_selecao.get_data(as_text=True),
        )

    def test_assistente_interrompe_operacao_com_pendencia(self) -> None:
        resposta = self.client.get("/operacoes/OP-002/assistente")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Pendências impeditivas", conteudo)
        self.assertIn(
            "Despesas portuárias ou armazenagem pendentes",
            conteudo,
        )
        self.assertNotIn("Solicitar agendamento", conteudo)

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
        self.assertIn("Simular atualização externa", conteudo)
        self.assertIn(
            'action="/operacoes/OP-002/simular-atualizacao-externa"',
            conteudo,
        )
        self.assertIn('name="origem" value="assistente"', conteudo)
        self.assertIn('class="botao botao-primario"', conteudo)

    def test_assistente_exibe_dois_horarios_para_op003(self) -> None:
        resposta = self.client.get("/operacoes/OP-003/assistente")
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("2 opções encontradas", conteudo)
        self.assertIn("24/09/2026 às 08:00", conteudo)
        self.assertIn("24/09/2026 às 10:00", conteudo)

    def test_assistente_rejeita_opcao_desconhecida(self) -> None:
        resposta = self.client.get(
            "/operacoes/OP-001/assistente?opcao=JT-999--TR-999"
        )

        self.assertEqual(resposta.status_code, 400)

    def test_solicita_e_depois_simula_confirmacao_do_terminal(self) -> None:
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
        self.assertIn("Aguardando confirmação do terminal", conteudo)
        self.assertIn("AG-001", conteudo)
        self.assertIn("Resposta do terminal", conteudo)
        self.assertIn("Confirmação pendente", conteudo)
        self.assertIn("Confirmar horário", conteudo)
        self.assertIn("Recusar horário", conteudo)
        self.assertEqual(resposta.request.path, "/agendamentos/AG-001")

        painel = self.client.get("/").get_data(as_text=True)
        self.assertIn("Aguardando confirmação do terminal", painel)
        self.assertIn("Acompanhar solicitação", painel)

        detalhes = self.client.get("/operacoes/OP-001").get_data(as_text=True)
        self.assertIn("Aguardando confirmação do terminal", detalhes)
        self.assertIn("Registro AG-001", detalhes)

        confirmacao = self.client.post(
            "/agendamentos/AG-001/confirmar",
            follow_redirects=True,
        )
        conteudo_confirmado = confirmacao.get_data(as_text=True)

        self.assertEqual(confirmacao.status_code, 200)
        self.assertIn("Agendamento confirmado", conteudo_confirmado)
        self.assertIn("Horário confirmado", conteudo_confirmado)
        self.assertIn("painel e o histórico", conteudo_confirmado)
        self.assertIn("Participantes que seriam comunicados", conteudo_confirmado)
        self.assertEqual(confirmacao.request.path, "/agendamentos/AG-001")

        painel_confirmado = self.client.get("/").get_data(as_text=True)
        self.assertIn("Agendamento confirmado", painel_confirmado)
        self.assertIn("Ver agendamento", painel_confirmado)
        self.assertIn("cartao-operacao-status-sucesso", painel_confirmado)

    def test_simula_resposta_negativa_na_mesma_pagina(self) -> None:
        self.client.post("/operacoes/simular-recebimento")
        self.client.post(
            "/operacoes/OP-001/confirmar",
            data={
                "janela_terminal_id": "JT-001",
                "transporte_id": "TR-001",
            },
        )

        resposta = self.client.post(
            "/agendamentos/AG-001/recusar",
            follow_redirects=True,
        )
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.request.path, "/agendamentos/AG-001")
        self.assertIn("Agendamento recusado pelo terminal", conteudo)
        self.assertIn("Horário recusado", conteudo)
        self.assertIn("janela e o transporte reservados foram liberados", conteudo)
        self.assertIn("Tentar novo horário", conteudo)
        self.assertNotIn("Confirmar horário", conteudo)
        self.assertNotIn("Recusar horário", conteudo)

        painel = self.client.get("/").get_data(as_text=True)
        self.assertIn("Agendamento recusado pelo terminal", painel)
        self.assertIn("Ver resposta do terminal", painel)

        detalhes = self.client.get("/operacoes/OP-001").get_data(as_text=True)
        self.assertIn("Agendamento recusado pelo terminal", detalhes)
        self.assertIn("Ver resposta do terminal", detalhes)

        reagendamento = self.client.post(
            "/agendamentos/AG-001/reagendar",
            follow_redirects=True,
        )
        conteudo_reagendamento = reagendamento.get_data(as_text=True)

        self.assertEqual(reagendamento.status_code, 200)
        self.assertEqual(
            reagendamento.request.path,
            "/operacoes/OP-001/assistente",
        )
        self.assertIn("Horários compatíveis", conteudo_reagendamento)
        self.assertIn("Pronta para agendamento", conteudo_reagendamento)
        # JT-001/TR-001 (22/09/2026 às 14:00) foi recusado e não pode
        # voltar a ser oferecido para esta operação.
        self.assertIn("2 opções encontradas", conteudo_reagendamento)
        self.assertNotIn("22/09/2026 às 14:00", conteudo_reagendamento)
        self.assertIn("22/09/2026 às 17:00", conteudo_reagendamento)

    def test_assistente_recarrega_solicitacao_pendente(self) -> None:
        self.client.post(
            "/operacoes/OP-001/confirmar",
            data={
                "janela_terminal_id": "JT-001",
                "transporte_id": "TR-001",
            },
        )

        resposta = self.client.get(
            "/operacoes/OP-001/assistente",
            follow_redirects=True,
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(
            "Aguardando confirmação do terminal",
            resposta.get_data(as_text=True),
        )

    def test_rejeita_solicitacao_repetida(self) -> None:
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
        self.assertNotIn("Acompanhar solicitação", conteudo)

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
