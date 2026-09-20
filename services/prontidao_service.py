from typing import Any


STATUS_PRONTA = "Pronta para agendamento"
STATUS_COM_PENDENCIAS = "Com pendências"

ROTULOS_VERIFICACAO = {
    "liberacao_aduaneira": "Presença/recepção da carga averbada",
    "documentacao_concluida": (
        "DUIMP desembaraçada, com documentação completa"
    ),
    "tributos_regularizados": (
        "Tributos e ICMS regularizados, quando aplicáveis"
    ),
    "possui_bloqueio": "Anuências e exigências encerradas",
    "liberacao_terminal": (
        "Despesas portuárias e armazenagem regularizadas"
    ),
}

REGRAS_PRONTIDAO = (
    (
        "liberacao_aduaneira",
        True,
        "Presença da carga não averbada",
        "A presença ou recepção da carga ainda não foi averbada.",
        "aduana",
        "Confirmar a presença da carga e concluir a averbação.",
    ),
    (
        "documentacao_concluida",
        True,
        "DUIMP ou documentação pendente",
        "A DUIMP ainda não foi desembaraçada ou a documentação está incompleta.",
        "documentacao",
        "Concluir a documentação e acompanhar o desembaraço da DUIMP.",
    ),
    (
        "tributos_regularizados",
        True,
        "Tributos ou ICMS pendentes",
        "Existem tributos ou valores de ICMS que ainda precisam ser regularizados.",
        "tributos",
        "Regularizar os tributos aplicáveis e confirmar os pagamentos.",
    ),
    (
        "possui_bloqueio",
        False,
        "Anuências ou exigências em aberto",
        "Ainda existem anuências ou exigências que impedem a retirada.",
        "bloqueio",
        "Encerrar as anuências e exigências antes de buscar horários.",
    ),
    (
        "liberacao_terminal",
        True,
        "Despesas portuárias ou armazenagem pendentes",
        "Existem despesas portuárias ou de armazenagem não regularizadas.",
        "terminal",
        "Regularizar as despesas junto ao terminal.",
    ),
)

VALORES_ESPERADOS_PRONTIDAO = {
    campo: valor_esperado
    for campo, valor_esperado, *_ in REGRAS_PRONTIDAO
}


def verificar_prontidao(operacao: dict[str, Any]) -> dict[str, Any]:
    """Avalia as condições obrigatórias sem alterar a operação recebida."""
    pendencias = []
    verificacoes = []

    for (
        campo,
        valor_esperado,
        descricao,
        motivo,
        papel_responsavel,
        proxima_acao,
    ) in REGRAS_PRONTIDAO:
        concluida = operacao[campo] == valor_esperado
        verificacoes.append(
            {
                "campo": campo,
                "descricao": ROTULOS_VERIFICACAO[campo],
                "concluida": concluida,
            }
        )

        if concluida:
            continue

        pendencias.append(
            {
                "campo": campo,
                "descricao": descricao,
                "motivo": motivo,
                "responsavel": operacao["responsaveis"][papel_responsavel],
                "proxima_acao": proxima_acao,
            }
        )

    pronta = not pendencias
    return {
        "operacao_id": operacao["id"],
        "pronta": pronta,
        "status": STATUS_PRONTA if pronta else STATUS_COM_PENDENCIAS,
        "verificacoes": verificacoes,
        "pendencias": pendencias,
    }
