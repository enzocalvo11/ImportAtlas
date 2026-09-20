from typing import Any


STATUS_PRONTA = "Pronta para agendamento"
STATUS_COM_PENDENCIAS = "Com pendências"

ROTULOS_VERIFICACAO = {
    "liberacao_aduaneira": "Liberação aduaneira",
    "documentacao_concluida": "Documentação concluída",
    "tributos_regularizados": "Tributos e pagamentos regularizados",
    "liberacao_terminal": "Liberação administrativa do terminal",
    "possui_bloqueio": "Ausência de bloqueio impeditivo",
}

REGRAS_PRONTIDAO = (
    (
        "liberacao_aduaneira",
        True,
        "Liberação aduaneira pendente",
        "A carga ainda não possui liberação aduaneira.",
        "aduana",
        "Acompanhar a análise e obter a liberação aduaneira.",
    ),
    (
        "documentacao_concluida",
        True,
        "Documentação incompleta",
        "Os documentos obrigatórios ainda não foram concluídos.",
        "documentacao",
        "Concluir e validar a documentação da operação.",
    ),
    (
        "tributos_regularizados",
        True,
        "Tributos ou pagamentos pendentes",
        "Existem tributos ou pagamentos que ainda precisam ser regularizados.",
        "tributos",
        "Regularizar os valores pendentes e confirmar o pagamento.",
    ),
    (
        "liberacao_terminal",
        True,
        "Liberação administrativa do terminal pendente",
        "O terminal ainda não liberou administrativamente a retirada.",
        "terminal",
        "Solicitar a regularização ao terminal.",
    ),
    (
        "possui_bloqueio",
        False,
        "Bloqueio impeditivo ativo",
        "Existe um bloqueio que impede o agendamento da retirada.",
        "bloqueio",
        "Identificar e remover o bloqueio antes de buscar horários.",
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
