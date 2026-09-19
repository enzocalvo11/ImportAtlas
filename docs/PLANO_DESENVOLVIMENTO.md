# Plano de Desenvolvimento

## Princípio

Construir uma etapa funcional por vez. Não iniciar melhorias opcionais antes de o fluxo principal estar completo e testado.

## Etapa 0 — Preparação

- Ler todos os documentos do projeto;
- Confirmar a estrutura técnica;
- Criar `.gitignore`;
- Criar `requirements.txt` somente com dependências necessárias;
- Preparar instruções de execução local;
- Fazer um commit da estrutura inicial.

## Etapa 1 — Estrutura básica

- Criar aplicação Flask mínima;
- Criar as pastas `services`, `data`, `templates`, `static/css`, `static/js` e `tests`;
- Criar rota inicial;
- Confirmar que o servidor inicia e a página abre.

Resultado esperado: aplicação vazia, mas executável.

## Etapa 2 — Dados simulados

- Criar operações dos três cenários obrigatórios;
- Criar janelas do terminal;
- Criar disponibilidades do transporte;
- Criar funções para leitura e validação dos arquivos JSON.

Resultado esperado: dados carregados de forma previsível e sem edição manual durante o pitch.

## Etapa 3 — Motor de prontidão

- Implementar regras de prontidão em serviço separado;
- Retornar lista de pendências, responsáveis e próximas ações;
- Criar testes para operação pronta e operação bloqueada.

Resultado esperado: nenhuma operação com pendência pode avançar.

## Etapa 4 — Motor de agendamento

- Filtrar janelas do terminal correto;
- Filtrar transportes disponíveis;
- Calcular compatibilidades;
- Ordenar resultados;
- Retornar recomendação e alternativas;
- Criar teste para o cenário sem compatibilidade.

Resultado esperado: recomendação determinada pelos dados e repetível.

## Etapa 5 — Painel

- Exibir operações e status;
- Adicionar indicadores simples;
- Permitir abrir os detalhes;
- Adicionar ação para iniciar o assistente.

Resultado esperado: usuário consegue localizar e selecionar uma operação.

## Etapa 6 — Interface do assistente

- Exibir checklist de prontidão;
- Exibir pendências ou horários compatíveis;
- Apresentar recomendação e alternativas;
- Exibir confirmação antes do registro.

Resultado esperado: fluxo compreensível sem treinamento técnico.

## Etapa 7 — Confirmação e atualização

- Registrar o agendamento;
- Atualizar o status;
- Impedir reutilização do mesmo horário;
- Mostrar comunicação simulada.

Resultado esperado: fluxo completo do início ao fim.

## Etapa 8 — Testes e demonstração

- Executar os três cenários;
- Corrigir mensagens e estados incorretos;
- Conferir responsividade básica;
- Criar um roteiro curto de demonstração;
- Fazer commit da versão estável.

## Somente se houver tempo

1. Melhorias visuais;
2. Filtros e histórico;
3. SQLite;
4. Explicações com IA gratuita ou local, sem tornar o MVP dependente dela.

## Divisão sugerida para quatro integrantes

- Integrante 1: backend e regras de prontidão;
- Integrante 2: motor de agendamento e dados simulados;
- Integrante 3: dashboard e interface do assistente;
- Integrante 4: integração, testes, documentação e roteiro do pitch.

Todos devem utilizar Git e evitar editar simultaneamente o mesmo arquivo sem combinar antes.

