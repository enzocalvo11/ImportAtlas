from pathlib import Path
from typing import Any

from services.data_service import (
    DIRETORIO_DADOS,
    carregar_agendamentos,
    carregar_disponibilidades_transporte,
    carregar_janelas_terminal,
    carregar_operacoes,
    salvar_estado_agendamento,
)
from services.prontidao_service import (
    REGRAS_PRONTIDAO,
    STATUS_PRONTA,
    verificar_prontidao,
)


class ErroSimulacao(ValueError):
    """Indica que não foi possível simular a atualização da operação."""


def simular_atualizacao_prontidao(
    operacao_id: str,
    diretorio_dados: Path = DIRETORIO_DADOS,
) -> dict[str, Any]:
    """Resolve, para fins de demonstração, todas as pendências da operação.

    Quando não há nenhuma pendência, não há nada a simular e a operação
    é devolvida sem alterações.
    """
    operacoes = carregar_operacoes(diretorio_dados)
    operacao = next(
        (item for item in operacoes if item["id"] == operacao_id),
        None,
    )
    if operacao is None:
        raise ErroSimulacao(f"A operação {operacao_id} não existe.")

    prontidao = verificar_prontidao(operacao)
    if not prontidao["pendencias"]:
        return operacao

    for campo, valor_esperado, *_ in REGRAS_PRONTIDAO:
        operacao[campo] = valor_esperado
    operacao["status"] = STATUS_PRONTA

    salvar_estado_agendamento(
        operacoes,
        carregar_janelas_terminal(diretorio_dados),
        carregar_disponibilidades_transporte(diretorio_dados),
        carregar_agendamentos(diretorio_dados),
        diretorio_dados,
    )
    return operacao
