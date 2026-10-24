/* Telas do professor: dashboard, alunos, relatórios, materiais, enviar conteúdo (RF06, RF17, RF20). */
(function () {
  const { esc, fmtDate, fmtMin, fmtNota, pill, statusTone, stats, section, bar, empty, bars, page, api, modal } = UI;

  const linhaAluno = a => `
    <tr><td><strong>${esc(a.nome)}</strong><br><span class="muted small">${esc(a.turmas.join(', '))}</span></td>
      <td style="min-width:120px">${a.progresso}%${bar(a.progresso)}</td>
      <td>${a.desempenho == null ? '—' : a.desempenho + '%'}</td>
      <td>${a.atrasadas || '—'}</td>
      <td>${pill(a.status, statusTone(a.status))}</td>
      <td><button class="btn btn-light" data-detalhes="${a.id}" type="button">Detalhes</button></td></tr>`;

  async function abrirDetalhes(id, dias = 30) {
    const rel = (await api().get(`/progresso/aluno/${id}?dias=${dias}`)).dados;
    const m = modal(rel.aluno.nome, `<div id="relBox">${UI.relatorioCompleto(rel)}</div>`,
      '<button class="btn btn-light" id="gerarRel" type="button">Salvar relatório</button><button class="btn btn-light" id="imprimirRel" type="button">Imprimir / PDF</button><button class="btn btn-light modal-close" type="button">Fechar</button>');
    m.querySelector('.modal').style.maxWidth = '860px';
    m.querySelector('.modal').style.maxHeight = '88vh';
    m.querySelector('.modal').style.overflowY = 'auto';
    m.querySelector('#gerarRel').onclick = async () => {
      try { await api().post(`/relatorios/aluno/${id}`, { dias }); window.showToast?.('Relatório salvo no histórico do aluno.', 'success'); }
      catch (e) { window.showToast?.(e.message, 'error'); }
    };
    m.querySelector('#imprimirRel').onclick = () => imprimir(m.querySelector('#relBox').innerHTML, rel.aluno.nome);
  }

  function imprimir(html, titulo) {
    const w = window.open('', '_blank');
    if (!w) { window.showToast?.('Permita pop-ups para imprimir.', 'error'); return; }
    w.document.write(`<!doctype html><meta charset="utf-8"><title>${esc(titulo)}</title><link rel="stylesheet" href="${location.origin}${location.pathname.replace(/[^/]*$/, '')}css/variables.css"><link rel="stylesheet" href="${location.origin}${location.pathname.replace(/[^/]*$/, '')}css/app.css"><body style="font-family:sans-serif;padding:24px;background:#fff;color:#111">${html}`);
    w.document.close(); w.focus(); setTimeout(() => w.print(), 400);
  }
  UI.imprimir = imprimir;

  function ligarDetalhes(host, dias) {
    host.querySelectorAll('[data-detalhes]').forEach(b => b.onclick = () => abrirDetalhes(b.dataset.detalhes, dias?.() || 30).catch(e => window.showToast?.(e.message, 'error')));
  }

  // ── Dashboard (RF17) ──────────────────────────────────────────────────────
  page('dashboard-professor', async app => {
    const [d, conteudos] = await Promise.all([api().get('/progresso/professor'), api().get('/conteudos/')]);
    const dados = d.dados;
    app.dataset.loading = '';
    const mediaTurma = nome => { const l = dados.alunos.filter(a => a.turmas.includes(nome)); return l.length ? Math.round(l.reduce((s, a) => s + a.progresso, 0) / l.length) : 0; };
    app.innerHTML = stats([
      ['Total de alunos', dados.totalAlunos, 'blue'], ['Progresso médio', dados.progressoMedio + '%', 'green'],
      ['Conteúdos publicados', conteudos.dados.length, 'purple'], ['Precisam de apoio', dados.alunosEmAtencao.length, dados.alunosEmAtencao.length ? 'red' : '']])
      + section('Visão geral das turmas', dados.turmas.length ? `<div class="grid grid-2">${dados.turmas.map(t => `<div class="card card-pad"><strong>${esc(t.nome)}</strong><p class="muted small">${t.totalAlunos} aluno(s) · progresso médio ${mediaTurma(t.nome)}%</p>${bar(mediaTurma(t.nome))}</div>`).join('')}</div>`
        : empty('Você ainda não tem turmas. Crie uma em “Turmas”.'))
      + section('Alunos que precisam de apoio', dados.alunosEmAtencao.length ? `<div class="card card-pad ui-table-wrap"><table class="ui-table"><thead><tr><th>Aluno</th><th>Progresso</th><th>Desempenho</th><th>Atrasos</th><th>Status</th><th></th></tr></thead><tbody>${dados.alunosEmAtencao.map(linhaAluno).join('')}</tbody></table></div>` : empty('Nenhum aluno precisa de apoio agora. 🎉'))
      + section('Acompanhamento individual', dados.alunos.length ? `<div class="card card-pad ui-table-wrap"><table class="ui-table"><thead><tr><th>Aluno</th><th>Progresso</th><th>Desempenho</th><th>Atrasos</th><th>Status</th><th></th></tr></thead><tbody>${dados.alunos.map(linhaAluno).join('')}</tbody></table></div>` : empty('Adicione alunos às turmas para acompanhá-los.'));
    ligarDetalhes(app);
  });

  // ── Alunos ────────────────────────────────────────────────────────────────
  page('alunos', async app => {
    const dados = (await api().get('/progresso/professor')).dados;
    app.dataset.loading = '';
    const turmas = ['Todas as turmas', ...dados.turmas.map(t => t.nome)];
    app.innerHTML = `<div class="ui-row" style="margin-bottom:16px"><select class="input" id="fTurma" style="max-width:240px">${turmas.map(t => `<option>${esc(t)}</option>`).join('')}</select>
      <input class="input" id="fBusca" placeholder="Buscar por nome ou matrícula" style="max-width:300px"></div><div id="listaAlunos"></div>`;
    const desenhar = () => {
      const t = app.querySelector('#fTurma').value, q = app.querySelector('#fBusca').value.trim().toLowerCase();
      const lista = dados.alunos.filter(a => (t === turmas[0] || a.turmas.includes(t)) && (!q || a.nome.toLowerCase().includes(q) || a.matricula.toLowerCase().includes(q)));
      app.querySelector('#listaAlunos').innerHTML = lista.length ? `<div class="card card-pad ui-table-wrap"><table class="ui-table"><thead><tr><th>Aluno</th><th>Progresso</th><th>Desempenho</th><th>Atrasos</th><th>Status</th><th></th></tr></thead><tbody>${lista.map(linhaAluno).join('')}</tbody></table></div>` : empty('Nenhum aluno encontrado.');
      ligarDetalhes(app);
    };
    app.querySelector('#fTurma').onchange = desenhar; app.querySelector('#fBusca').oninput = desenhar; desenhar();
  });

  // ── Relatórios (RF20) ─────────────────────────────────────────────────────
  page('relatorios-professor', async app => {
    app.dataset.loading = '';
    app.innerHTML = `<div class="ui-row" style="margin-bottom:16px"><select class="input" id="fDias" style="max-width:220px"><option value="7">Últimos 7 dias</option><option value="30" selected>Últimos 30 dias</option><option value="180">Últimos 6 meses</option></select>
      <button class="btn btn-light" id="btnImprimir" type="button">Imprimir / salvar PDF</button></div><div id="relBody"></div>`;
    const carregar = async () => {
      const dias = Number(app.querySelector('#fDias').value);
      const d = (await api().get(`/progresso/professor?dias=${dias}`)).dados;
      const notas = d.porMateria.filter(m => m.mediaNota != null);
      app.querySelector('#relBody').innerHTML = stats([
        ['Progresso médio', d.progressoMedio + '%', 'green'], ['Atividades enviadas', d.atividadesEnviadas, 'blue'],
        ['Tempo médio de estudo', fmtMin(d.tempoMedioEstudoMinutos), 'purple'], ['Alertas pedagógicos', d.alunosEmAtencao.length, d.alunosEmAtencao.length ? 'red' : '']])
        + section('Desempenho por disciplina', d.porMateria.length ? `<div class="ui-list">${d.porMateria.map(m => { const pct = m.atividades ? m.enviadas / m.atividades * 100 : 0; return `<div class="card card-pad"><div class="ui-row"><strong>${esc(m.materia)}</strong><span class="muted small">${m.enviadas}/${m.atividades} entregas · nota média ${fmtNota(m.mediaNota)}</span></div>${bar(pct)}</div>`; }).join('')}</div>` : empty('Sem atividades no período.'))
        + section('Alunos', d.alunos.length ? `<div class="card card-pad ui-table-wrap"><table class="ui-table"><thead><tr><th>Aluno</th><th>Progresso</th><th>Desempenho</th><th>Atrasos</th><th>Status</th><th></th></tr></thead><tbody>${d.alunos.map(linhaAluno).join('')}</tbody></table></div>` : empty('Sem alunos.'))
        + (d.alunosEmAtencao.length ? section('Alertas', `<div class="card card-pad"><ul style="padding-left:18px;display:grid;gap:6px">${d.alunosEmAtencao.map(a => `<li><strong>${esc(a.nome)}</strong>: ${a.atrasadas ? `${a.atrasadas} atividade(s) em atraso. ` : ''}${a.materiasDificeis.length ? `Dificuldade em ${a.materiasDificeis.map(esc).join(', ')}.` : ''}</li>`).join('')}</ul></div>`) : '');
      ligarDetalhes(app, () => dias);
    };
    app.querySelector('#fDias').onchange = () => carregar().catch(e => window.showToast?.(e.message, 'error'));
    app.querySelector('#btnImprimir').onclick = () => imprimir(app.querySelector('#relBody').innerHTML, 'Relatório da turma');
    await carregar();
  });

  // ── Materiais (RF06) ──────────────────────────────────────────────────────
  page('materiais', async app => {
    const carregar = async () => {
      const itens = (await api().get('/conteudos/')).dados;
      app.dataset.loading = '';
      app.innerHTML = `<div class="page-title-row"><div><h2>Materiais publicados</h2><p class="muted small">${itens.length} conteúdo(s)</p></div><a class="btn btn-primary" href="enviar-conteudo.html">+ Novo conteúdo</a></div>`
        + (itens.length ? `<div class="card card-pad ui-table-wrap"><table class="ui-table"><thead><tr><th>Título</th><th>Turma</th><th>Formato</th><th>Data</th><th></th></tr></thead><tbody>${itens.map(c => `<tr><td><strong>${esc(c.titulo)}</strong></td><td>${esc(c.turmaNome)}</td><td>${esc(c.tipo)}</td><td>${fmtDate(c.dataPostagem)}</td>
          <td style="white-space:nowrap"><button class="btn btn-light" data-ver="${c.id}" type="button">Ver</button> <button class="btn btn-light" data-del="${c.id}" type="button">Excluir</button></td></tr>`).join('')}</tbody></table></div>` : empty('Nenhum conteúdo publicado ainda.'));
      app.querySelectorAll('[data-ver]').forEach(b => b.onclick = async () => {
        const c = (await api().get(`/conteudos/${b.dataset.ver}`)).dados;
        const link = c.tipo === 'Link' && c.arquivo ? `<p><a href="${esc(c.arquivo)}" target="_blank" rel="noopener noreferrer">${esc(c.arquivo)}</a></p>` : '';
        modal(c.titulo, `${link}${c.texto ? `<div class="ad-box" style="max-height:50vh;overflow:auto"><p>${esc(c.texto).replace(/\n\n/g, '</p><p>')}</p></div>` : ''}`);
      });
      app.querySelectorAll('[data-del]').forEach(b => b.onclick = () => {
        const m = modal('Excluir conteúdo', '<p class="muted">Esta ação remove o conteúdo e suas adaptações.</p>', '<button class="btn btn-light modal-close" type="button">Cancelar</button><button class="btn btn-primary" id="okDel" type="button">Excluir</button>');
        m.querySelector('#okDel').onclick = async () => {
          try { await api().delete(`/conteudos/${b.dataset.del}`); UI.closeModals(); window.showToast?.('Conteúdo removido.', 'success'); await carregar(); }
          catch (e) { window.showToast?.(e.message, 'error'); }
        };
      });
    };
    await carregar();
  });

  // ── Enviar conteúdo (RF06) ────────────────────────────────────────────────
  page('enviar-conteudo', async app => {
    const turmas = (await api().get('/turmas/')).dados;
    app.dataset.loading = '';
    if (!turmas.length) { app.innerHTML = empty('Crie uma turma antes de publicar conteúdo.') + '<p style="margin-top:14px"><a class="btn btn-primary" href="turmas.html">Ir para Turmas</a></p>'; return; }
    app.innerHTML = `<form class="card form-card" id="conteudoForm" style="max-width:780px">
      <div class="ui-field"><label for="cTitulo">Título do conteúdo</label><input class="input" id="cTitulo" name="titulo" required maxlength="120"></div>
      <div class="ui-field"><label for="cTurma">Turma</label><select class="input" id="cTurma" name="turma_id">${turmas.map(t => `<option value="${t.id}">${esc(t.nome)}</option>`).join('')}</select></div>
      <div class="ui-field"><label>Formato</label><div class="ui-tabs" id="cTipo">${['Texto', 'PDF', 'Link'].map((t, i) => `<button type="button" data-tipo="${t}" class="${i ? '' : 'active'}">${t}</button>`).join('')}</div></div>
      <div class="ui-field" data-for="Texto"><label for="cTexto">Texto do conteúdo</label><textarea class="input" id="cTexto" name="texto" rows="9" placeholder="Cole ou digite o conteúdo da aula"></textarea></div>
      <div class="ui-field" data-for="PDF" hidden><label for="cPdf">Arquivo PDF (até 10 MB)</label><input class="input" id="cPdf" name="arquivo" type="file" accept="application/pdf"><small class="muted">O texto do PDF é extraído automaticamente para gerar as adaptações. PDFs escaneados como imagem não funcionam.</small></div>
      <div class="ui-field" data-for="Link" hidden><label for="cLink">Endereço do link</label><input class="input" id="cLink" name="arquivo" type="url" placeholder="https://..."></div>
      <p class="muted small">Ao publicar, cada aluno recebe o conteúdo adaptado ao seu perfil (resumo, TDAH, TEA, mapa mental, áudio, flashcards).</p>
      <button class="btn btn-primary" type="submit" style="margin-top:12px">Publicar conteúdo</button></form>`;
    let tipo = 'Texto';
    const alternar = () => app.querySelectorAll('[data-for]').forEach(el => { const on = el.dataset.for === tipo; el.hidden = !on; el.querySelectorAll('input,textarea').forEach(i => { i.disabled = !on; }); });
    app.querySelector('#cTipo').onclick = e => { const b = e.target.closest('[data-tipo]'); if (!b) return; tipo = b.dataset.tipo; app.querySelectorAll('#cTipo button').forEach(x => x.classList.toggle('active', x === b)); alternar(); };
    alternar();
    app.querySelector('#conteudoForm').onsubmit = async e => {
      e.preventDefault();
      const btn = e.target.querySelector('button[type=submit]'); btn.disabled = true;
      const f = new FormData(e.target); f.set('tipo', tipo);
      try {
        if (tipo === 'PDF') await api().upload('/conteudos/', f);
        else await api().post('/conteudos/', Object.fromEntries([...f.entries()].filter(([k]) => tipo === 'Link' || k !== 'arquivo')));
        window.showToast?.('Conteúdo publicado!', 'success');
        setTimeout(() => { location.href = 'materiais.html'; }, 700);
      } catch (err) { window.showToast?.(err.message, 'error'); btn.disabled = false; }
    };
  });
})();
