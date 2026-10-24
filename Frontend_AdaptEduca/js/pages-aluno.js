/* Telas do aluno: dashboard, conteúdos + modos de estudo, histórico, perfil (RF04, RF07-RF10, RF13, RF14, RF16). */
(function () {
  const { esc, fmtDate, fmtMin, fmtNota, pill, stats, section, bar, empty, page, api, Voz } = UI;
  const eu = () => AdaptAuth.session();
  const MODOS_FORMATO = [['para-mim', 'Para mim'], ['resumo', 'Resumo'], ['simplificado', 'Texto simplificado'], ['tdah', 'Foco (TDAH)'], ['tea', 'Estruturado (TEA)'], ['mapa', 'Mapa mental']];
  const NOME_MODO = Object.fromEntries(MODOS_FORMATO);

  // ── sessões de estudo (RF14/RF16) ────────────────────────────────────────
  const Sessao = {
    atual: null,
    iniciar(conteudoId, modo) { Sessao.parar(); Sessao.atual = { conteudoId, modo, inicio: Date.now() }; },
    parar(keepalive = false) {
      const s = Sessao.atual; Sessao.atual = null;
      if (!s) return;
      const segundos = Math.round((Date.now() - s.inicio) / 1000);
      if (segundos < 5) return;
      const corpo = { modo: s.modo, segundos: Math.min(segundos, 4 * 3600), conteudo_id: s.conteudoId };
      api().request('/estudo/sessoes', { method: 'POST', body: JSON.stringify(corpo), keepalive }).catch(() => {});
    },
  };
  window.addEventListener('pagehide', () => Sessao.parar(true));

  // ── Dashboard (RF16) ──────────────────────────────────────────────────────
  page('dashboard-aluno', async app => {
    const perfil = (await api().get('/alunos/me')).dados;
    const [rel, ativ, conts] = await Promise.all([
      api().get(`/progresso/aluno/${perfil.id}`), api().get('/atividades/'), api().get('/conteudos/')]);
    const r = rel.dados;
    app.dataset.loading = '';
    const sub = document.querySelector('#heroSub');
    if (sub && perfil.learningMethods.length) sub.textContent = `Seu método de aprendizagem preferido: ${perfil.learningMethods.join(', ')}`;
    const pendentes = ativ.dados.filter(a => a.status === 'Pendente').sort((a, b) => (a.prazo || '9999').localeCompare(b.prazo || '9999'));
    const hoje = new Date().toISOString().slice(0, 10);
    app.innerHTML = stats([
      ['Atividades concluídas', `${r.atividades.enviadas}/${r.atividades.total}`, 'green'], ['Pendentes', r.atividades.pendentes, 'blue'],
      ['Progresso', r.progresso + '%', 'purple'], ['Tempo de estudo (30 dias)', fmtMin(r.tempoEstudoMinutos), '']])
      + `<div class="ui-actions" style="margin:-6px 0 6px"><a class="btn btn-primary" href="conteudos-aluno.html">Estudar agora</a><a class="btn btn-light" href="adaptacao-conteudo.html">Adaptar um texto</a></div>`
      + section('Para fazer', pendentes.length ? `<div class="ui-list">${pendentes.slice(0, 5).map(a => `<div class="card card-pad ui-row"><span><strong>${esc(a.titulo)}</strong> <span class="muted small">${esc(a.turmaNome || '')}</span></span><span>${a.prazo && a.prazo < hoje ? pill('Atrasada', 'bad') : pill(a.prazo ? 'até ' + fmtDate(a.prazo) : 'sem prazo')} <a class="btn btn-light" href="atividades-aluno.html">Abrir</a></span></div>`).join('')}</div>` : empty('Tudo em dia! Nenhuma atividade pendente.'))
      + section('Conteúdos novos', conts.dados.length ? `<div class="ui-list">${conts.dados.slice(0, 3).map(c => `<div class="card card-pad ui-row"><span><strong>${esc(c.titulo)}</strong> <span class="muted small">${esc(c.turmaNome)} · ${fmtDate(c.dataPostagem)}</span></span><a class="btn btn-light" href="conteudos-aluno.html?id=${c.id}">Estudar</a></div>`).join('')}</div>` : empty('Seus professores ainda não publicaram conteúdos.'))
      + `<div class="ia-slot" data-ia-aluno="${perfil.id}" data-ia-dias="30" hidden style="margin-bottom:16px"></div>`
      + section('Seu desempenho por disciplina', UI.materiasHtml(r))
      + section('Sua evolução', UI.evolucao(r))
      + (r.materiasDificeis.length ? section('Vale revisar', `<div class="card card-pad">Você foi melhor em outras matérias. Reforce: <strong>${r.materiasDificeis.map(esc).join(', ')}</strong>. Use o modo Revisão (flashcards) nos conteúdos.</div>`) : '');
  });

  // ── Conteúdos + modos de estudo (RF06, RF07, RF13, RF14) ──────────────────
  page('conteudos-aluno', async app => {
    const [lista, modos] = await Promise.all([api().get('/conteudos/'), api().get('/estudo/modos')]);
    app.dataset.loading = '';
    const itens = lista.dados, cfg = modos.dados;
    const abrir = id => viewer(app, itens.find(c => c.id === id), cfg, () => mostrarLista());
    function mostrarLista() {
      Sessao.parar(); Voz.parar();
      const turmas = ['Todas', ...new Set(itens.map(c => c.turmaNome))];
      app.innerHTML = `<div class="page-title-row"><div><h2>Biblioteca de conteúdos</h2><p class="muted small">${itens.length} conteúdo(s) · modo recomendado para você: <strong>${esc(NOME_MODO[cfg.recomendado] || cfg.recomendado)}</strong></p></div><a class="btn btn-light" href="adaptacao-conteudo.html">✣ Adaptar um texto</a></div>
        <div class="ui-tabs" id="fTurmas">${turmas.map((t, i) => `<button type="button" class="${i ? '' : 'active'}" data-t="${esc(t)}">${esc(t)}</button>`).join('')}</div><div class="ui-list" id="cLista"></div>`;
      const desenhar = t => {
        const l = itens.filter(c => t === 'Todas' || c.turmaNome === t);
        app.querySelector('#cLista').innerHTML = l.length ? l.map(c => `<div class="card card-pad ui-row"><span><strong>${esc(c.titulo)}</strong><br><span class="muted small">${esc(c.turmaNome)} · ${esc(c.tipo)} · ${fmtDate(c.dataPostagem)}</span></span><button class="btn btn-primary" data-abrir="${c.id}" type="button">Estudar</button></div>`).join('') : empty('Nenhum conteúdo publicado ainda.');
        app.querySelectorAll('[data-abrir]').forEach(b => b.onclick = () => abrir(Number(b.dataset.abrir)));
      };
      app.querySelector('#fTurmas').onclick = e => { const b = e.target.closest('[data-t]'); if (!b) return; app.querySelectorAll('#fTurmas button').forEach(x => x.classList.toggle('active', x === b)); desenhar(b.dataset.t); };
      desenhar('Todas');
    }
    const pedido = Number(new URLSearchParams(location.search).get('id'));
    if (pedido && itens.some(c => c.id === pedido)) abrir(pedido); else mostrarLista();
  });

  async function viewer(app, item, cfg, voltar) {
    const conteudo = (await api().get(`/conteudos/${item.id}`)).dados;
    let modoEstudo = 'leitura', formato = 'para-mim';
    const foco = cfg.modos.find(m => m.id === 'foco');
    app.innerHTML = `<div class="ui-row" style="margin-bottom:12px"><button class="btn btn-light" id="vVoltar" type="button">← Conteúdos</button><div><strong>${esc(conteudo.titulo)}</strong> <span class="muted small">${esc(item.turmaNome)}</span></div></div>
      ${conteudo.temPdf ? '<p><button class="btn btn-light" id="vPdf" type="button">Baixar PDF original</button></p>' : ''}
      <div class="ui-tabs" id="vModos">${cfg.modos.map(m => `<button type="button" data-m="${m.id}" class="${m.id === 'leitura' ? 'active' : ''}" title="${esc(m.descricao)}">${esc(m.nome)}</button>`).join('')}</div>
      <div id="vFormatos" class="ui-tabs">${MODOS_FORMATO.map(([id, nome]) => `<button type="button" data-f="${id}" class="${id === 'para-mim' ? 'active' : ''}">${esc(nome)}${id === cfg.recomendado ? ' ★' : ''}</button>`).join('')}</div>
      <p class="muted small" id="vDesc"></p><div id="vCorpo" class="card card-pad"><p class="muted">Carregando…</p></div>
      <details id="vTutorBox" class="card card-pad" style="margin-top:14px" hidden><summary><strong>💬 Tirar dúvidas com o tutor de IA</strong></summary><div id="vTutor" style="margin-top:10px"></div></details>`;
    const $ = s => app.querySelector(s);
    $('#vVoltar').onclick = voltar;
    if (conteudo.texto) UI.iaStatus().then(st => { if (st.disponivel) { $('#vTutorBox').hidden = false; UI.tutorChat($('#vTutor'), { conteudoId: item.id }); } });
    $('#vPdf')?.addEventListener('click', async () => {
      try {
        const r = await fetch(`${api().base}/conteudos/${item.id}/arquivo`, { headers: { Authorization: `Bearer ${api().getToken()}` } });
        if (!r.ok) throw new Error('Não foi possível baixar o PDF.');
        const url = URL.createObjectURL(await r.blob()); const a = document.createElement('a'); a.href = url; a.download = conteudo.arquivoOriginal || 'conteudo.pdf'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 5000);
      } catch (e) { window.showToast?.(e.message, 'error'); }
    });

    const buscar = async modo => (await api().get(`/conteudos/${item.id}/adaptacao?modo=${modo}`)).dados;
    async function desenhar() {
      Voz.parar(); clearInterval(desenhar.timer);
      const corpo = $('#vCorpo');
      $('#vFormatos').hidden = !(modoEstudo === 'leitura');
      $('#vDesc').textContent = cfg.modos.find(m => m.id === modoEstudo).descricao;
      Sessao.iniciar(item.id, modoEstudo);
      if (!conteudo.texto) { corpo.innerHTML = empty('Este conteúdo é apenas um link — abra-o pelo endereço informado pelo professor.') + (conteudo.arquivo ? `<p style="margin-top:12px"><a href="${esc(conteudo.arquivo)}" target="_blank" rel="noopener noreferrer">${esc(conteudo.arquivo)}</a></p>` : ''); return; }
      corpo.innerHTML = '<p class="muted">Gerando adaptação…</p>';
      try {
        if (modoEstudo === 'leitura') {
          const d = await buscar(formato);
          corpo.innerHTML = d.recomendado ? `<p class="muted small" style="margin-bottom:10px">Adaptado para o seu perfil: <strong>${esc(NOME_MODO[d.modo])}</strong></p><div id="vRender"></div>` : '<div id="vRender"></div>';
          UI.renderAdaptacao($('#vRender'), d.modo, d.resultado);
        } else if (modoEstudo === 'revisao') {
          UI.renderAdaptacao(corpo, 'flashcards', (await buscar('flashcards')).resultado);
        } else if (modoEstudo === 'audio') {
          UI.renderAdaptacao(corpo, 'audio', (await buscar('audio')).resultado);
        } else if (modoEstudo === 'foco') {
          await modoFoco(corpo, (await buscar('tdah')).resultado);
        }
      } catch (e) { corpo.innerHTML = empty(e.message); }
    }

    async function modoFoco(corpo, r) {
      let i = 0, fase = 'foco', restante = foco.minutosFoco * 60, rodando = false;
      const fmt = s => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
      const pintar = () => {
        const b = r.blocos[i];
        corpo.innerHTML = `<div class="ad-focus"><div><div class="muted small">${fase === 'foco' ? 'Foco' : 'Pausa — respire e movimente-se'}</div><div class="ad-timer" id="fTempo">${fmt(restante)}</div></div>
          <button class="btn btn-primary" id="fIniciar" type="button">${rodando ? 'Pausar' : 'Iniciar'}</button><button class="btn btn-light" id="fReset" type="button">Reiniciar</button>
          <span class="muted small">Blocos de ${foco.minutosFoco} min com pausa de ${foco.minutosPausa} min</span></div>
          <p class="muted small">Parte ${i + 1} de ${r.totalBlocos}</p>
          <div class="ad-block"><h4><span>${esc(b.titulo)}</span><span class="muted small">≈ ${b.minutos} min</span></h4><p>${(() => { let h = b.itens.map(esc).join(' '); b.destaques.forEach(d => { h = h.replace(new RegExp(`(${d.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'), '<mark>$1</mark>'); }); return h; })()}</p><div class="ad-check">${esc(b.checkpoint)}</div></div>
          <div class="ui-actions"><button class="btn btn-light" id="fPrev" type="button" ${i ? '' : 'disabled'}>← Anterior</button><button class="btn btn-primary" id="fNext" type="button" ${i === r.blocos.length - 1 ? 'disabled' : ''}>Próxima parte →</button></div>`;
        $('#fIniciar').onclick = () => { rodando = !rodando; pintar(); };
        $('#fReset').onclick = () => { fase = 'foco'; restante = foco.minutosFoco * 60; rodando = false; pintar(); };
        $('#fPrev').onclick = () => { i--; pintar(); }; $('#fNext').onclick = () => { i++; pintar(); };
      };
      pintar();
      desenhar.timer = setInterval(() => {
        if (!rodando) return;
        restante -= 1; const t = $('#fTempo'); if (t) t.textContent = fmt(Math.max(restante, 0));
        if (restante <= 0) {
          fase = fase === 'foco' ? 'pausa' : 'foco'; restante = (fase === 'foco' ? foco.minutosFoco : foco.minutosPausa) * 60;
          window.showToast?.(fase === 'pausa' ? 'Hora da pausa! Descanse um pouco.' : 'Pausa acabou. Vamos voltar ao foco!', 'success'); pintar();
        }
      }, 1000);
    }

    $('#vModos').onclick = e => { const b = e.target.closest('[data-m]'); if (!b) return; modoEstudo = b.dataset.m; app.querySelectorAll('#vModos button').forEach(x => x.classList.toggle('active', x === b)); desenhar(); };
    $('#vFormatos').onclick = e => { const b = e.target.closest('[data-f]'); if (!b) return; formato = b.dataset.f; app.querySelectorAll('#vFormatos button').forEach(x => x.classList.toggle('active', x === b)); desenhar(); };
    await desenhar();
  }

  // ── Histórico (RF16) ──────────────────────────────────────────────────────
  page('historico-aluno', async app => {
    const perfil = (await api().get('/alunos/me')).dados;
    const [rel, ativ, sess] = await Promise.all([api().get(`/progresso/aluno/${perfil.id}`), api().get('/atividades/'), api().get('/estudo/sessoes')]);
    const r = rel.dados;
    app.dataset.loading = '';
    const eventos = [
      ...ativ.dados.filter(a => a.minhaResposta?.enviadaEm).map(a => ({ quando: a.minhaResposta.enviadaEm, titulo: a.titulo, texto: `Enviou a atividade${a.nota != null ? ` · nota ${fmtNota(a.nota)}` : ''}${a.feedbacks?.length ? ` · feedback: “${a.feedbacks[0].mensagem}”` : ''}.` })),
      ...sess.dados.map(s => ({ quando: s.iniciadaEm, titulo: s.conteudoTitulo || 'Estudo livre', texto: `Estudou ${fmtMin(Math.round(s.segundos / 60))} no modo ${s.modo}.` }))]
      .sort((a, b) => b.quando.localeCompare(a.quando)).slice(0, 25);
    app.innerHTML = stats([['Tempo estudado (30 dias)', fmtMin(r.tempoEstudoMinutos), 'purple'], ['Atividades enviadas', r.atividades.enviadas, 'green'], ['Sessões de estudo', r.sessoes, 'blue'], ['Média das notas', fmtNota(r.mediaNota), '']])
      + section('Atividade recente', eventos.length ? `<div class="ui-list">${eventos.map(e => `<div class="card card-pad"><span class="muted small">${fmtDate(e.quando)}</span><h4>${esc(e.titulo)}</h4><p class="muted">${esc(e.texto)}</p></div>`).join('')}</div>` : empty('Quando você estudar e enviar atividades, o histórico aparece aqui.'))
      + section('Sua evolução', UI.evolucao(r));
  });

  // ── Perfil (RF04) ─────────────────────────────────────────────────────────
  page('perfil-aluno', async app => {
    const p = (await api().get('/alunos/me')).dados, q = p.questionario || {};
    app.dataset.loading = '';
    const linha = (rotulo, v) => v && (!Array.isArray(v) || v.length) ? `<p><strong>${rotulo}:</strong> ${esc(Array.isArray(v) ? v.join(', ') : v)}</p>` : '';
    app.innerHTML = `<form class="card form-card" id="perfilForm" style="max-width:720px"><div class="form-row">
      <div class="ui-field"><label>Nome</label><input class="input" name="nome" value="${esc(p.nome)}" required></div>
      <div class="ui-field"><label>Data de nascimento</label><input class="input" type="date" name="dataNascimento" value="${esc(p.dataNascimento || '')}"></div></div>
      <p class="muted small">E-mail: ${esc(p.email)} · Matrícula: ${esc(p.matricula)} (informe ao professor ou responsável para vincular você)</p>
      <button class="btn btn-primary" type="submit" style="margin-top:12px">Salvar alterações</button></form>
      <div class="card card-pad" style="max-width:720px;margin-top:20px"><div class="ui-row"><h3>Meu perfil de aprendizagem</h3><a class="btn btn-light" href="questionario-aluno.html">Refazer questionário</a></div>
      ${p.questionarioConcluido ? `<div style="margin-top:10px;display:grid;gap:4px">${linha('Formatos preferidos', q.formats)}${linha('Matéria mais difícil', q.dificuldade)}${linha('Necessidades', q.necessidades)}${linha('Melhor horário', q.horario)}${linha('Concentração', q.concentracao)}${linha('Explicações', q.explicacoes)}</div><p class="muted small" style="margin-top:10px">Essas respostas são vistas só por você. Elas escolhem o formato adaptado dos conteúdos.</p>` : '<p class="muted">Você ainda não respondeu o questionário.</p>'}</div>`;
    app.querySelector('#perfilForm').onsubmit = async e => {
      e.preventDefault(); const f = new FormData(e.target);
      try { await api().put(`/alunos/${p.id}`, { nome: f.get('nome').trim(), dataNascimento: f.get('dataNascimento') || null });
        const s = AdaptAuth.session(); if (s) { s.name = f.get('nome').trim(); localStorage.setItem('adapteduca_session', JSON.stringify(s)); }
        window.showToast?.('Perfil atualizado!', 'success'); }
      catch (err) { window.showToast?.(err.message, 'error'); }
    };
  });
})();
