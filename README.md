# ImportAtlas — Assistente de Agendamento

Protótipo desenvolvido para o Porto Hack Santos 2026. A solução organiza e automatiza o processo entre a liberação de uma carga e o agendamento de sua retirada.

## Situação atual

O repositório possui a estrutura inicial executável do MVP. As regras de prontidão, os dados simulados e o fluxo de agendamento ainda não foram implementados.

## Tecnologias planejadas

- Python;
- Flask;
- HTML;
- CSS;
- JavaScript puro;
- JSON no primeiro MVP;
- Git para controle de versão.

## Execução local

Requisitos: Python 3 instalado.

No PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Acesse `http://127.0.0.1:5000` no navegador.

O Flask é a única dependência externa nesta etapa. Ele fornece o servidor web, as rotas e a renderização dos arquivos HTML. Os testes usam o módulo `unittest`, incluído no Python.

Para executar o teste da página inicial:

```powershell
python -m unittest discover -s tests
```

## Primeira instrução para o Codex

Abra o chat do Codex no VS Code e envie:

```text
Leia o AGENTS.md, o README.md e todos os arquivos Markdown da pasta docs. Depois, analise o repositório e apresente um plano curto para criar somente a estrutura inicial do MVP. Não implemente funcionalidades ainda e não adicione dependências sem explicar a necessidade.
```

Depois de revisar o plano, autorize a criação da estrutura inicial. Faça um commit antes de iniciar a primeira funcionalidade.

## Princípio do projeto

Primeiro entregar o fluxo essencial funcionando com dados simulados. Melhorias visuais, banco de dados e recursos de IA somente serão considerados após o MVP estar estável.
