from datetime import datetime
from typing import Any

from flask import Flask, abort, render_template, request

from services.agendamento_service import buscar_horarios_compativeis
from services.data_service import (
    ErroDados,
    carregar_disponibilidades_transporte,
    carregar_janelas_terminal,
    carregar_operacoes,
)


CLASSES_STATUS = {
    "Aguardando liberação": "status-alerta",
    "Com pendências": "status-erro",
    "Pronta para agendamento": "status-sucesso",
    "Sem horário compatível": "status-alerta",
    "Aguardando confirmação": "status-informativo",
    "Agendamento confirmado": "status-sucesso",
}


def create_app() -> Flask:
    """Cria a aplicação web do ImportAtlas."""
    app = Flask(__name__)

    app.jinja_env.filters["data_br"] = _formatar_data
    app.jinja_env.filters["classe_status"] = _classe_status

    @app.get("/")
    def painel_operacoes() -> str:
        operacoes = carregar_operacoes()
        indicadores = {
            "total": len(operacoes),
            "prontas": _contar_status(operacoes, "Pronta para agendamento"),
            "pendencias": _contar_status(operacoes, "Com pendências"),
            "confirmadas": _contar_status(operacoes, "Agendamento confirmado"),
        }
        return render_template(
            "index.html",
            operacoes=operacoes,
            indicadores=indicadores,
        )

    @app.get("/operacoes/<operacao_id>")
    def detalhes_operacao(operacao_id: str) -> str:
        operacao = _buscar_operacao(operacao_id)
        return render_template("operacao.html", operacao=operacao)

    @app.get("/operacoes/<operacao_id>/assistente")
    def iniciar_assistente(operacao_id: str) -> str:
        operacao = _buscar_operacao(operacao_id)
        resultado = buscar_horarios_compativeis(
            operacao,
            carregar_janelas_terminal(),
            carregar_disponibilidades_transporte(),
        )
        opcoes = _preparar_opcoes(resultado)
        opcao_selecionada = _selecionar_opcao(
            opcoes,
            request.args.get("opcao"),
        )
        participantes = list(dict.fromkeys(operacao["responsaveis"].values()))
        return render_template(
            "assistente_inicio.html",
            operacao=operacao,
            resultado=resultado,
            opcoes=opcoes,
            opcao_selecionada=opcao_selecionada,
            participantes=participantes,
        )

    @app.errorhandler(400)
    def solicitacao_invalida(erro: Any) -> tuple[str, int]:
        return (
            render_template(
                "erro.html",
                titulo="Opção inválida",
                mensagem=getattr(
                    erro,
                    "description",
                    "Não foi possível processar a opção informada.",
                ),
            ),
            400,
        )

    @app.errorhandler(404)
    def pagina_nao_encontrada(erro: Any) -> tuple[str, int]:
        return (
            render_template(
                "erro.html",
                titulo="Operação não encontrada",
                mensagem=getattr(
                    erro,
                    "description",
                    "Não foi possível localizar o conteúdo solicitado.",
                ),
            ),
            404,
        )

    @app.errorhandler(ErroDados)
    def falha_ao_carregar_dados(erro: ErroDados) -> tuple[str, int]:
        return (
            render_template(
                "erro.html",
                titulo="Não foi possível carregar os dados",
                mensagem=str(erro),
            ),
            500,
        )

    return app


def _buscar_operacao(operacao_id: str) -> dict[str, Any]:
    operacao = next(
        (
            item
            for item in carregar_operacoes()
            if item["id"] == operacao_id
        ),
        None,
    )
    if operacao is None:
        abort(404, description=f"A operação {operacao_id} não existe.")
    return operacao


def _contar_status(operacoes: list[dict[str, Any]], status: str) -> int:
    return sum(operacao["status"] == status for operacao in operacoes)


def _preparar_opcoes(resultado: dict[str, Any]) -> list[dict[str, Any]]:
    recomendacao = resultado["recomendacao"]
    if recomendacao is None:
        return []

    opcoes = []
    for posicao, opcao in enumerate(
        [recomendacao, *resultado["alternativas"]]
    ):
        opcoes.append(
            {
                **opcao,
                "chave": (
                    f"{opcao['janela_terminal_id']}--{opcao['transporte_id']}"
                ),
                "recomendada": posicao == 0,
            }
        )
    return opcoes


def _selecionar_opcao(
    opcoes: list[dict[str, Any]],
    chave_solicitada: str | None,
) -> dict[str, Any] | None:
    if not opcoes:
        return None
    if chave_solicitada is None:
        return opcoes[0]

    opcao = next(
        (item for item in opcoes if item["chave"] == chave_solicitada),
        None,
    )
    if opcao is None:
        abort(400, description="O horário selecionado não está disponível.")
    return opcao


def _formatar_data(valor: str) -> str:
    return datetime.fromisoformat(valor).strftime("%d/%m/%Y às %H:%M")


def _classe_status(status: str) -> str:
    return CLASSES_STATUS.get(status, "status-neutro")


app = create_app()


if __name__ == "__main__":
    app.run()
