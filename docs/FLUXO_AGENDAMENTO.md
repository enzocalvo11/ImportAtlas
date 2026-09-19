# Fluxo do Assistente de Agendamento

## 1. Início

O usuário acessa o Painel de Operações e seleciona uma carga. Em seguida, clica em **Verificar e agendar retirada**.

## 2. Verificação de prontidão

O sistema verifica as condições obrigatórias e monta uma checklist visual.

Exemplo:

```text
Liberação aduaneira: concluída
Documentação: concluída
Tributos e pagamentos: concluídos
Liberação do terminal: pendente
Bloqueios: nenhum
```

## 3. Caminho com pendência

Se uma ou mais condições estiverem pendentes:

1. Interromper a busca de horários.
2. Atualizar o status para `Com pendências`.
3. Mostrar todas as pendências impeditivas.
4. Indicar o responsável e a próxima ação.
5. Não exibir botão de confirmação de agendamento.

Mensagem de exemplo:

```text
O agendamento ainda não pode ser realizado.
Pendência: liberação administrativa do terminal.
Responsável: equipe operacional.
Próxima ação: solicitar a regularização ao terminal.
```

## 4. Caminho com operação pronta

Quando não existirem pendências:

1. Atualizar o status para `Pronta para agendamento`.
2. Buscar janelas futuras disponíveis no terminal correto.
3. Buscar disponibilidades futuras de transporte.
4. Calcular as interseções de horário.
5. Ordenar as combinações pelo início mais próximo.

## 5. Regra de compatibilidade

Uma combinação é válida quando existe sobreposição suficiente entre a janela do terminal e a disponibilidade do transporte.

No primeiro MVP, usar uma duração fixa de atendimento configurável. Exemplo: 60 minutos.

```text
início possível = maior valor entre os dois horários de início
fim possível = menor valor entre os dois horários de fim

se fim possível - início possível >= duração necessária:
    combinação compatível
```

## 6. Resultado sem compatibilidade

Quando não existir combinação:

- Atualizar o status para `Sem horário compatível`;
- Informar que a carga está apta, mas as disponibilidades não coincidem;
- Orientar o usuário a atualizar as janelas ou a disponibilidade de transporte;
- Não inventar horários.

## 7. Recomendação

Quando existirem combinações:

- A primeira será a recomendada;
- Até duas combinações seguintes serão alternativas;
- O sistema explicará que a opção foi escolhida por ser a primeira compatibilidade disponível.

Mensagem de exemplo:

```text
A operação está pronta para retirada.
Horário recomendado: 22/09 às 14h.
Essa é a primeira compatibilidade entre a janela do terminal e a disponibilidade do transporte.
```

## 8. Confirmação

Antes de registrar, mostrar um resumo com:

- Operação;
- Carga;
- Terminal;
- Data e horário;
- Transportadora e veículo;
- Participantes que seriam comunicados.

O registro somente acontece quando o usuário clicar em **Confirmar agendamento**.

## 9. Finalização

Depois da confirmação:

1. Criar o registro do agendamento;
2. Atualizar a operação para `Agendamento confirmado`;
3. Marcar a janela e o transporte como utilizados no conjunto de dados;
4. Exibir a confirmação;
5. Simular a comunicação aos envolvidos.

## 10. Regra de segurança

O frontend nunca será responsável sozinho por decidir a prontidão ou registrar o agendamento. As verificações e regras principais devem ser executadas no backend.

