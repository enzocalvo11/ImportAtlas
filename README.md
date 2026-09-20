# ImportAtlas — Assistente de Agendamento

Protótipo desenvolvido para o Porto Hack Santos 2026. A solução organiza e automatiza o processo entre a liberação de uma carga e o agendamento de sua retirada.

## Situação atual

O repositório possui o fluxo completo do MVP: dados simulados, verificação de prontidão, recomendação de horários, solicitação de agendamento, resposta simulada do terminal (confirmação ou recusa, com reagendamento) e atualização das disponibilidades. As comunicações externas continuam sendo apenas simuladas.

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

> Sempre que um arquivo `.py` for alterado, reinicie o servidor (`Ctrl+C` e `python app.py` novamente) — o Flask não recarrega os módulos sozinho neste modo.

## Funcionalidades

### Painel de operações (`/`)

- **Simular recebimento das operações**: carrega as cargas simuladas para o painel (estado inicial vazio, até essa ação ser executada).
- Indicadores de resumo: total de operações, prontas para agendamento, com pendências e agendamentos confirmados.
- Cartão por operação com status colorido e ação principal (ir para os detalhes, iniciar o assistente ou acompanhar uma solicitação já feita).
- **Restaurar demonstração**: descarta qualquer agendamento e recoloca os cenários no estado inicial, para repetir a demonstração sem editar arquivos manualmente.

### Detalhes da operação (`/operacoes/<id>`)

- Dados da carga (importador, contêiner, terminal, chegada prevista) e responsáveis.
- Checklist de prontidão (mesma lógica do assistente) e histórico de agendamento.
- **Simular atualização externa**: aparece apenas quando a operação tem alguma pendência; resolve **todas** as pendências da operação de uma vez, como se as confirmações tivessem chegado por um sistema externo.

### Assistente de agendamento (`/operacoes/<id>/assistente`)

Fluxo em três etapas:

1. **Verificação de prontidão** — checklist com 5 condições, exibidas nesta ordem:
   1. Presença/recepção da carga averbada;
   2. DUIMP desembaraçada, com documentação completa;
   3. Tributos e ICMS regularizados, quando aplicáveis;
   4. Anuências e exigências encerradas;
   5. Despesas portuárias e armazenagem regularizadas.

   Cada condição é avaliada de forma independente: **todas** as que estiverem com valor pendente aparecem, ao mesmo tempo, como cards em "Pendências impeditivas" (descrição, motivo, responsável e próxima ação). O botão **Simular atualização** (só aparece quando há alguma pendência) resolve **todas** de uma vez, para fins de demonstração.

2. **Horários compatíveis** — só é calculada se a operação estiver 100% pronta. O método (em [`services/agendamento_service.py`](services/agendamento_service.py)):
   1. Filtra as janelas do terminal: só entram as marcadas como disponíveis **e** cujo terminal é o mesmo da operação.
   2. Filtra as disponibilidades de transporte: só entram as marcadas como disponíveis **e** vinculadas a essa operação específica.
   3. Cruza cada janela de terminal com cada disponibilidade de transporte (todas as combinações possíveis) e calcula a **interseção** dos três horários envolvidos — chegada prevista da carga, janela do terminal e disponibilidade do transporte: início possível é o mais tardio dos três inícios, fim possível é o mais cedo dos dois fins.
   4. A combinação só é válida se essa interseção durar pelo menos a duração mínima de atendimento configurada (60 minutos por padrão).
   5. Todas as combinações válidas são ordenadas pelo início mais próximo. A primeira vira a **Recomendada**; as duas seguintes viram **Alternativa 1** e **Alternativa 2** (o restante só é contado, não exibido).

   Se nenhuma combinação for válida, o sistema mostra "Sem horário compatível" — ele nunca inventa uma disponibilidade que não exista nos dados. A opção escolhida pelo usuário fica lembrada mesmo se ele sair da página e voltar.

3. **Resumo da solicitação** — aparece após a escolha de um horário; o botão **Solicitar agendamento** registra a solicitação e avança para a resposta do terminal.

### Resposta do terminal (`/agendamentos/<id>`)

Simula o retorno do terminal a uma solicitação:

- **Confirmar horário** → status "Agendamento confirmado".
- **Recusar horário** → status "Agendamento recusado pelo terminal"; a janela e o transporte reservados voltam a ficar disponíveis **para outras operações**, mas essa combinação específica de janela+transporte fica registrada como recusada e não volta a ser oferecida **para esta operação**.
- Se recusado, o botão **Tentar novo horário** reabre o assistente para uma nova escolha (reagendamento), sem precisar refazer a verificação de prontidão. A Etapa 2 já é calculada excluindo qualquer combinação já recusada anteriormente para essa operação.

Nenhuma mensagem real é enviada em nenhuma etapa — todas as comunicações e integrações externas são simuladas e sinalizadas como tal na interface.

## Demonstração

Consulte o roteiro completo em [`docs/ROTEIRO_DEMONSTRACAO.md`](docs/ROTEIRO_DEMONSTRACAO.md).

## Princípio do projeto

Primeiro entregar o fluxo essencial funcionando com dados simulados. Melhorias visuais, banco de dados e recursos de IA somente serão considerados após o MVP estar estável.
