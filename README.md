# ImportAtlas — Assistente de Agendamento

Protótipo desenvolvido para o Porto Hack Santos 2026. A solução organiza e automatiza o processo entre a liberação de uma carga e o agendamento de sua retirada.

## Situação atual

O repositório possui o fluxo principal do MVP: dados simulados, verificação de prontidão, recomendação de horários, confirmação humana, registro em JSON e atualização das disponibilidades. As comunicações externas continuam sendo apenas simuladas.

## Tecnologias

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

O Flask é a única dependência externa. Ele fornece o servidor web, as rotas e a renderização dos arquivos HTML. Os testes usam o módulo `unittest`, incluído no Python.

Para executar todos os testes:

```powershell
python -m unittest discover -s tests
```

## Demonstração

O painel possui a ação **Restaurar demonstração**, que remove o agendamento registrado e recupera os três cenários iniciais sem edição manual dos arquivos.

Consulte o roteiro completo em [`docs/ROTEIRO_DEMONSTRACAO.md`](docs/ROTEIRO_DEMONSTRACAO.md).

## Princípio do projeto

Primeiro entregar o fluxo essencial funcionando com dados simulados. Melhorias visuais, banco de dados e recursos de IA somente serão considerados após o MVP estar estável.
