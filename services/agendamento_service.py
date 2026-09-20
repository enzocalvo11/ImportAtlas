from datetime import datetime, timedelta
from typing import Any

from services.prontidao_service import STATUS_PRONTA, verificar_prontidao


STATUS_SEM_HORARIO = "Sem horário compatível"
STATUS_CONFIRMADO = "Agendamento confirmado"
DURACAO_PADRAO_MINUTOS = 60


def buscar_horarios_compativeis(
    operacao: dict[str, Any],
    janelas_terminal: list[dict[str, Any]],
    disponibilidades_transporte: list[dict[str, Any]],
    duracao_minutos: int = DURACAO_PADRAO_MINUTOS,
) -> dict[str, Any]:
    """Retorna a primeira compatibilidade e até duas alternativas."""
    if duracao_minutos <= 0:
        raise ValueError("A duração do atendimento deve ser maior que zero.")

    prontidao = verificar_prontidao(operacao)
    if operacao["status"] == STATUS_CONFIRMADO:
        return {
            "operacao_id": operacao["id"],
            "status": STATUS_CONFIRMADO,
            "mensagem": "Esta operação já possui agendamento confirmado.",
            "recomendacao": None,
            "alternativas": [],
            "total_opcoes": 0,
            "verificacoes": prontidao["verificacoes"],
            "pendencias": [],
        }

    if not prontidao["pronta"]:
        return {
            "operacao_id": operacao["id"],
            "status": prontidao["status"],
            "mensagem": "O agendamento ainda não pode ser realizado.",
            "recomendacao": None,
            "alternativas": [],
            "total_opcoes": 0,
            "verificacoes": prontidao["verificacoes"],
            "pendencias": prontidao["pendencias"],
        }

    compatibilidades = _calcular_compatibilidades(
        operacao,
        janelas_terminal,
        disponibilidades_transporte,
        duracao_minutos,
    )

    if not compatibilidades:
        return {
            "operacao_id": operacao["id"],
            "status": STATUS_SEM_HORARIO,
            "mensagem": (
                "A operação está apta, mas as disponibilidades do terminal "
                "e do transporte não coincidem."
            ),
            "recomendacao": None,
            "alternativas": [],
            "total_opcoes": 0,
            "verificacoes": prontidao["verificacoes"],
            "pendencias": [],
        }

    return {
        "operacao_id": operacao["id"],
        "status": STATUS_PRONTA,
        "mensagem": (
            "A recomendação é a primeira compatibilidade disponível entre "
            "o terminal e o transporte."
        ),
        "recomendacao": compatibilidades[0],
        "alternativas": compatibilidades[1:3],
        "total_opcoes": len(compatibilidades),
        "verificacoes": prontidao["verificacoes"],
        "pendencias": [],
    }


def _calcular_compatibilidades(
    operacao: dict[str, Any],
    janelas_terminal: list[dict[str, Any]],
    disponibilidades_transporte: list[dict[str, Any]],
    duracao_minutos: int,
) -> list[dict[str, Any]]:
    chegada_prevista = datetime.fromisoformat(operacao["chegada_prevista"])
    duracao = timedelta(minutes=duracao_minutos)
    compatibilidades = []

    janelas_validas = [
        janela
        for janela in janelas_terminal
        if janela["disponivel"] and janela["terminal"] == operacao["terminal"]
    ]
    transportes_validos = [
        transporte
        for transporte in disponibilidades_transporte
        if transporte["disponivel"]
        and transporte["operacao_id"] == operacao["id"]
    ]

    for janela in janelas_validas:
        inicio_janela = datetime.fromisoformat(janela["inicio"])
        fim_janela = datetime.fromisoformat(janela["fim"])

        for transporte in transportes_validos:
            inicio_transporte = datetime.fromisoformat(transporte["inicio"])
            fim_transporte = datetime.fromisoformat(transporte["fim"])
            inicio_possivel = max(
                chegada_prevista,
                inicio_janela,
                inicio_transporte,
            )
            fim_possivel = min(fim_janela, fim_transporte)

            if fim_possivel - inicio_possivel < duracao:
                continue

            compatibilidades.append(
                {
                    "janela_terminal_id": janela["id"],
                    "transporte_id": transporte["id"],
                    "terminal": janela["terminal"],
                    "transportadora": transporte["transportadora"],
                    "veiculo": transporte["veiculo"],
                    "inicio": inicio_possivel.isoformat(),
                    "fim": (inicio_possivel + duracao).isoformat(),
                }
            )

    return sorted(
        compatibilidades,
        key=lambda opcao: datetime.fromisoformat(opcao["inicio"]),
    )
