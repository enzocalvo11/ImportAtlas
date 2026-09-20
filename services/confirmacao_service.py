from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

from services.agendamento_service import buscar_horarios_compativeis
from services.data_service import (
    DIRETORIO_DADOS,
    carregar_agendamentos,
    carregar_disponibilidades_transporte,
    carregar_janelas_terminal,
    carregar_operacoes,
    salvar_estado_agendamento,
)


STATUS_CONFIRMADO = "Agendamento confirmado"
_TRAVA_CONFIRMACAO = Lock()


class ErroConfirmacao(ValueError):
    """Indica que o agendamento não pode ser confirmado com segurança."""


def confirmar_agendamento(
    operacao_id: str,
    janela_terminal_id: str,
    transporte_id: str,
    diretorio_dados: Path = DIRETORIO_DADOS,
) -> dict[str, Any]:
    with _TRAVA_CONFIRMACAO:
        return _confirmar_agendamento(
            operacao_id,
            janela_terminal_id,
            transporte_id,
            diretorio_dados,
        )


def _confirmar_agendamento(
    operacao_id: str,
    janela_terminal_id: str,
    transporte_id: str,
    diretorio_dados: Path,
) -> dict[str, Any]:
    operacoes = carregar_operacoes(diretorio_dados)
    janelas = carregar_janelas_terminal(diretorio_dados)
    transportes = carregar_disponibilidades_transporte(diretorio_dados)
    agendamentos = carregar_agendamentos(diretorio_dados)

    operacao = _buscar_por_id(operacoes, operacao_id)
    if operacao is None:
        raise ErroConfirmacao(f"A operação {operacao_id} não existe.")
    if operacao["status"] == STATUS_CONFIRMADO:
        raise ErroConfirmacao("Esta operação já possui agendamento confirmado.")

    resultado = buscar_horarios_compativeis(operacao, janelas, transportes)
    if resultado["pendencias"]:
        raise ErroConfirmacao(
            "A operação possui pendências impeditivas e não pode ser agendada."
        )
    if resultado["recomendacao"] is None:
        raise ErroConfirmacao(
            "Nenhum horário compatível está disponível para esta operação."
        )

    opcoes = [
        opcao
        for opcao in [resultado["recomendacao"], *resultado["alternativas"]]
        if opcao is not None
    ]
    opcao = next(
        (
            item
            for item in opcoes
            if item["janela_terminal_id"] == janela_terminal_id
            and item["transporte_id"] == transporte_id
        ),
        None,
    )
    if opcao is None:
        raise ErroConfirmacao(
            "O horário selecionado não está mais disponível para confirmação."
        )

    janela = _buscar_por_id(janelas, janela_terminal_id)
    transporte = _buscar_por_id(transportes, transporte_id)
    if janela is None or transporte is None:
        raise ErroConfirmacao("Os dados do horário selecionado não foram encontrados.")

    agendamento = {
        "id": _proximo_id_agendamento(agendamentos),
        "operacao_id": operacao_id,
        "janela_terminal_id": janela_terminal_id,
        "transporte_id": transporte_id,
        "inicio": opcao["inicio"],
        "fim": opcao["fim"],
        "status": STATUS_CONFIRMADO,
        "confirmado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
    }

    operacao["status"] = STATUS_CONFIRMADO
    janela["disponivel"] = False
    transporte["disponivel"] = False
    agendamentos.append(agendamento)

    salvar_estado_agendamento(
        operacoes,
        janelas,
        transportes,
        agendamentos,
        diretorio_dados,
    )

    participantes = list(dict.fromkeys(operacao["responsaveis"].values()))
    return {
        "operacao": operacao,
        "agendamento": agendamento,
        "opcao": opcao,
        "comunicacoes": [
            {
                "destinatario": participante,
                "status": "Simulação — mensagem não enviada",
            }
            for participante in participantes
        ],
    }


def _buscar_por_id(
    registros: list[dict[str, Any]],
    identificador: str,
) -> dict[str, Any] | None:
    return next(
        (registro for registro in registros if registro["id"] == identificador),
        None,
    )


def _proximo_id_agendamento(agendamentos: list[dict[str, Any]]) -> str:
    numeros = []
    for agendamento in agendamentos:
        try:
            numeros.append(int(agendamento["id"].split("-")[-1]))
        except ValueError:
            continue
    return f"AG-{max(numeros, default=0) + 1:03d}"
