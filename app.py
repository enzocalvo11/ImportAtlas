import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, abort, redirect, render_template, request, session, url_for

from services.agendamento_service import buscar_horarios_compativeis
from services.atualizacao_externa_service import (
    ErroAtualizacaoExterna,
    simular_atualizacao_externa,
)
from services.confirmacao_service import (
    ErroConfirmacao,
    confirmar_agendamento,
    recusar_agendamento,
    solicitar_agendamento,
)
from services.data_service import (
    DIRETORIO_DADOS,
    ErroDados,
    carregar_agendamentos,
    carregar_disponibilidades_transporte,
    carregar_janelas_terminal,
    carregar_operacoes,
)
from services.demonstracao_service import (
    DIRETORIO_BASE_DEMO,
    restaurar_dados_demonstracao,
)
from services.simulacao_service import ErroSimulacao, simular_atualizacao_prontidao
from services.prontidao_service import verificar_prontidao


CLASSES_STATUS = {
    "Aguardando liberação": "status-alerta",
    "Com pendências": "status-erro",
    "Pronta para agendamento": "status-alerta",
    "Sem horário compatível": "status-alerta",
    "Aguardando confirmação": "status-informativo",
    "Aguardando confirmação do terminal": "status-informativo",
    "Agendamento confirmado": "status-sucesso",
    "Agendamento recusado pelo terminal": "status-erro",
}


def create_app(configuracao: dict[str, Any] | None = None) -> Flask:
    """Cria a aplicação web do ImportAtlas."""
    app = Flask(__name__)
    app.secret_key = os.environ.get(
        "SECRET_KEY", "chave-de-desenvolvimento-import-atlas"
    )
    app.config.from_mapping(
        DIRETORIO_DADOS=DIRETORIO_DADOS,
        DIRETORIO_BASE_DEMO=DIRETORIO_BASE_DEMO,
        SECRET_KEY=(
            os.environ.get("IMPORTATLAS_SECRET_KEY") or secrets.token_hex(32)
        ),
    )
    if configuracao:
        app.config.update(configuracao)

    app.jinja_env.filters["data_br"] = _formatar_data
    app.jinja_env.filters["classe_status"] = _classe_status

    @app.get("/")
    def painel_operacoes() -> str:
        operacoes_recebidas = bool(session.get("operacoes_recebidas"))
        diretorio_dados = _diretorio_dados(app)
        operacoes = (
            carregar_operacoes(diretorio_dados) if operacoes_recebidas else []
        )
        agendamentos_por_operacao = (
            {
                agendamento["operacao_id"]: agendamento
                for agendamento in carregar_agendamentos(diretorio_dados)
            }
            if operacoes_recebidas
            else {}
        )
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
            agendamentos_por_operacao=agendamentos_por_operacao,
            operacoes_recebidas=operacoes_recebidas,
            recebimento_simulado=(
                request.args.get("recebimento") == "simulado"
            ),
            atualizacao_simulada=(
                request.args.get("atualizacao") == "simulada"
            ),
            operacao_atualizada=request.args.get("operacao", ""),
            demonstracao_restaurada=(
                request.args.get("demonstracao") == "restaurada"
            ),
        )

    @app.post("/operacoes/simular-recebimento")
    def simular_recebimento_operacoes() -> Any:
        session["operacoes_recebidas"] = True
        return redirect(
            url_for("painel_operacoes", recebimento="simulado"),
            code=303,
        )

    @app.get("/operacoes/<operacao_id>")
    def detalhes_operacao(operacao_id: str) -> str:
        diretorio_dados = _diretorio_dados(app)
        operacao = _buscar_operacao(operacao_id, diretorio_dados)
        agendamento = next(
            (
                item
                for item in carregar_agendamentos(diretorio_dados)
                if item["operacao_id"] == operacao_id
            ),
            None,
        )
        return render_template(
            "operacao.html",
            operacao=operacao,
            agendamento=agendamento,
            prontidao=verificar_prontidao(operacao),
            atualizacao_simulada=(
                request.args.get("atualizacao") == "simulada"
            ),
        )

    @app.get("/operacoes/<operacao_id>/assistente")
    def iniciar_assistente(operacao_id: str) -> Any:
        diretorio_dados = _diretorio_dados(app)
        operacao = _buscar_operacao(operacao_id, diretorio_dados)
        agendamento = _buscar_agendamento_operacao(operacao_id, diretorio_dados)
        if agendamento is not None:
            return redirect(
                url_for(
                    "exibir_agendamento_confirmado",
                    agendamento_id=agendamento["id"],
                )
            )
        resultado = buscar_horarios_compativeis(
            operacao,
            carregar_janelas_terminal(diretorio_dados),
            carregar_disponibilidades_transporte(diretorio_dados),
        )
        opcoes = _preparar_opcoes(resultado)
        opcao_selecionada = _resolver_opcao_selecionada(operacao_id, opcoes)
        participantes = list(dict.fromkeys(operacao["responsaveis"].values()))
        return render_template(
            "assistente_inicio.html",
            operacao=operacao,
            resultado=resultado,
            opcoes=opcoes,
            opcao_selecionada=opcao_selecionada,
            participantes=participantes,
            atualizacao_simulada=(
                request.args.get("atualizacao") == "simulada"
            ),
        )

    @app.post("/operacoes/<operacao_id>/simular-atualizacao-externa")
    def atualizar_operacao_externamente(operacao_id: str) -> Any:
        try:
            simular_atualizacao_externa(
                operacao_id,
                _diretorio_dados(app),
            )
        except ErroAtualizacaoExterna as erro:
            abort(409, description=str(erro))

        origem = request.form.get("origem", "painel")
        if origem == "detalhes":
            destino = url_for(
                "detalhes_operacao",
                operacao_id=operacao_id,
                atualizacao="simulada",
            )
        elif origem == "assistente":
            destino = url_for(
                "iniciar_assistente",
                operacao_id=operacao_id,
                atualizacao="simulada",
            )
        else:
            session["operacoes_recebidas"] = True
            destino = url_for(
                "painel_operacoes",
                atualizacao="simulada",
                operacao=operacao_id,
            )

        return redirect(destino, code=303)

    @app.post("/operacoes/<operacao_id>/simular-atualizacao")
    def simular_atualizacao(operacao_id: str) -> Any:
        try:
            simular_atualizacao_prontidao(operacao_id, _diretorio_dados(app))
        except ErroSimulacao as erro:
            abort(404, description=str(erro))

        session["operacoes_recebidas"] = True
        session.pop(_chave_sessao_selecao(operacao_id), None)
        return redirect(
            url_for("iniciar_assistente", operacao_id=operacao_id),
            code=303,
        )

    @app.post("/operacoes/<operacao_id>/confirmar")
    def confirmar_retirada(operacao_id: str) -> Any:
        janela_terminal_id = request.form.get("janela_terminal_id", "")
        transporte_id = request.form.get("transporte_id", "")
        if not janela_terminal_id or not transporte_id:
            abort(400, description="Selecione um horário antes de solicitar.")

        try:
            resultado = solicitar_agendamento(
                operacao_id,
                janela_terminal_id,
                transporte_id,
                _diretorio_dados(app),
            )
        except ErroConfirmacao as erro:
            abort(409, description=str(erro))

        session.pop(_chave_sessao_selecao(operacao_id), None)
        return redirect(
            url_for(
                "exibir_agendamento_confirmado",
                agendamento_id=resultado["agendamento"]["id"],
            ),
            code=303,
        )

    @app.post("/agendamentos/<agendamento_id>/confirmar")
    def simular_confirmacao_terminal(agendamento_id: str) -> Any:
        try:
            confirmar_agendamento(
                agendamento_id,
                _diretorio_dados(app),
            )
        except ErroConfirmacao as erro:
            abort(409, description=str(erro))

        return redirect(
            url_for(
                "exibir_agendamento_confirmado",
                agendamento_id=agendamento_id,
            ),
            code=303,
        )

    @app.post("/agendamentos/<agendamento_id>/recusar")
    def simular_recusa_terminal(agendamento_id: str) -> Any:
        try:
            recusar_agendamento(
                agendamento_id,
                _diretorio_dados(app),
            )
        except ErroConfirmacao as erro:
            abort(409, description=str(erro))

        return redirect(
            url_for(
                "exibir_agendamento_confirmado",
                agendamento_id=agendamento_id,
            ),
            code=303,
        )

    @app.get("/agendamentos/<agendamento_id>")
    def exibir_agendamento_confirmado(agendamento_id: str) -> str:
        diretorio_dados = _diretorio_dados(app)
        agendamento = _buscar_registro(
            carregar_agendamentos(diretorio_dados),
            agendamento_id,
        )
        if agendamento is None:
            abort(404, description=f"O agendamento {agendamento_id} não existe.")

        operacao = _buscar_operacao(agendamento["operacao_id"], diretorio_dados)
        transporte = _buscar_registro(
            carregar_disponibilidades_transporte(diretorio_dados),
            agendamento["transporte_id"],
        )
        if transporte is None:
            raise ErroDados("O transporte do agendamento não foi encontrado.")

        participantes = list(dict.fromkeys(operacao["responsaveis"].values()))
        comunicacoes = [
            {
                "destinatario": participante,
                "status": "Simulação — mensagem não enviada",
            }
            for participante in participantes
        ]
        return render_template(
            "agendamento_confirmado.html",
            operacao=operacao,
            agendamento=agendamento,
            transporte=transporte,
            comunicacoes=comunicacoes,
        )

    @app.post("/demonstracao/restaurar")
    def restaurar_demonstracao() -> Any:
        restaurar_dados_demonstracao(
            _diretorio_dados(app),
            Path(app.config["DIRETORIO_BASE_DEMO"]),
        )
        session.clear()
        return redirect(
            url_for("painel_operacoes", demonstracao="restaurada"),
            code=303,
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

    @app.errorhandler(409)
    def conflito_de_confirmacao(erro: Any) -> tuple[str, int]:
        return (
            render_template(
                "erro.html",
                titulo="Agendamento não confirmado",
                mensagem=getattr(
                    erro,
                    "description",
                    "O horário não pôde ser confirmado.",
                ),
            ),
            409,
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


def _diretorio_dados(app: Flask) -> Path:
    return Path(app.config["DIRETORIO_DADOS"])


def _buscar_operacao(
    operacao_id: str,
    diretorio_dados: Path,
) -> dict[str, Any]:
    operacao = _buscar_registro(
        carregar_operacoes(diretorio_dados),
        operacao_id,
    )
    if operacao is None:
        abort(404, description=f"A operação {operacao_id} não existe.")
    return operacao


def _buscar_registro(
    registros: list[dict[str, Any]],
    identificador: str,
) -> dict[str, Any] | None:
    return next(
        (registro for registro in registros if registro["id"] == identificador),
        None,
    )


def _buscar_agendamento_operacao(
    operacao_id: str,
    diretorio_dados: Path,
) -> dict[str, Any] | None:
    return next(
        (
            item
            for item in carregar_agendamentos(diretorio_dados)
            if item["operacao_id"] == operacao_id
        ),
        None,
    )


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


def _chave_sessao_selecao(operacao_id: str) -> str:
    return f"opcao_selecionada_{operacao_id}"


def _resolver_opcao_selecionada(
    operacao_id: str,
    opcoes: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Nenhuma opção é pré-selecionada. A escolha do usuário é lembrada na sessão."""
    chave_sessao = _chave_sessao_selecao(operacao_id)
    chave_informada = request.args.get("opcao")

    if chave_informada is not None:
        opcao = _buscar_opcao(opcoes, chave_informada)
        if opcao is None:
            abort(400, description="O horário selecionado não está disponível.")
        session[chave_sessao] = chave_informada
        return opcao

    chave_lembrada = session.get(chave_sessao)
    if chave_lembrada is None:
        return None

    opcao = _buscar_opcao(opcoes, chave_lembrada)
    if opcao is None:
        session.pop(chave_sessao, None)
    return opcao


def _buscar_opcao(
    opcoes: list[dict[str, Any]],
    chave: str,
) -> dict[str, Any] | None:
    return next(
        (item for item in opcoes if item["chave"] == chave),
        None,
    )


def _formatar_data(valor: str) -> str:
    return datetime.fromisoformat(valor).strftime("%d/%m/%Y às %H:%M")


def _classe_status(status: str) -> str:
    return CLASSES_STATUS.get(status, "status-neutro")


app = create_app()


if __name__ == "__main__":
    app.run()
