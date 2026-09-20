const gradeHorarios = document.querySelector("[data-assistente-agendamento]");

if (gradeHorarios) {
  const cartoes = [...gradeHorarios.querySelectorAll("[data-opcao-horario]")];
  const camposResumo = {
    terminal: document.querySelector('[data-resumo-horario="terminal"]'),
    inicio: document.querySelector('[data-resumo-horario="inicio"]'),
    transportadora: document.querySelector('[data-resumo-horario="transportadora"]'),
    veiculo: document.querySelector('[data-resumo-horario="veiculo"]'),
  };
  const campoJanela = document.querySelector(
    '[data-campo-horario="janela_terminal_id"]',
  );
  const campoTransporte = document.querySelector(
    '[data-campo-horario="transporte_id"]',
  );
  const avisoSelecao = document.querySelector("[data-aviso-selecao]");
  const resumoConfirmacao = document.querySelector(
    "[data-resumo-confirmacao]",
  );

  function atualizarSelecao(cartao) {
    cartoes.forEach((item) => {
      const selecionado = item === cartao;
      const rotulo = item.querySelector("[data-rotulo-selecionado]");
      const seletor = item.querySelector("[data-selecionar-horario]");

      item.classList.toggle("cartao-selecionado", selecionado);
      rotulo.hidden = !selecionado;
      seletor.textContent = selecionado
        ? "Desmarcar horário"
        : "Selecionar este horário";

      if (selecionado) {
        seletor.setAttribute("aria-current", "true");
      } else {
        seletor.removeAttribute("aria-current");
      }
    });

    avisoSelecao.hidden = Boolean(cartao);
    resumoConfirmacao.hidden = !cartao;

    const url = new URL(window.location.href);
    if (!cartao) {
      Object.values(camposResumo).forEach((campo) => {
        campo.textContent = "";
      });
      campoJanela.value = "";
      campoTransporte.value = "";
      url.searchParams.set("opcao", "");
      window.history.replaceState({}, "", url);
      return;
    }

    camposResumo.terminal.textContent = cartao.dataset.terminal;
    camposResumo.inicio.textContent = cartao.dataset.inicioFormatado;
    camposResumo.transportadora.textContent = cartao.dataset.transportadora;
    camposResumo.veiculo.textContent = cartao.dataset.veiculo;
    campoJanela.value = cartao.dataset.janelaTerminalId;
    campoTransporte.value = cartao.dataset.transporteId;

    url.searchParams.set("opcao", cartao.dataset.chave);
    window.history.replaceState({}, "", url);
  }

  gradeHorarios.addEventListener("click", (evento) => {
    const seletor = evento.target.closest("[data-selecionar-horario]");
    if (!seletor) {
      return;
    }
    if (
      !campoJanela ||
      !campoTransporte ||
      !avisoSelecao ||
      !resumoConfirmacao
    ) {
      return;
    }

    evento.preventDefault();
    const cartao = seletor.closest("[data-opcao-horario]");
    atualizarSelecao(
      cartao.classList.contains("cartao-selecionado") ? null : cartao,
    );
  });
}
