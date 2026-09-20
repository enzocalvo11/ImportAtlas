from pathlib import Path
from threading import Lock
from typing import Any

from services.data_service import (
    DIRETORIO_DADOS,
    carregar_operacoes,
    salvar_operacoes,
)
from services.prontidao_service import (
    VALORES_ESPERADOS_PRONTIDAO,
    verificar_prontidao,
)


_TRAVA_ATUALIZACAO = Lock()


class ErroAtualizacaoExterna(ValueError):
    """Indica que uma atualização externa simulada não pode ser aplicada."""


def simular_atualizacao_externa(
    operacao_id: str,
    diretorio_dados: Path = DIRETORIO_DADOS,
) -> dict[str, Any]:
    """Conclui as pendências e recalcula o status da operação informada."""
    with _TRAVA_ATUALIZACAO:
        operacoes = carregar_operacoes(diretorio_dados)
        operacao = next(
            (item for item in operacoes if item["id"] == operacao_id),
            None,
        )
        if operacao is None:
            raise ErroAtualizacaoExterna(
                f"A operação {operacao_id} não existe."
            )

        prontidao_anterior = verificar_prontidao(operacao)
        if prontidao_anterior["pronta"]:
            raise ErroAtualizacaoExterna(
                "Esta operação não possui pendências para atualizar."
            )

        campos_atualizados = []
        for pendencia in prontidao_anterior["pendencias"]:
            campo = pendencia["campo"]
            operacao[campo] = VALORES_ESPERADOS_PRONTIDAO[campo]
            campos_atualizados.append(campo)

        prontidao_atual = verificar_prontidao(operacao)
        operacao["status"] = prontidao_atual["status"]
        salvar_operacoes(operacoes, diretorio_dados)

        return {
            "operacao": operacao,
            "campos_atualizados": campos_atualizados,
            "prontidao": prontidao_atual,
        }
