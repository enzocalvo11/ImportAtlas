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

  function selecionarHorario(cartao) {
    cartoes.forEach((item) => {
      const selecionado = item === cartao;
      const rotulo = item.querySelector("[data-rotulo-selecionado]");
      const seletor = item.querySelector("[data-selecionar-horario]");

      item.classList.toggle("cartao-selecionado", selecionado);
      rotulo.hidden = !selecionado;
      seletor.textContent = selecionado
        ? "Horário selecionado"
        : "Selecionar este horário";

      if (selecionado) {
        seletor.setAttribute("aria-current", "true");
      } else {
        seletor.removeAttribute("aria-current");
      }
    });

    camposResumo.terminal.textContent = cartao.dataset.terminal;
    camposResumo.inicio.textContent = cartao.dataset.inicioFormatado;
    camposResumo.transportadora.textContent = cartao.dataset.transportadora;
    camposResumo.veiculo.textContent = cartao.dataset.veiculo;
    campoJanela.value = cartao.dataset.janelaTerminalId;
    campoTransporte.value = cartao.dataset.transporteId;

    const url = new URL(window.location.href);
    url.searchParams.set("opcao", cartao.dataset.chave);
    window.history.replaceState({}, "", url);
  }

  gradeHorarios.addEventListener("click", (evento) => {
    const seletor = evento.target.closest("[data-selecionar-horario]");
    if (!seletor) {
      return;
    }

    evento.preventDefault();
    selecionarHorario(seletor.closest("[data-opcao-horario]"));
  });
}
