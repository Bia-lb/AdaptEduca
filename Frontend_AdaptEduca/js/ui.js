
/* Utilitários de interface compartilhados pelas telas conectadas à API. */

(function () {
  const esc = v => String(v ?? '').replace(/[&<>'"]/g, c => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[c]));

  const fmtDate = iso =>
    iso ? String(iso).slice(0, 10).split('-').reverse().join('/') : 'sem prazo';

  const fmtMin = m => {
    m = Math.round(m || 0);
    return m >= 60
      ? `${Math.floor(m / 60)}h${String(m % 60).padStart(2, '0')}`
      : `${m} min`;
  };

  const fmtNota = n =>
    n == null ? '—' : Number(n).toFixed(1).replace('.', ',');

  const toneOf = pct =>
    pct >= 70 ? 'good' : pct >= 50 ? 'warn' : 'bad';

  const statusTone = s => ({
    'Excelente': 'good',
    'Bom desempenho': 'good',
    'Acompanhar': 'warn',
    'Precisa de atenção': 'bad'
  }[s] || '');

  const pill = (text, tone = '') =>
    `<span class="ui-pill ${tone}">${esc(text)}</span>`;

  const stat = (label, value, tone = '') =>
    `<div class="ui-stat tone-${tone}">
      <strong>${esc(value)}</strong>
      <small>${esc(label)}</small>
    </div>`;

  const stats = items =>
    `<section class="ui-stats">${items.map(i => stat(...i)).join('')}</section>`;

  const bar = pct =>
    `<div class="ui-bar ${toneOf(pct)}"
       role="progressbar"
       aria-valuenow="${Math.round(pct)}"
       aria-valuemin="0"
       aria-valuemax="100">
       <span style="width:${Math.max(0, Math.min(100, pct))}%"></span>
    </div>`;

  const empty = msg =>
    `<div class="ui-empty">${esc(msg)}</div>`;

  const section = (title, html) =>
    `<section class="ui-section">
      <h2>${esc(title)}</h2>
      ${html}
    </section>`;

  const card = html =>
    `<div class="card card-pad">${html}</div>`;

  function bars(items, fmt = v => v) {
    const max = Math.max(1, ...items.map(i => i.value || 0));

    return `<div class="ui-bars">
      ${items.map(i => `
        <div title="${esc(i.label)}: ${esc(fmt(i.value))}">
          <b>${esc(i.value ? fmt(i.value) : '')}</b>
          <span class="col" style="height:${Math.round((i.value || 0) / max * 100)}%"></span>
          <small>${esc(i.label)}</small>
        </div>
      `).join('')}
    </div>`;
  }

  const semanaLabel = iso =>
    iso.slice(8, 10) + '/' + iso.slice(5, 7);

  function evolucao(rel) {
    const ev = rel.evolucao || [];

    if (!ev.length) {
      return empty('Ainda não há dados de evolução.');
    }

    return `
      <div class="ui-row" style="align-items:flex-start;gap:30px">
        <div style="flex:1;min-width:240px">
          <h3 style="font-size:.95rem">Atividades enviadas por semana</h3>
          ${bars(ev.map(e => ({
            label: semanaLabel(e.semana),
            value: e.atividadesEnviadas
          })))}
        </div>

        <div style="flex:1;min-width:240px">
          <h3 style="font-size:.95rem">Minutos de estudo por semana</h3>
          ${bars(ev.map(e => ({
            label: semanaLabel(e.semana),
            value: e.minutosEstudo
          })))}
        </div>
      </div>`;
  }

  function materiasHtml(rel) {
    if (!rel.materias.length) {
      return empty('Sem matérias ainda: o aluno precisa estar em uma turma.');
    }

    return `<div class="ui-list">
      ${rel.materias.map(m => {
        const pct = m.atividades
          ? m.enviadas / m.atividades * 100
          : 0;

        return `
          <div class="card card-pad">
            <div class="ui-row">
              <strong>${esc(m.materia)}</strong>
              <span class="muted small">
                ${m.enviadas}/${m.atividades} enviadas
                ${m.atrasadas ? ` · ${m.atrasadas} em atraso` : ''}
                · média ${fmtNota(m.mediaNota)}
              </span>
            </div>
            ${bar(pct)}
          </div>`;
      }).join('')}
    </div>`;
  }

  function relatorioCompleto(rel, opcoes = {}) {
    const a = rel.atividades;
    const dificeis = [...(rel.materiasDificeis || [])];

    return `
      <div class="ui-row">
        <div>
          <strong style="font-size:1.1rem">${esc(rel.aluno.nome)}</strong>
          <span class="muted small">
            mat. ${esc(rel.aluno.matricula)} · últimos ${rel.periodoDias} dias
          </span>
        </div>
        ${pill(rel.status, statusTone(rel.status))}
      </div>

      <div class="ui-stats" style="margin-top:14px">
        ${stat('Progresso', rel.progresso + '%', 'blue')}
        ${stat('Desempenho (notas)', rel.desempenho == null
          ? '—'
          : rel.desempenho + '%',
          rel.desempenho == null
            ? ''
            : toneOf(rel.desempenho) === 'good'
              ? 'green'
              : toneOf(rel.desempenho) === 'bad'
                ? 'red'
                : 'purple'
        )}
        ${stat('Atividades enviadas', `${a.enviadas}/${a.total}`, 'green')}
        ${stat('Em atraso', a.atrasadas, a.atrasadas ? 'red' : '')}
        ${stat('Tempo de estudo', fmtMin(rel.tempoEstudoMinutos), 'purple')}
        ${stat('Média das notas', fmtNota(rel.mediaNota), '')}
      </div>

      ${section('Por disciplina', materiasHtml(rel))}
      ${section('Evolução semanal', evolucao(rel))}

      ${section('Pontos de atenção',
        dificeis.length || rel.dificuldadeDeclarada
          ? `<div class="card card-pad">
              ${dificeis.length
                ? `<p><strong>Dificuldade nos resultados:</strong> ${dificeis.map(esc).join(', ')}</p>`
                : ''}
              ${rel.dificuldadeDeclarada
                ? `<p><strong>Dificuldade informada pelo aluno:</strong> ${esc(rel.dificuldadeDeclarada)}</p>`
                : ''}
             </div>`
          : empty('Nenhum ponto de atenção no período.')
      )}

      ${rel.proximasAtividades.length
        ? section('Próximas atividades', `
            <div class="ui-list">
              ${rel.proximasAtividades.map(p => `
                <div class="card card-pad ui-row">
                  <span>
                    <strong>${esc(p.titulo)}</strong>
                    <span class="muted small">${esc(p.materia)}</span>
                  </span>
                  <span class="muted small">${fmtDate(p.prazo)}</span>
                </div>
              `).join('')}
            </div>`)
        : ''}

      ${opcoes.ia === false
        ? ''
        : `<div
            class="ia-slot"
            data-ia-aluno="${Number(rel.aluno.id)}"
            data-ia-dias="${Number(rel.periodoDias) || 30}"
            hidden
            style="margin-top:16px"
          ></div>`}
    `;
  }

  // ==========================================
  // EXECUÇÃO DAS PÁGINAS
  // ==========================================

  function page(name, fn) {
    document.addEventListener('DOMContentLoaded', async () => {
      if (document.body.dataset.page !== name) return;

      try {
        await fn(document.querySelector('#app'));
      } catch (e) {
        console.error(e);
        window.showToast?.(
          e.message || 'Erro ao carregar a página.',
          'error'
        );

        const a = document.querySelector('#app');

        if (a && a.dataset.loading) {
          a.innerHTML = empty(
            e.message || 'Erro ao carregar.'
          );
        }
      }
    });
  }

  const api = () => window.AdaptEducaAPI;

  function modal(
    title,
    html,
    actions = '<button class="btn btn-light modal-close" type="button">Fechar</button>'
  ) {
    window.openModal(esc(title), html, actions);

    return [
      ...document.querySelectorAll('.modal-backdrop')
    ].pop();
  }

  const closeModals = () =>
    document.querySelectorAll('.modal-backdrop')
      .forEach(m => m.remove());

  // ==========================================
  // VOZ — NARRAÇÃO EM PORTUGUÊS (RF09)
  // ==========================================

  const Voz = {

    suportada: () => 'speechSynthesis' in window,

    velocidade: 1,

    _ativo: false,

    _sessao: 0,

    parar() {
      // Invalida eventos da reprodução anterior.
      Voz._sessao += 1;
      Voz._ativo = false;

      if (Voz.suportada()) {
        window.speechSynthesis.cancel();
      }
    },

    falar(segmentos, { onSegmento, onFim } = {}) {

      if (!Voz.suportada()) {
        window.showToast?.(
          'Seu navegador não suporta leitura em voz alta.',
          'error'
        );
        return;
      }

      // Interrompe a narração anterior.
      Voz.parar();

      if (!Array.isArray(segmentos) || !segmentos.length) {
        return;
      }

      Voz._ativo = true;

      // Identifica esta sessão de narração.
      const sessao = Voz._sessao;

      const vozes = window.speechSynthesis
        .getVoices()
        .filter(v =>
          v.lang &&
          v.lang.toLowerCase().startsWith('pt')
        );

      let i = 0;

      function proximo() {

        // Ignora eventos de reproduções canceladas.
        if (
          sessao !== Voz._sessao ||
          !Voz._ativo
        ) {
          return;
        }

        if (i >= segmentos.length) {
          Voz._ativo = false;
          onFim?.();
          return;
        }

        const u = new SpeechSynthesisUtterance(
          segmentos[i]
        );

        u.lang = 'pt-BR';

        if (vozes.length) {
          u.voice =
            vozes.find(v => v.lang === 'pt-BR') ||
            vozes[0];
        }

        // Aplica a velocidade escolhida.
        u.rate = Voz.velocidade;

        onSegmento?.(i);

        u.onend = function () {

          if (sessao !== Voz._sessao) return;

          i += 1;
          proximo();
        };

        u.onerror = function () {

          if (sessao !== Voz._sessao) return;

          Voz._ativo = false;
          onFim?.();
        };

        window.speechSynthesis.speak(u);
      }

      proximo();
    }
  };

  // Para a voz ao sair da página.
  window.addEventListener('pagehide', () => {
    Voz.parar();
  });

  // ==========================================
  // APRESENTAÇÃO DOS MODOS DE ADAPTAÇÃO
  // ==========================================

  function renderAdaptacaoBase(host, modo, r) {

    Voz.parar();

    if (modo === 'resumo') {

      host.innerHTML = `
        <div class="ad-box">
          <h3>Resumo</h3>
          <ul class="ad-list">
            ${r.pontos.map(p =>
              `<li>${esc(p)}</li>`
            ).join('')}
          </ul>

          <div class="ad-key">
            ${(r.palavrasChave || []).map(k => pill(k)).join('')}
          </div>

          <p class="muted small" style="margin-top:12px">
            Reduzido para ${esc(r.reducao)}.
          </p>
        </div>`;

    } else if (modo === 'simplificado') {

      host.innerHTML = `
        <div class="ad-box">
          <h3>Texto simplificado</h3>
          ${r.paragrafos.map(p =>
            `<p>${esc(p)}</p>`
          ).join('')}
        </div>`;

    } else if (modo === 'tdah') {

      host.innerHTML = `
        <div class="ad-box">
          <h3>Adaptado para foco (TDAH)</h3>
          <p class="muted small">
            ${esc(r.dica)}
            Tempo total estimado: ${r.tempoTotal} min.
          </p>

          <div style="margin-top:14px">
            ${r.blocos.map(b => {

              let html = b.itens.map(esc).join(' ');

              b.destaques.forEach(d => {
                html = html.replace(
                  new RegExp(
                    `(${d.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`,
                    'gi'
                  ),
                  '<mark>$1</mark>'
                );
              });

              return `
                <div class="ad-block">
                  <h4>
                    <span>${esc(b.titulo)}</span>
                    <span class="muted small">
                      ≈ ${b.minutos} min
                    </span>
                  </h4>

                  <p>${html}</p>

                  <div class="ad-check">
                    ${esc(b.checkpoint)}
                  </div>
                </div>`;
            }).join('')}
          </div>
        </div>`;

    } else if (modo === 'tea') {

      host.innerHTML = `
        <div class="ad-box ad-tea">
          <h3>Adaptado (TEA)</h3>

          <p>${esc(r.visaoGeral)}</p>
          <p class="muted">${esc(r.estrutura)}</p>

          <ol>
            ${r.passos.map(p =>
              `<li>${esc(p)}</li>`
            ).join('')}
          </ol>

          ${r.glossario.length
            ? `
              <h4 style="margin-top:18px">
                Palavras importantes
              </h4>
              <ul class="ad-list">
                ${r.glossario.map(g =>
                  `<li>
                    <strong>${esc(g.termo)}</strong>:
                    ${esc(g.exemplo)}
                  </li>`
                ).join('')}
              </ul>`
            : ''}

          ${r.expressoes.length
            ? `
              <h4 style="margin-top:18px">
                Expressões figuradas
              </h4>
              <ul class="ad-list">
                ${r.expressoes.map(e =>
                  `<li>
                    “${esc(e.expressao)}” significa:
                    ${esc(e.significado)}.
                  </li>`
                ).join('')}
              </ul>`
            : ''}

          <p class="muted small" style="margin-top:14px">
            ${esc(r.aviso)}
          </p>
        </div>`;

    } else if (modo === 'mapa') {

      host.innerHTML = `
        <div class="ad-mm">

          <div class="ad-mm-center">
            ${esc(r.centro)}
          </div>

          <div class="ad-mm-branches">
            ${r.ramos.map(b => `
              <div class="ad-mm-branch">
                <strong>${esc(b.titulo)}</strong>
                <ul>
                  ${b.filhos.map(f =>
                    `<li>${esc(f)}</li>`
                  ).join('')}
                </ul>
              </div>
            `).join('')}
          </div>
        </div>`;

    } else if (modo === 'audio') {

      // ======================================
      // INTERFACE DO ÁUDIO
      // ======================================

      host.innerHTML = `
        <div class="ad-audio">

          <button
            class="btn btn-primary"
            type="button"
            data-voz="play"
          >
            ▶ Ouvir
          </button>

          <button
            class="btn btn-light"
            type="button"
            data-voz="stop"
          >
            ■ Parar
          </button>

          <label class="small">
            Velocidade

            <select
              data-voz="rate"
              class="input"
              style="width:auto;display:inline-block"
            >
             
            <option value="0.5">Lenta (0,5×)</option>
            <option value="1">Normal (1×)</option>
            <option value="2">Rápida (2×)</option>

            </select>
          </label>

          <span class="muted small">
            ≈ ${fmtMin(Math.ceil(r.duracaoSegundos / 60))}
            · ${r.palavras} palavras
          </span>

          <div class="seg" style="flex-basis:100%">
            ${r.segmentos.map((s, i) =>
              `<p data-seg="${i}">${esc(s)}</p>`
            ).join('')}
          </div>
        </div>

        ${Voz.suportada()
          ? ''
          : `<p class="muted small" style="margin-top:8px">
              Seu navegador não tem leitura em voz alta.
              Use o texto acima.
             </p>`}
      `;

      // ======================================
      // ELEMENTOS DE CONTROLE
      // ======================================

      const segs = [
        ...host.querySelectorAll('[data-seg]')
      ];

      const botaoOuvir = host.querySelector(
        '[data-voz="play"]'
      );

      const botaoParar = host.querySelector(
        '[data-voz="stop"]'
      );

      const seletorVelocidade = host.querySelector(
        '[data-voz="rate"]'
      );

      // Parágrafo atual da narração.
      let indiceAtual = 0;

      // Mantém a velocidade selecionada.
      seletorVelocidade.value = String(
        Voz.velocidade
      );

      // ======================================
      // DESTAQUE DO PARÁGRAFO
      // ======================================

      function limparDestaques() {
        segs.forEach(paragrafo => {
          paragrafo.classList.remove('on');
        });
      }

      function destacarParagrafo(indice) {
        indiceAtual = indice;

        segs.forEach((paragrafo, posicao) => {
          paragrafo.classList.toggle(
            'on',
            posicao === indice
          );
        });
      }

      // ======================================
      // INICIAR NARRAÇÃO
      // ======================================

      function iniciarLeitura(inicio = 0) {

        if (!Array.isArray(r.segmentos) ||
            !r.segmentos.length) {
          return;
        }

        if (!Voz.suportada()) {
          window.showToast?.(
            'Seu navegador não suporta narração.',
            'error'
          );
          return;
        }

        const inicioSeguro = Math.max(
          0,
          Math.min(
            inicio,
            r.segmentos.length - 1
          )
        );

        const segmentosRestantes =
          r.segmentos.slice(inicioSeguro);

        Voz.falar(segmentosRestantes, {

          onSegmento: function (indice) {

            destacarParagrafo(
              inicioSeguro + indice
            );
          },

          onFim: function () {
            limparDestaques();
          }

        });
      }

      // ======================================
      // BOTÃO OUVIR
      // ======================================

      botaoOuvir.onclick = function () {

        indiceAtual = 0;

        iniciarLeitura(0);
      };

      // ======================================
      // BOTÃO PARAR
      // ======================================

      botaoParar.onclick = function () {

        Voz.parar();

        indiceAtual = 0;

        limparDestaques();
      };

      // ======================================
      // ALTERAR VELOCIDADE DURANTE O ÁUDIO
      // ======================================

      seletorVelocidade.onchange = function (evento) {

        const novaVelocidade = Number(
          evento.target.value
        );

        
        const velocidadesPermitidas = [
          0.5,
          1,
          2
        ];


        if (!velocidadesPermitidas.includes(novaVelocidade)) {
          return;
        }

        // Verifica se a voz está reproduzindo.
        const estavaOuvindo =
          Voz._ativo === true;

        // Atualiza a velocidade.
        Voz.velocidade = novaVelocidade;

        // Reinicia a partir do parágrafo atual,
        // usando a nova velocidade.
        if (estavaOuvindo) {
          iniciarLeitura(indiceAtual);
        }

        window.showToast?.(
          'Velocidade do áudio atualizada!',
          'success'
        );
      };

    } else if (modo === 'flashcards') {

      host.innerHTML = r.cartoes.length
        ? `
          <p class="muted small">
            Toque no cartão para ver a resposta.
          </p>

          <div class="ad-flip">
            ${r.cartoes.map(c => `
              <button
                type="button"
                class="ad-card"
                data-front="${esc(c.frente)}"
                data-back="${esc(c.verso)}"
              >
                <small>Pergunta</small>
                ${esc(c.frente)}
              </button>
            `).join('')}
          </div>`
        : empty('Texto curto demais para gerar cartões.');

      host.querySelectorAll('.ad-card')
        .forEach(b => {

          b.onclick = () => {

            const virado = b.classList.toggle('flipped');

            b.innerHTML = `
              <small>
                ${virado ? 'Resposta' : 'Pergunta'}
              </small>
              ${esc(
                virado
                  ? b.dataset.back
                  : b.dataset.front
              )}
            `;
          };
        });
    }
  }

  // ==========================================
  // ADAPTAÇÃO COM IA
  // ==========================================

  function renderAdaptacao(host, modo, r) {

    renderAdaptacaoBase(host, modo, r);

    if (r && r.fonte) {

      host.insertAdjacentHTML(
        'beforeend',
        `<p
          class="ia-fonte muted small"
          style="margin-top:12px"
        >
          ${r.fonte === 'ia'
            ? '✨ Adaptado por IA a partir do texto original. Confira as informações importantes.'
            : 'Adaptado por regras automáticas (a IA não foi usada).'}
        </p>`
      );
    }
  }

  let _statusIA = null;

  const iaStatus = () =>
    _statusIA ||
    (_statusIA = window.AdaptEducaAPI
      .get('/ia/status')
      .then(r => r.dados)
      .catch(() => ({ disponivel: false })));

  function analiseHtml(d) {

    const lista = (t, itens) =>
      itens && itens.length
        ? `
          <h4 style="margin:12px 0 4px">
            ${t}
          </h4>
          <ul class="ad-list">
            ${itens.map(i =>
              `<li>${esc(i)}</li>`
            ).join('')}
          </ul>`
        : '';

    return `
      <p>${esc(d.resumo)}</p>

      ${lista('Pontos fortes', d.pontosFortes)}
      ${lista('Pontos de atenção', d.pontosDeAtencao)}
      ${lista('Sugestões', d.sugestoes)}

      <p class="muted small" style="margin-top:12px">
        ✨ Gerado por IA a partir dos dados de desempenho.
        Pode conter imprecisões; use como apoio,
        não como diagnóstico.
      </p>`;
  }

  async function ativarSlotsIA() {

    const slots = [
      ...document.querySelectorAll(
        '.ia-slot:not([data-ok])'
      )
    ];

    if (!slots.length) return;

    slots.forEach(s => {
      s.dataset.ok = '1';
    });

    if (!(await iaStatus()).disponivel) return;

    slots.forEach(slot => {

      slot.hidden = false;

      slot.innerHTML = `
        <div class="card card-pad">

          <div class="ui-row">
            <div>
              <strong>Análise com IA</strong>

              <div class="muted small">
                Um assistente lê o desempenho
                e sugere próximos passos.
              </div>
            </div>

            <button
              type="button"
              class="btn btn-primary ia-btn"
            >
              ✨ Gerar análise com IA
            </button>
          </div>

          <div
            class="ia-out"
            aria-live="polite"
            style="margin-top:12px"
          ></div>
        </div>`;
    });
  }

  document.addEventListener('click', async e => {

    const btn = e.target.closest('.ia-btn');

    if (!btn) return;

    const slot = btn.closest('.ia-slot');
    const saida = slot.querySelector('.ia-out');

    btn.disabled = true;
    btn.textContent = 'Analisando…';
    saida.innerHTML = '';

    try {

      const r = await window.AdaptEducaAPI.post(
        `/progresso/aluno/${slot.dataset.iaAluno}/analise`,
        {
          dias: Number(slot.dataset.iaDias) || 30
        }
      );

      saida.innerHTML = analiseHtml(r.dados);

      btn.textContent = '↻ Gerar novamente';

    } catch (err) {

      saida.innerHTML = `
        <p class="muted">
          ${esc(err.message)}
        </p>`;

      btn.textContent = '✨ Tentar novamente';

    } finally {

      btn.disabled = false;
    }
  });

  document.addEventListener('DOMContentLoaded', () => {

    ativarSlotsIA();

    new MutationObserver(ativarSlotsIA)
      .observe(document.body, {
        childList: true,
        subtree: true
      });
  });

  // ==========================================
  // TUTOR COM IA
  // ==========================================

  async function tutorPerguntar({
    conteudoId,
    texto,
    historico
  }) {

    const corpo = {
      mensagens: historico.slice(-10)
    };

    if (conteudoId) {
      corpo.conteudo_id = conteudoId;
    } else if (texto) {
      corpo.texto = texto;
    }

    return (
      await window.AdaptEducaAPI.post(
        '/tutor/mensagem',
        corpo
      )
    ).dados.resposta;
  }

  function tutorChat(host, {
    conteudoId,
    texto
  } = {}) {

    const historico = [];

    host.innerHTML = `
      <div
        class="chat-messages"
        style="max-height:320px;overflow:auto"
      >
        <div class="chat-bubble">
          Oi! Sou o tutor de IA.
          Pergunte o que não entendeu neste conteúdo.
        </div>
      </div>

      <form
        class="chat-form"
        style="display:flex;gap:8px;margin-top:10px"
      >
        <input
          class="input"
          name="message"
          maxlength="1000"
          placeholder="Digite sua dúvida"
          autocomplete="off"
          aria-label="Sua dúvida"
          required
        >

        <button
          class="btn btn-primary"
          type="submit"
        >
          Enviar
        </button>
      </form>

      <p class="muted small" style="margin-top:6px">
        Respostas geradas por IA podem errar.
        Em dúvida, pergunte ao seu professor.
      </p>`;

    const msgs = host.querySelector('.chat-messages');
    const form = host.querySelector('form');

    const bolha = (t, cls = '') => {

      const d = document.createElement('div');

      d.className = `chat-bubble ${cls}`;
      d.style.whiteSpace = 'pre-wrap';
      d.textContent = t;

      msgs.appendChild(d);

      msgs.scrollTop = msgs.scrollHeight;

      return d;
    };

    form.onsubmit = async ev => {

      ev.preventDefault();

      const input = form.elements.message;
      const pergunta = input.value.trim();

      if (!pergunta) return;

      input.value = '';

      bolha(pergunta, 'user');

      historico.push({
        role: 'user',
        content: pergunta
      });

      const espera = bolha('Pensando…');

      form.querySelector('button').disabled = true;

      try {

        const t = typeof texto === 'function'
          ? texto()
          : texto;

        const resposta = await tutorPerguntar({
          conteudoId,
          texto: t,
          historico
        });

        espera.textContent = resposta;

        historico.push({
          role: 'assistant',
          content: resposta
        });

      } catch (err) {

        historico.pop();

        espera.textContent =
          err.message ||
          'O tutor não conseguiu responder agora.';

      } finally {

        form.querySelector('button').disabled = false;

        msgs.scrollTop = msgs.scrollHeight;
      }
    };
  }

  // ==========================================
  // DISPONIBILIZAR FUNÇÕES GLOBALMENTE
  // ==========================================

  window.UI = {
    esc,
    fmtDate,
    fmtMin,
    fmtNota,
    toneOf,
    statusTone,
    pill,
    stat,
    stats,
    bar,
    empty,
    section,
    card,
    bars,
    evolucao,
    materiasHtml,
    relatorioCompleto,
    page,
    api,
    modal,
    closeModals,
    Voz,
    renderAdaptacao,
    iaStatus,
    tutorChat,
    tutorPerguntar,
    analiseHtml
  };

})();
