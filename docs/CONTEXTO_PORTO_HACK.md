# Contexto do Porto Hack Santos 2026

## 1. Origem do projeto

O projeto nasceu durante o Porto Hack Santos 2026, na trilha Hack, a partir de uma pesquisa sobre o novo processo de importação com a DUIMP. A equipe possui quatro integrantes e começou a investigação buscando compreender o comportamento dos importadores, as dificuldades para preparar operações antecipadamente e os fatores que atrasam a retirada das cargas.

O cenário inicialmente estudado foi a retirada direta. A hipótese era que a DUIMP poderia agilizar a liberação quando os dados, documentos, pagamentos e a logística estivessem organizados, mas que barreiras financeiras, cadastrais, regulatórias e operacionais poderiam limitar esse benefício.

## 2. Evidências que orientaram a solução

As entrevistas e os materiais pesquisados mostraram que:

- Muitas informações da operação ficam dispersas entre planilhas, sistemas, documentos, mensagens e diferentes participantes.
- O controle ainda pode ser manual e dependente de planilhas Excel.
- A falta de integração aumenta o tempo gasto em conferências e acompanhamento.
- Processos mais complexos exigem fiscalização constante das informações.
- Mesmo depois da liberação aduaneira, fatores administrativos, operacionais e logísticos podem impedir a retirada imediata.
- Empresas pequenas podem ter maior dificuldade para adotar sistemas completos e caros.
- A antecipação da operação depende de qualidade dos dados, organização, disponibilidade financeira, documentação e planejamento logístico.

A despachante aduaneira Martha Losso destacou a falta de integração das informações, o controle manual por planilhas e a utilidade de uma solução simples para pequenas empresas do setor.

## 3. Evolução da ideia

A primeira solução proposta foi a **Central de Prontidão da Operação**, também chamada de **Painel de Integração**. Ela centralizaria informações da carga e mostraria prontidão, pendências, responsáveis e prazos.

Após mentorias com Martha Losso e Marco Riveiros, a solução principal evoluiu para o **Assistente de Agendamento de Retirada**. O painel passou a ser uma parte complementar.

A mudança tornou a proposta mais objetiva: não apenas mostrar informações, mas utilizar essas informações para adiantar a preparação da retirada depois que os processos legais e burocráticos estiverem concluídos.

## 4. Problema escolhido

Existe um intervalo entre a liberação da carga e o agendamento de sua retirada. Nesse período, profissionais precisam verificar manualmente pendências, disponibilidade física e administrativa, janelas do terminal e disponibilidade do transporte. As informações dispersas podem gerar contatos repetidos, perda de tempo, perda de janelas e menor previsibilidade.

## 5. Solução proposta

O ImportAtlas será um aplicativo web com um assistente visual e automatizado. Ele deverá:

1. Receber ou consultar as informações da operação.
2. Verificar se todas as condições obrigatórias foram concluídas.
3. Interromper o processo quando houver pendências.
4. Informar a pendência, o responsável e a próxima ação.
5. Consultar janelas simuladas do terminal.
6. Consultar a disponibilidade simulada do transporte.
7. Cruzar os horários.
8. Recomendar a primeira opção viável e apresentar alternativas.
9. Solicitar confirmação humana.
10. Registrar o agendamento e simular a comunicação aos envolvidos.

## 6. Público principal

- Despachantes aduaneiros;
- Equipes operacionais de pequenas importadoras;
- Pequenas empresas que controlam operações com planilhas e ferramentas dispersas.

Transportadoras, terminais e operadores logísticos aparecem como participantes do fluxo, mas não precisam possuir acesso completo no primeiro MVP.

## 7. O que significa “assistente”

O assistente não precisa ser um chatbot. Na primeira versão, será um fluxo visual baseado em regras, com checklist, mensagens automáticas, recomendação de horário e botões de confirmação.

Um chat com inteligência artificial pode ser acrescentado futuramente para explicar pendências, responder perguntas e preparar mensagens. Ele não é necessário para o funcionamento do MVP.

## 8. Limites e transparência

- O protótipo utilizará dados simulados.
- Não haverá integração real com sistemas governamentais, terminais ou transportadoras.
- O sistema não cria janelas disponíveis.
- O sistema não substitui decisões legais, aduaneiras ou operacionais.
- O sistema somente agenda quando os dados indicam que a operação está apta.
- O agendamento exige confirmação do usuário.
- Comunicações externas serão demonstradas como simulação.

## 9. Resultado esperado

Demonstrar que a centralização das informações e o cruzamento automático das disponibilidades podem reduzir verificações manuais, acelerar a preparação da retirada, evitar perda de janelas e aumentar a previsibilidade operacional.

