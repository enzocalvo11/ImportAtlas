import json
from datetime import datetime
from pathlib import Path
from typing import Any


DIRETORIO_DADOS = Path(__file__).resolve().parent.parent / "data"

ESQUEMA_OPERACAO = {
    "id": str,
    "importador": str,
    "container": str,
    "terminal": str,
    "chegada_prevista": str,
    "liberacao_aduaneira": bool,
    "documentacao_concluida": bool,
    "tributos_regularizados": bool,
    "liberacao_terminal": bool,
    "possui_bloqueio": bool,
    "responsaveis": dict,
    "status": str,
}

ESQUEMA_JANELA_TERMINAL = {
    "id": str,
    "terminal": str,
    "inicio": str,
    "fim": str,
    "disponivel": bool,
}

ESQUEMA_DISPONIBILIDADE_TRANSPORTE = {
    "id": str,
    "operacao_id": str,
    "transportadora": str,
    "veiculo": str,
    "inicio": str,
    "fim": str,
    "disponivel": bool,
}

CAMPOS_RESPONSAVEIS = {
    "aduana",
    "documentacao",
    "tributos",
    "terminal",
    "bloqueio",
    "transporte",
}


class ErroDados(ValueError):
    """Indica que um arquivo de dados está ausente ou inválido."""


def carregar_operacoes(
    diretorio_dados: Path = DIRETORIO_DADOS,
) -> list[dict[str, Any]]:
    registros = _carregar_colecao(
        diretorio_dados / "operacoes.json",
        ESQUEMA_OPERACAO,
        campos_data=("chegada_prevista",),
    )
    _validar_responsaveis(registros)
    return registros


def carregar_janelas_terminal(
    diretorio_dados: Path = DIRETORIO_DADOS,
) -> list[dict[str, Any]]:
    registros = _carregar_colecao(
        diretorio_dados / "janelas_terminal.json",
        ESQUEMA_JANELA_TERMINAL,
        campos_data=("inicio", "fim"),
    )
    _validar_intervalos(registros, "janelas do terminal")
    return registros


def carregar_disponibilidades_transporte(
    diretorio_dados: Path = DIRETORIO_DADOS,
) -> list[dict[str, Any]]:
    registros = _carregar_colecao(
        diretorio_dados / "disponibilidades_transporte.json",
        ESQUEMA_DISPONIBILIDADE_TRANSPORTE,
        campos_data=("inicio", "fim"),
    )
    _validar_intervalos(registros, "disponibilidades de transporte")
    return registros


def _carregar_colecao(
    caminho: Path,
    esquema: dict[str, type],
    campos_data: tuple[str, ...],
) -> list[dict[str, Any]]:
    try:
        with caminho.open(encoding="utf-8") as arquivo:
            registros = json.load(arquivo)
    except FileNotFoundError as erro:
        raise ErroDados(f"Arquivo de dados não encontrado: {caminho.name}.") from erro
    except json.JSONDecodeError as erro:
        raise ErroDados(f"O arquivo {caminho.name} contém JSON inválido.") from erro

    if not isinstance(registros, list):
        raise ErroDados(f"O arquivo {caminho.name} deve conter uma lista.")

    _validar_registros(registros, esquema, campos_data, caminho.name)
    return registros


def _validar_registros(
    registros: list[Any],
    esquema: dict[str, type],
    campos_data: tuple[str, ...],
    nome_arquivo: str,
) -> None:
    identificadores: set[str] = set()

    for posicao, registro in enumerate(registros, start=1):
        if not isinstance(registro, dict):
            raise ErroDados(
                f"O item {posicao} de {nome_arquivo} deve ser um objeto."
            )

        campos_ausentes = esquema.keys() - registro.keys()
        if campos_ausentes:
            campos = ", ".join(sorted(campos_ausentes))
            raise ErroDados(
                f"O item {posicao} de {nome_arquivo} não possui: {campos}."
            )

        for campo, tipo_esperado in esquema.items():
            valor = registro[campo]
            if not isinstance(valor, tipo_esperado):
                raise ErroDados(
                    f"O campo '{campo}' do item {posicao} de {nome_arquivo} "
                    "possui tipo inválido."
                )
            if isinstance(valor, str) and not valor.strip():
                raise ErroDados(
                    f"O campo '{campo}' do item {posicao} de {nome_arquivo} "
                    "não pode estar vazio."
                )

        identificador = registro["id"]
        if identificador in identificadores:
            raise ErroDados(
                f"O arquivo {nome_arquivo} possui o ID duplicado '{identificador}'."
            )
        identificadores.add(identificador)

        for campo in campos_data:
            _converter_data(registro[campo], campo, identificador, nome_arquivo)


def _validar_intervalos(
    registros: list[dict[str, Any]],
    descricao: str,
) -> None:
    for registro in registros:
        inicio = datetime.fromisoformat(registro["inicio"])
        fim = datetime.fromisoformat(registro["fim"])
        if inicio >= fim:
            raise ErroDados(
                f"O registro {registro['id']} de {descricao} deve terminar após o início."
            )


def _validar_responsaveis(registros: list[dict[str, Any]]) -> None:
    for registro in registros:
        responsaveis = registro["responsaveis"]
        campos_ausentes = CAMPOS_RESPONSAVEIS - responsaveis.keys()
        if campos_ausentes:
            campos = ", ".join(sorted(campos_ausentes))
            raise ErroDados(
                f"A operação {registro['id']} não possui responsáveis para: {campos}."
            )

        for papel, responsavel in responsaveis.items():
            if not isinstance(responsavel, str) or not responsavel.strip():
                raise ErroDados(
                    f"O responsável por '{papel}' na operação {registro['id']} "
                    "deve ser um texto preenchido."
                )


def _converter_data(
    valor: str,
    campo: str,
    identificador: str,
    nome_arquivo: str,
) -> datetime:
    try:
        return datetime.fromisoformat(valor)
    except ValueError as erro:
        raise ErroDados(
            f"O campo '{campo}' do registro {identificador} em {nome_arquivo} "
            "deve usar uma data ISO válida."
        ) from erro
