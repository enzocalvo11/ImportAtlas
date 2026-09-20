from pathlib import Path

from services.data_service import (
    DIRETORIO_DADOS,
    carregar_agendamentos,
    carregar_disponibilidades_transporte,
    carregar_janelas_terminal,
    carregar_operacoes,
    salvar_estado_agendamento,
)


DIRETORIO_BASE_DEMO = DIRETORIO_DADOS / "base_demo"


def restaurar_dados_demonstracao(
    diretorio_dados: Path = DIRETORIO_DADOS,
    diretorio_base: Path = DIRETORIO_BASE_DEMO,
) -> None:
    """Restaura os três cenários determinísticos usados na demonstração."""
    salvar_estado_agendamento(
        carregar_operacoes(diretorio_base),
        carregar_janelas_terminal(diretorio_base),
        carregar_disponibilidades_transporte(diretorio_base),
        carregar_agendamentos(diretorio_base),
        diretorio_dados,
    )
