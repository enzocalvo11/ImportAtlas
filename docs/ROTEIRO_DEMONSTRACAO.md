# Roteiro de Demonstração do MVP

## Preparação

1. Inicie a aplicação e abra `http://127.0.0.1:5000`.
2. No painel, clique em **Restaurar demonstração** e confirme.
3. Explique que todos os dados e todas as comunicações exibidas são simulados.

## Cenário A — Operação pronta

1. Na operação `OP-001`, clique em **Verificar e agendar**.
2. Mostre a checklist concluída.
3. Destaque o primeiro horário recomendado e as duas alternativas.
4. Selecione uma opção e confira o resumo.
5. Clique em **Confirmar agendamento**.
6. Mostre o registro criado, a comunicação simulada e o novo status no painel.

Mensagem principal: o sistema cruza as disponibilidades, recomenda a primeira opção viável e mantém a decisão final com o usuário.

## Cenário B — Operação com pendência

1. Na operação `OP-002`, clique em **Verificar e agendar**.
2. Mostre a documentação pendente, o motivo, o responsável e a próxima ação.
3. Destaque que nenhum horário e nenhum botão de confirmação são exibidos.

Mensagem principal: uma carga com pendência impeditiva nunca pode ser agendada.

## Cenário C — Sem compatibilidade

1. Na operação `OP-003`, clique em **Verificar e agendar**.
2. Mostre que a checklist está concluída.
3. Destaque a mensagem de que terminal e transporte não possuem horários coincidentes.

Mensagem principal: o sistema não cria disponibilidade nem inventa horários.

## Encerramento

Volte ao painel e use **Restaurar demonstração** para repetir os cenários. Reforce que o MVP utiliza JSON local e não possui integrações reais com terminais, transportadoras ou sistemas governamentais.
