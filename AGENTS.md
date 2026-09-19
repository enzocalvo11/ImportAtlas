# AGENTS.md

## Projeto

Este repositório contém o protótipo do **ImportAtlas — Assistente de Agendamento de Retirada**, desenvolvido para o Porto Hack Santos 2026.

Antes de executar qualquer tarefa, leia:

1. `README.md`;
2. `docs/CONTEXTO_PORTO_HACK.md`;
3. `docs/REQUISITOS_MVP.md`;
4. `docs/FLUXO_AGENDAMENTO.md`;
5. `docs/PLANO_DESENVOLVIMENTO.md`.

## Objetivo principal

Construir um protótipo web simples que reduza o intervalo entre a liberação de uma carga e o agendamento de sua retirada. O sistema deve verificar a prontidão da operação, identificar pendências, cruzar janelas simuladas do terminal com a disponibilidade simulada do transporte, recomendar o primeiro horário viável e solicitar confirmação humana.

## Regras de desenvolvimento

- Priorize um MVP funcional do início ao fim.
- Use linguagem simples em textos, mensagens e explicações.
- Evite arquitetura complexa, microsserviços e dependências desnecessárias.
- Stack inicial: Python, Flask, HTML, CSS e JavaScript puro.
- Use arquivos JSON no início. Migre para SQLite somente se o MVP já estiver funcionando e a mudança trouxer benefício claro.
- Não dependa de Azure OpenAI, APIs pagas ou modelos de IA para o funcionamento principal.
- Não adicione React, TypeScript, Docker ou frameworks adicionais sem necessidade comprovada e autorização do usuário.
- Não implemente integrações reais com terminais, transportadoras, Siscomex ou Portal Único. Essas fontes serão simuladas no protótipo.
- Nunca apresente uma integração simulada como se fosse real.
- Nunca permita agendamento quando existir uma pendência impeditiva.
- O usuário deve confirmar antes de registrar o agendamento.
- A solução não cria disponibilidade no terminal; ela encontra e organiza as opções disponíveis.
- A IA é uma melhoria opcional e posterior. Se adicionada, deverá apenas explicar resultados ou preparar comunicações. As decisões de prontidão e compatibilidade continuam no código.
- Não coloque senhas, tokens ou chaves no código. Use variáveis de ambiente e mantenha `.env` fora do Git.
- Preserve alterações existentes do usuário e evite reescrever arquivos sem necessidade.

## Forma de trabalhar

Para cada tarefa:

1. Inspecione os arquivos relacionados.
2. Explique brevemente o que será alterado.
3. Faça apenas as alterações necessárias para a tarefa atual.
4. Execute verificações ou testes adequados.
5. Informe os arquivos modificados, o resultado dos testes e qualquer limitação restante.

Se um requisito estiver ambíguo e mudar significativamente o comportamento, pergunte antes de implementar. Para escolhas pequenas e reversíveis, use a opção mais simples e registre a decisão.

## Padrão de qualidade

- Nomes de variáveis e funções claros.
- Funções pequenas e com responsabilidade única.
- Separar regras de negócio das rotas e da interface.
- Mensagens de erro compreensíveis para usuários leigos.
- Interface responsiva o suficiente para notebook e celular.
- Estados vazios, carregamento e falhas devem ter mensagens visíveis.
- Dados da demonstração devem ser determinísticos para que o pitch possa ser repetido sem surpresas.

## Escopo protegido

O dashboard é complementar. A prioridade é o fluxo:

`operação selecionada → verificação de prontidão → pendência ou busca de horários → recomendação → confirmação → atualização do status`.

