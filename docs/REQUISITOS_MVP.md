# Requisitos do MVP

## 1. Objetivo do MVP

Demonstrar, de maneira funcional, o caminho completo entre a seleção de uma operação e a confirmação simulada de sua retirada.

## 2. Funcionalidades obrigatórias — P0

### RF01 — Painel de operações

Exibir uma lista de operações com:

- Identificador;
- Importador;
- Carga ou contêiner;
- Terminal;
- Data prevista de chegada;
- Status atual;
- Situação de prontidão;
- Ação para verificar ou iniciar o agendamento.

### RF02 — Detalhes da operação

Permitir abrir uma operação e visualizar seus dados, liberações, pendências, responsável e histórico básico.

### RF03 — Verificação de prontidão

Verificar pelo menos:

- Liberação aduaneira;
- Documentação concluída;
- Tributos e pagamentos regularizados;
- Liberação administrativa do terminal;
- Existência de bloqueio impeditivo.

Uma operação somente estará pronta quando todas as condições obrigatórias forem atendidas.

### RF04 — Tratamento de pendências

Quando houver impedimento, mostrar:

- Qual é a pendência;
- Por que ela impede o agendamento;
- Quem é o responsável;
- Qual é a próxima ação sugerida.

### RF05 — Consulta de disponibilidades simuladas

Ler as janelas disponíveis do terminal e os períodos disponíveis do transporte a partir dos dados locais.

### RF06 — Cruzamento de horários

Encontrar as combinações compatíveis entre terminal e transporte. Ordenar as combinações da mais próxima para a mais distante.

### RF07 — Recomendação

Apresentar:

- Primeira opção viável como recomendação;
- Explicação simples do motivo;
- Até duas alternativas, quando existirem.

### RF08 — Confirmação humana

O agendamento somente será registrado depois que o usuário confirmar a opção escolhida.

### RF09 — Atualização de status

Após a confirmação, atualizar a operação para `Agendamento confirmado` e registrar data, horário, terminal e transporte.

### RF10 — Comunicação simulada

Mostrar quais participantes seriam comunicados. Não enviar mensagens reais na primeira versão.

## 3. Status padronizados

- `Aguardando liberação`;
- `Com pendências`;
- `Pronta para agendamento`;
- `Sem horário compatível`;
- `Aguardando confirmação`;
- `Agendamento confirmado`.

## 4. Dados mínimos

### Operação

- `id`;
- `importador`;
- `container` ou identificação da carga;
- `terminal`;
- `chegada_prevista`;
- `liberacao_aduaneira`;
- `documentacao_concluida`;
- `tributos_regularizados`;
- `liberacao_terminal`;
- `possui_bloqueio`;
- `responsaveis`;
- `status`.

### Janela do terminal

- `id`;
- `terminal`;
- `inicio`;
- `fim`;
- `disponivel`.

### Disponibilidade do transporte

- `id`;
- `transportadora`;
- `veiculo`;
- `inicio`;
- `fim`;
- `disponivel`.

### Agendamento

- `id`;
- `operacao_id`;
- `janela_terminal_id`;
- `transporte_id`;
- `inicio`;
- `fim`;
- `status`;
- `confirmado_em`.

## 5. Cenários obrigatórios da demonstração

### Cenário A — Operação pronta

Todos os requisitos estão concluídos. O sistema encontra horários compatíveis, recomenda a primeira opção e permite confirmar.

### Cenário B — Operação com pendência

Existe uma pendência administrativa ou documental. O sistema interrompe o fluxo e identifica responsável e próxima ação.

### Cenário C — Sem compatibilidade

A carga está pronta, mas nenhuma janela do terminal coincide com a disponibilidade do transporte. O sistema informa o problema sem inventar uma solução.

## 6. Critérios de aceite

O MVP será considerado funcional quando:

- Os três cenários puderem ser repetidos sem alterar manualmente o código;
- Uma operação bloqueada nunca puder ser agendada;
- Uma operação pronta receber uma recomendação baseada nos dados;
- A confirmação atualizar o status corretamente;
- As mensagens forem claras para uma pessoa leiga;
- O sistema puder ser executado localmente com instruções simples;
- Nenhuma API paga for necessária.

## 7. Melhorias posteriores — P1

- Filtros por status, terminal e data;
- Indicadores no dashboard;
- Histórico de alterações;
- Persistência em SQLite;
- Interface mais responsiva;
- Simulação visual de notificações.

## 8. Fora do escopo inicial — P2

- Chatbot ou modelo de IA;
- Login completo e permissões complexas;
- Envio real de mensagens;
- Integrações externas reais;
- Aplicativo móvel;
- Previsões com aprendizado de máquina;
- Arquitetura de microsserviços.

