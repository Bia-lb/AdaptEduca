/* Telas do responsável (RF19, RF20): só mostram os filhos vinculados com matrícula + e-mail. */
(function () {
  const { esc, fmtDate, fmtMin, fmtNota, pill, statusTone, stats, section, bar, empty, page, api, modal } = UI;

  const formVincular = () => `<form id="vincularForm" class="card form-card" style="max-width:560px"><h3>Vincular um filho</h3>
    <p class="muted small">Para sua segurança, informe a matrícula e o e-mail cadastrados pelo aluno (a matrícula aparece no perfil dele).</p>
    <div class="ui-field"><label>Matrícula</label><input class="input" name="matricula" required></div>
    <div class="ui-field"><label>E-mail do aluno</label><input class="input" type="email" name="email" required></div>
    <button class="btn btn-primary" type="submit">Vincular</button></form>`;

  function ligarVinculo(app, recarregar) {
    const f = app.querySelector('#vincularForm');
    if (!f) return;
    f.onsubmit = async e => {
      e.preventDefault(); const d = new FormData(f);
      try { await api().post('/responsaveis/me/filhos', { matricula: d.get('matricula').trim(), email: d.get('email').trim() });
        window.showToast?.('Aluno vinculado!', 'success'); await recarregar(); }
      catch (err) { window.showToast?.(err.message, 'error'); }
    };
  }

  const semFilhos = (app, recarregar) => { app.innerHTML = empty('Você ainda não vinculou nenhum filho.') + '<div style="margin-top:18px">' + formVincular() + '</div>'; ligarVinculo(app, recarregar); };

  // Seletor de filho + período reutilizado em várias telas
  async function comFilho(app, desenhar, { periodo = true, extra = '' } = {}) {
    const painel = (await api().get('/progresso/responsavel')).dados;
    app.dataset.loading = '';
    if (!painel.filhos.length) return semFilhos(app, () => comFilho(app, desenhar, { periodo, extra }));
    app.innerHTML = `<div class="ui-row" style="margin-bottom:16px"><select class="input" id="sFilho" style="max-width:260px">${painel.filhos.map(f => `<option value="${f.aluno.id}">${esc(f.aluno.nome)}</option>`).join('')}</select>
      ${periodo ? '<select class="input" id="sDias" style="max-width:200px"><option value="7">Últimos 7 dias</option><option value="30" selected>Últimos 30 dias</option><option value="90">Últimos 3 meses</option><option value="180">Últimos 6 meses</option></select>' : ''}${extra}</div><div id="corpo"></div>`;
    const atualizar = async () => {
      const id = app.querySelector('#sFilho').value, dias = periodo ? app.querySelector('#sDias').value : 30;
      const rel = (await api().get(`/progresso/aluno/${id}?dias=${dias}`)).dados;
      await desenhar(app.querySelector('#corpo'), rel, { id, dias });
    };
    const seguro = () => atualizar().catch(e => window.showToast?.(e.message, 'error'));
    app.querySelector('#sFilho').onchange = seguro; app.querySelector('#sDias')?.addEventListener('change', seguro);
    await atualizar();
  }

  // ── Dashboard ─────────────────────────────────────────────────────────────
  page('dashboard-responsavel', async app => {
    const carregar = async () => {
      const d = (await api().get('/progresso/responsavel')).dados;
      const fb = await api().get('/feedbacks/');
      app.dataset.loading = '';
      if (!d.filhos.length) return semFilhos(app, carregar);
      const alertas = d.filhos.filter(f => f.status === 'Precisa de atenção' || f.atividades.atrasadas > 0).length;
      app.innerHTML = stats([['Filhos vinculados', d.totalFilhos, 'blue'], ['Progresso médio', d.progressoMedio + '%', 'green'], ['Feedbacks dos professores', fb.dados.length, 'purple'], ['Alertas', alertas, alertas ? 'red' : '']])
        + d.filhos.map(f => `<div class="card card-pad" style="margin-bottom:16px"><div class="ui-row"><h3>${esc(f.aluno.nome)}</h3>${pill(f.status, statusTone(f.status))}</div>
          <p class="muted small">Progresso geral</p>${bar(f.progresso)}<div class="ui-stats" style="margin-top:14px">
          <div class="ui-stat"><strong>${f.atividades.enviadas}</strong><small>Atividades concluídas</small></div><div class="ui-stat"><strong>${f.atividades.pendentes}</strong><small>Pendentes</small></div>
          <div class="ui-stat ${f.atividades.atrasadas ? 'tone-red' : ''}"><strong>${f.atividades.atrasadas}</strong><small>Em atraso</small></div><div class="ui-stat"><strong>${fmtMin(f.tempoEstudoMinutos)}</strong><small>Estudo (30 dias)</small></div></div>
          ${f.materiasDificeis.length ? `<p><strong>Atenção:</strong> ${f.materiasDificeis.map(esc).join(', ')}</p>` : ''}
          ${f.proximasAtividades.length ? `<p class="muted small" style="margin-top:8px">Próxima atividade: <strong>${esc(f.proximasAtividades[0].titulo)}</strong> (${fmtDate(f.proximasAtividades[0].prazo)})</p>` : ''}
          <div class="ui-actions"><a class="btn btn-light" href="acompanhamento.html">Acompanhar</a><a class="btn btn-light" href="desempenho.html">Desempenho</a><a class="btn btn-light" href="relatorios-responsavel.html">Relatórios</a></div></div>`).join('');
    };
    await carregar();
  });

  // ── Acompanhamento ────────────────────────────────────────────────────────
  page('acompanhamento', app => comFilho(app, (corpo, rel) => { corpo.innerHTML = UI.relatorioCompleto(rel); }));

  // ── Desempenho (notas) ────────────────────────────────────────────────────
  page('desempenho', app => comFilho(app, (corpo, rel) => {
    const fortes = rel.materias.filter(m => m.mediaNota != null && m.mediaNota >= 8).map(m => m.materia);
    corpo.innerHTML = stats([['Progresso geral', rel.progresso + '%', 'blue'], ['Média atual', fmtNota(rel.mediaNota), 'green'], ['Atividades concluídas', rel.atividades.enviadas, ''], ['Tempo de estudo', fmtMin(rel.tempoEstudoMinutos), 'purple']])
      + section('Notas por disciplina', UI.materiasHtml(rel)) + section('Evolução', UI.evolucao(rel))
      + `<div class="grid grid-2" style="margin-top:22px"><div class="card card-pad"><h3>Pontos fortes</h3><p class="muted">${fortes.length ? fortes.map(esc).join(', ') : 'Ainda sem notas altas registradas.'}</p></div>
         <div class="card card-pad"><h3>Pontos de atenção</h3><p class="muted">${rel.materiasDificeis.length ? rel.materiasDificeis.map(esc).join(', ') : 'Nenhum ponto de atenção.'}</p></div></div>`;
  }));

  // ── Progresso (tempo de estudo) ───────────────────────────────────────────
  page('progresso-responsavel', app => comFilho(app, (corpo, rel) => {
    const modos = Object.entries(rel.tempoPorModo).map(([m, min]) => ({ label: { leitura: 'Leitura', foco: 'Foco', revisao: 'Revisão', audio: 'Áudio' }[m] || m, value: min }));
    corpo.innerHTML = stats([['Tempo total', fmtMin(rel.tempoEstudoMinutos), 'purple'], ['Sessões de estudo', rel.sessoes, 'blue'], ['Atividades enviadas', `${rel.atividades.enviadas}/${rel.atividades.total}`, 'green']])
      + section('Tempo de estudo por semana (minutos)', `<div class="card card-pad">${UI.bars(rel.evolucao.map(e => ({ label: e.semana.slice(8, 10) + '/' + e.semana.slice(5, 7), value: e.minutosEstudo })))}</div>`)
      + section('Como o aluno estuda (minutos por modo)', modos.length ? `<div class="card card-pad">${UI.bars(modos)}</div>` : empty('Nenhuma sessão de estudo registrada no período.'))
      + section('Atividades por disciplina', UI.materiasHtml(rel));
  }));

  // ── Relatórios (RF20) ─────────────────────────────────────────────────────
  page('relatorios-responsavel', app => comFilho(app, async (corpo, rel, ctx) => {
    const salvos = (await api().get(`/relatorios/aluno/${ctx.id}`)).dados;
    corpo.innerHTML = `<div class="ui-actions" style="margin:0 0 16px"><button class="btn btn-primary" id="rSalvar" type="button">Gerar e salvar relatório</button><button class="btn btn-light" id="rPrint" type="button">Imprimir / PDF</button></div>
      <div id="rBox" class="card card-pad">${UI.relatorioCompleto(rel)}</div>
      ${section('Relatórios salvos', salvos.length ? `<div class="ui-list">${salvos.map(r => `<div class="card card-pad ui-row"><span><strong>${esc(r.periodo)}</strong> <span class="muted small">gerado em ${fmtDate(r.geradoEm)}</span></span><span>${r.desempenho != null ? pill('Desempenho ' + Math.round(r.desempenho) + '%', UI.toneOf(r.desempenho)) : ''} <button class="btn btn-light" data-abrir="${r.id}" type="button">Abrir</button></span></div>`).join('')}</div>` : empty('Nenhum relatório salvo ainda.'))}`;
    corpo.querySelector('#rSalvar').onclick = async () => { try { await api().post(`/relatorios/aluno/${ctx.id}`, { dias: Number(ctx.dias) }); window.showToast?.('Relatório salvo.', 'success'); await seguirAtualizando(); } catch (e) { window.showToast?.(e.message, 'error'); } };
    corpo.querySelector('#rPrint').onclick = () => UI.imprimir?.(corpo.querySelector('#rBox').innerHTML, 'Relatório de evolução') || window.print();
    corpo.querySelectorAll('[data-abrir]').forEach(b => b.onclick = async () => {
      const r = (await api().get(`/relatorios/${b.dataset.abrir}`)).dados;
      const m = modal(r.periodo, UI.relatorioCompleto(r.relatorio, { ia: false })); m.querySelector('.modal').style.maxWidth = '860px'; m.querySelector('.modal').style.maxHeight = '88vh'; m.querySelector('.modal').style.overflowY = 'auto';
    });
    async function seguirAtualizando() { app.querySelector('#sFilho').dispatchEvent(new Event('change')); }
  }));

  // ── Comunicados = feedbacks dos professores ───────────────────────────────
  page('comunicados', async app => {
    const [painel, fb] = await Promise.all([api().get('/progresso/responsavel'), api().get('/feedbacks/')]);
    app.dataset.loading = '';
    const nomes = Object.fromEntries(painel.dados.filhos.map(f => [f.aluno.id, f.aluno.nome]));
    const tom = { Incentivo: 'good', Correcao: 'warn', Orientacao: '' };
    app.innerHTML = `<p class="muted" style="margin-bottom:14px">Mensagens que os professores enviaram sobre as atividades dos seus filhos.</p>` + (fb.dados.length ? `<div class="ui-list">${fb.dados.map(f => `<div class="card card-pad"><div class="ui-row"><strong>${esc(f.professor)}</strong><span class="muted small">${fmtDate(f.data)}</span></div>
      <p class="muted small">${esc(nomes[f.aluno_id] || 'Aluno')} · ${esc(f.atividadeTitulo)} ${pill(f.tipo === 'Correcao' ? 'Correção' : f.tipo === 'Orientacao' ? 'Orientação' : f.tipo, tom[f.tipo])}</p><p style="margin-top:8px">${esc(f.mensagem)}</p></div>`).join('')}</div>` : empty('Nenhum feedback recebido ainda.'));
  });

  // ── Configurações: filhos vinculados ─────────────────────────────────────
  page('configuracoes-responsavel', async app => {
    const carregar = async () => {
      const d = (await api().get('/progresso/responsavel')).dados;
      app.dataset.loading = '';
      app.innerHTML = `<div class="card card-pad" style="max-width:720px"><h3>Dados do responsável</h3><p>${esc(d.responsavel.nome)} · ${esc(d.responsavel.email)}</p></div>
        <div class="card card-pad" style="max-width:720px;margin-top:18px"><h3>Filhos vinculados</h3>${d.filhos.length ? `<div class="ui-list" style="margin-top:10px">${d.filhos.map(f => `<div class="ui-row"><span><strong>${esc(f.aluno.nome)}</strong> <span class="muted small">mat. ${esc(f.aluno.matricula)}</span></span><button class="btn btn-light" data-rem="${f.aluno.id}" type="button">Desvincular</button></div>`).join('')}</div>` : '<p class="muted">Nenhum filho vinculado.</p>'}</div>
        <div style="margin-top:18px">${formVincular()}</div>`;
      app.querySelectorAll('[data-rem]').forEach(b => b.onclick = async () => { try { await api().delete(`/responsaveis/me/filhos/${b.dataset.rem}`); window.showToast?.('Vínculo removido.', 'success'); await carregar(); } catch (e) { window.showToast?.(e.message, 'error'); } });
      ligarVinculo(app, carregar);
    };
    await carregar();
  });
})();
