(function () {
  document.addEventListener('DOMContentLoaded', () => {
    initSelectableCards();
    initStudentCourses();
    initSearch();
    initGenericForms();
    initReferenceInteractions();
    initAdaptation();
    initApiPages();
  });

  function initSelectableCards() {
    document.querySelectorAll('.select-card').forEach((card) => {
      card.addEventListener('click', () => {
        const input = card.querySelector('input');
        if (input?.type === 'checkbox') input.checked = !input.checked;
        else if (input) input.checked = true;
        card.classList.toggle('selected', Boolean(input?.checked));
      });
    });

    document.querySelectorAll('[data-save-preferences]').forEach((button) => {
      button.addEventListener('click', () => window.showToast?.('Preferências salvas com sucesso!', 'success'));
    });
  }

  function initStudentCourses() {
    const subjectTabs = document.querySelector('#subjectTabs');
    if (subjectTabs) {
      subjectTabs.addEventListener('click', (event) => {
        const button = event.target.closest('[data-subject]');
        if (!button) return;
        subjectTabs.querySelectorAll('button').forEach((item) => item.classList.remove('active'));
        button.classList.add('active');
        renderCourses(button.dataset.subject);
      });
    }

    if (document.querySelector('#courseList')) renderCourses('Matemática');
  }

  function renderCourses(subject) {
    const host = document.querySelector('#courseList');
    if (!host || !window.AdaptEducaData) return;

    const courses = (AdaptEducaData.courses || []).filter((course) => course.subject === subject);
    host.innerHTML = courses.map((course) => {
      const statusClass = course.progress === 100 ? 'success' : course.progress ? 'progress' : 'neutral';
      const statusIcon = course.progress === 100 ? '✓' : course.progress ? '◷' : '';
      return `
        <article class="card course-card">
          <button class="course-card-button" type="button" data-course-title="${escapeHtml(course.title)}" data-course-subject="${escapeHtml(course.subject)}">
            <span class="course-head">
              <span>
                <span class="course-title"><h3>${escapeHtml(course.title)}</h3></span>
                <span class="course-tags">${course.tags.map((tag) => `<span class="course-tag">${escapeHtml(tag)}</span>`).join('')}</span>
              </span>
              <span class="course-status ${statusClass}">${statusIcon} ${escapeHtml(course.status)}</span>
            </span>
            <span class="progress course-progress"><span style="width:${course.progress}%"></span></span>
          </button>
        </article>`;
    }).join('') || `
      <div class="card empty-state">
        <div class="icon-box">▤</div>
        <h3>Nenhum conteúdo nesta disciplina</h3>
        <p class="muted small">Novos materiais aparecerão aqui.</p>
      </div>`;

    host.querySelectorAll('[data-course-title]').forEach((button) => {
      button.addEventListener('click', () => {
        const title = button.dataset.courseTitle;
        const subjectName = button.dataset.courseSubject;
        const actions = `<button class="btn btn-light modal-close" type="button">Fechar</button><a class="btn btn-primary" href="adaptacao-conteudo.html">Adaptar com IA</a>`;
        window.openModal?.(title, `<p class="muted">Conteúdo de <strong>${escapeHtml(subjectName)}</strong>. Escolha um dos formatos disponíveis ou abra a adaptação por IA.</p>`, actions);
      });
    });
  }

  function initSearch() {
    document.querySelectorAll('[data-filter-list]').forEach((input) => {
      input.addEventListener('input', () => {
        const selector = input.dataset.filterList;
        const query = input.value.trim().toLowerCase();
        document.querySelectorAll(selector).forEach((item) => {
          item.hidden = !item.textContent.toLowerCase().includes(query);
        });
      });
    });
  }

  function initGenericForms() {
    document.querySelectorAll('[data-demo-form]').forEach((form) => {
      form.addEventListener('submit', (event) => {
        event.preventDefault();
        window.showToast?.(form.dataset.success || 'Informações salvas com sucesso!', 'success');
        form.reset();
      });
    });

    document.querySelectorAll('[data-delete-item]').forEach((button) => {
      button.addEventListener('click', () => {
        window.openModal?.('Confirmar exclusão', '<p class="muted">Esta ação é apenas uma simulação. Deseja remover o item?</p>', '<button class="btn btn-light modal-close">Cancelar</button><button class="btn btn-primary" onclick="this.closest(\'.modal-backdrop\').remove();showToast(\'Item removido.\',\'success\')">Remover</button>');
      });
    });
  }

  function initReferenceInteractions() {
    document.querySelectorAll('[data-info-title]').forEach((button) => {
      button.addEventListener('click', () => {
        window.openModal?.(escapeHtml(button.dataset.infoTitle), `<p class="muted">${escapeHtml(button.dataset.infoText || '')}</p>`);
      });
    });

    document.querySelectorAll('[data-navigate]').forEach((button) => {
      button.addEventListener('click', () => {
        window.location.href = button.dataset.navigate;
      });
    });

    document.querySelectorAll('[data-subject-filter]').forEach((button) => {
      button.addEventListener('click', () => {
        const subject = button.dataset.subjectFilter;
        window.openModal?.(`Conteúdos de ${escapeHtml(subject)}`, `<p class="muted">Abrindo a listagem simulada de conteúdos de ${escapeHtml(subject)}.</p>`, '<button class="btn btn-light modal-close">Fechar</button><a class="btn btn-primary" href="materiais.html">Ver materiais</a>');
      });
    });

    document.querySelectorAll('[data-help]').forEach((button) => {
      button.addEventListener('click', () => {
        window.openModal?.('Central de Ajuda', '<p class="muted">Escolha um formato de adaptação, cole seu conteúdo no campo inferior e pressione o botão de envio.</p>');
      });
    });
  }

  function initAdaptation() {
    const types = document.querySelectorAll('.adapt-type');
    if (!types.length) return;

    types.forEach((type) => {
      type.addEventListener('click', () => {
        types.forEach((item) => item.classList.remove('active'));
        type.classList.add('active');
        const mode = document.querySelector('#adaptMode');
        const description = document.querySelector('#adaptDescription');
        if (mode) mode.textContent = type.dataset.mode;
        if (description) description.textContent = type.dataset.description;
      });
    });

    const textArea = document.querySelector('#adaptText');
    const sendButton = document.querySelector('#adaptSend');
    const sendContent = () => {
      const text = textArea?.value.trim() || '';
      if (!text) {
        window.showToast?.('Cole ou digite um conteúdo para adaptar.', 'error');
        textArea?.focus();
        return;
      }
      const mode = document.querySelector('.adapt-type.active')?.dataset.mode || 'Resumo';
      const empty = document.querySelector('#adaptEmpty');
      const output = document.querySelector('#generatedOutput');
      if (empty) empty.style.display = 'none';
      output?.classList.add('show');
      const outputTitle = document.querySelector('#outputTitle');
      if (outputTitle) outputTitle.textContent = `${mode} gerado pela IA`;
      renderOutput(mode, text);
    };

    sendButton?.addEventListener('click', sendContent);
    textArea?.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendContent();
      }
    });

    document.querySelectorAll('[data-output-tab]').forEach((button) => {
      button.addEventListener('click', () => {
        document.querySelectorAll('[data-output-tab]').forEach((item) => item.classList.remove('active'));
        button.classList.add('active');
        renderOutput(button.dataset.outputTab, textArea?.value || '');
      });
    });

    const chat = document.querySelector('#chatDrawer');
    document.querySelectorAll('[data-open-chat]').forEach((button) => button.addEventListener('click', () => chat?.classList.add('open')));
    document.querySelector('[data-close-chat]')?.addEventListener('click', () => chat?.classList.remove('open'));

    const historicoChat = [];
    document.querySelector('#chatForm')?.addEventListener('submit', async (event) => {
      event.preventDefault();
      const input = event.target.elements.message;
      const question = input.value.trim();
      if (!question) return;
      const messages = document.querySelector('#chatMessages');
      const bolha = (texto, classe = '') => {
        const el = document.createElement('div');
        el.className = `chat-bubble ${classe}`.trim();
        el.style.whiteSpace = 'pre-wrap';
        el.textContent = texto;
        messages?.appendChild(el);
        if (messages) messages.scrollTop = messages.scrollHeight;
        return el;
      };
      input.value = '';
      bolha(question, 'user');
      historicoChat.push({ role: 'user', content: question });
      const espera = bolha('Pensando…');
      try {
        const resposta = await UI.tutorPerguntar({ texto: document.querySelector('#adaptText')?.value || '', historico: historicoChat });
        espera.textContent = resposta;
        historicoChat.push({ role: 'assistant', content: resposta });
      } catch (error) {
        historicoChat.pop();
        espera.textContent = error.message || 'O tutor de IA não está disponível agora.';
      }
      if (messages) messages.scrollTop = messages.scrollHeight;
    });
  }

  const MODO_API = { 'resumo': 'resumo', 'mapa mental': 'mapa', 'roteiro de áudio': 'audio', 'áudio': 'audio', 'adaptado tdah': 'tdah', 'adaptado tea': 'tea', 'simplificado': 'simplificado', 'texto simplificado': 'simplificado' };

  // RF07-RF10: a adaptação é gerada no servidor a partir do texto enviado.
  async function renderOutput(mode, text) {
    const pane = document.querySelector('#outputPane');
    if (!pane) return;
    const modo = MODO_API[mode.toLowerCase()] || 'resumo';
    pane.innerHTML = '<p class="muted">Gerando adaptação…</p>';
    try {
      const resposta = await AdaptEducaAPI.post('/adaptar', { modo, texto: text });
      UI.renderAdaptacao(pane, modo, resposta.dados.resultado);
    } catch (error) {
      pane.innerHTML = `<p class="muted">${escapeHtml(error.message)}</p>`;
      window.showToast?.(error.message, 'error');
    }
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
  }

  async function initApiPages() {
    if (!window.AdaptEducaAPI) return;
    const page = document.body?.dataset.page;

    try {
      if (page === 'turmas') { initTurmaActions(); await renderTurmasFromApi(); }
      if (page === 'atividades-professor') { initAtividadeProfessorActions(); await renderAtividadesFromApi(); }
      if (page === 'atividades-aluno') await renderAtividadesAluno();
    } catch (error) {
      console.error(error);
      window.showToast?.(`Não foi possível carregar a API: ${error.message}`, 'error');
    }
  }

  // ── Turmas (RF05) ────────────────────────────────────────────────────────
  async function renderTurmasFromApi() {
    const host = document.querySelector('.class-overview');
    if (!host) return;
    const result = await AdaptEducaAPI.get('/turmas/');
    const turmas = result.dados || [];
    const total = turmas.reduce((sum, t) => sum + (t.totalAlunos || 0), 0);
    const subtitle = document.querySelector('#turmasResumo');
    if (subtitle) subtitle.textContent = `${turmas.length} turma(s) · ${total} aluno(s)`;

    host.innerHTML = turmas.map(turma => `
      <article class="class-card card">
        <h3>${escapeHtml(turma.nome)}</h3>
        <p class="muted small">Código: ${escapeHtml(turma.codigo)}</p>
        <div class="class-metrics">
          <span>Alunos</span><strong>${Number(turma.totalAlunos || 0)}</strong>
          <span>Descrição</span><strong>${escapeHtml(turma.descricao || '—')}</strong>
        </div>
        <button class="btn btn-light btn-block" data-open-turma="${turma.id}" style="margin-top:12px">Gerenciar turma</button>
      </article>`).join('') || '<div class="card card-pad">Você ainda não tem turmas. Clique em “+ Nova Turma”.</div>';

    host.querySelectorAll('[data-open-turma]').forEach(btn =>
      btn.addEventListener('click', () => openTurmaModal(turmas.find(t => t.id === Number(btn.dataset.openTurma)))));
  }

  function initTurmaActions() {
    document.querySelector('#newTurmaBtn')?.addEventListener('click', () => {
      window.openModal?.('Criar nova turma', `
        <form id="turmaForm" class="auth-form">
          <div class="input-group"><label>Nome</label><input class="input" name="nome" placeholder="Ex.: 9º Ano A" required maxlength="80"></div>
          <div class="input-group"><label>Código</label><input class="input" name="codigo" placeholder="Ex.: 9A-2026" required maxlength="20"></div>
          <div class="input-group"><label>Descrição</label><input class="input" name="descricao" placeholder="Opcional"></div>
          <button class="btn btn-primary btn-block" type="submit">Criar turma</button>
        </form>`);
      document.querySelector('#turmaForm').addEventListener('submit', async event => {
        event.preventDefault();
        const form = new FormData(event.target);
        try {
          await AdaptEducaAPI.post('/turmas/', {
            nome: form.get('nome').trim(), codigo: form.get('codigo').trim(), descricao: form.get('descricao').trim() || null
          });
          document.querySelector('.modal-backdrop')?.remove();
          window.showToast?.('Turma criada!', 'success');
          await renderTurmasFromApi();
        } catch (error) { window.showToast?.(error.message, 'error'); }
      });
    });
  }

  async function openTurmaModal(turma) {
    if (!turma) return;
    const draw = async () => {
      const alunos = (await AdaptEducaAPI.get(`/turmas/${turma.id}/alunos`)).dados || [];
      const list = alunos.map(a => `
        <li style="display:flex;justify-content:space-between;gap:10px;align-items:center;padding:6px 0">
          <span><strong>${escapeHtml(a.nome)}</strong> <span class="muted small">${escapeHtml(a.email)} · mat. ${escapeHtml(a.matricula)}</span></span>
          <button class="btn btn-light" type="button" data-remove-aluno="${a.id}">Remover</button>
        </li>`).join('') || '<li class="muted small">Nenhum aluno nesta turma ainda.</li>';
      document.querySelector('#turmaAlunos').innerHTML = list;
    };
    window.openModal?.(escapeHtml(turma.nome), `
      <p class="muted small">Código: ${escapeHtml(turma.codigo)}</p>
      <h4 style="margin:14px 0 6px">Alunos</h4>
      <ul id="turmaAlunos" style="display:grid;gap:2px"></ul>
      <form id="addAlunoForm" style="display:flex;gap:8px;margin-top:14px">
        <input class="input" name="identificador" placeholder="Matrícula ou e-mail do aluno" required style="flex:1">
        <button class="btn btn-primary" type="submit">Adicionar</button>
      </form>`, '<button class="btn btn-light modal-close" type="button">Fechar</button>');

    const modal = [...document.querySelectorAll('.modal-backdrop')].pop();
    const reload = async () => { try { await draw(); } catch (e) { window.showToast?.(e.message, 'error'); } };
    await reload();

    modal.querySelector('#addAlunoForm').addEventListener('submit', async event => {
      event.preventDefault();
      const valor = new FormData(event.target).get('identificador').trim();
      const corpo = valor.includes('@') ? { email: valor } : { matricula: valor };
      try {
        await AdaptEducaAPI.post(`/turmas/${turma.id}/alunos`, corpo);
        event.target.reset();
        window.showToast?.('Aluno adicionado à turma.', 'success');
        await reload();
        renderTurmasFromApi();
      } catch (error) { window.showToast?.(error.message, 'error'); }
    });
    modal.addEventListener('click', async event => {
      const btn = event.target.closest('[data-remove-aluno]');
      if (!btn) return;
      try {
        await AdaptEducaAPI.delete(`/turmas/${turma.id}/alunos/${btn.dataset.removeAluno}`);
        await reload();
        renderTurmasFromApi();
      } catch (error) { window.showToast?.(error.message, 'error'); }
    });
  }

  // ── Atividades do professor (RF12) ───────────────────────────────────────
  const formatDate = iso => iso ? iso.split('-').reverse().join('/') : 'sem prazo';

  async function renderAtividadesFromApi() {
    const grid = document.querySelector('#activitiesGrid');
    if (!grid) return;
    const atividades = (await AdaptEducaAPI.get('/atividades/')).dados || [];
    const resumo = document.querySelector('#atividadesResumo');
    if (resumo) resumo.textContent = `${atividades.length} atividade(s) publicada(s).`;

    grid.innerHTML = atividades.map(a => {
      const pct = a.totalAlunos ? Math.round(a.totalEnviadas / a.totalAlunos * 100) : 0;
      return `
      <article class="card card-pad">
        <span class="chip">${escapeHtml(a.turmaNome || 'Turma')}</span>
        <h3 style="margin:12px 0 5px">${escapeHtml(a.titulo)}</h3>
        <p class="muted small">${a.questoes.length} questão(ões) · ${a.etapas.length} etapa(s) · entrega em ${escapeHtml(formatDate(a.prazo))}</p>
        <div class="progress" style="margin:16px 0"><span style="width:${pct}%"></span></div>
        <p class="small"><strong>${a.totalEnviadas} de ${a.totalAlunos}</strong> alunos enviaram</p>
        <button class="btn btn-light" style="margin-top:14px" data-ver-respostas="${a.id}">Respostas e feedback</button>
      </article>`;
    }).join('') || '<div class="card card-pad">Nenhuma atividade criada ainda.</div>';

    grid.querySelectorAll('[data-ver-respostas]').forEach(btn =>
      btn.addEventListener('click', () => abrirRespostas(atividades.find(a => a.id === Number(btn.dataset.verRespostas)))));
  }

  // RF18: o professor lê as respostas, dá nota e envia feedback individual.
  async function abrirRespostas(atividade, abrirId) {
    try {
      const respostas = (await AdaptEducaAPI.get(`/atividades/${atividade.id}/respostas`)).dados || [];
      const rotulo = { Incentivo: 'Incentivo', Correcao: 'Correção', Orientacao: 'Orientação' };
      const corpo = respostas.map(r => `
        <details ${r.aluno_id === abrirId ? 'open' : ''} style="padding:8px 0;border-bottom:1px solid var(--border)"><summary><strong>${escapeHtml(r.aluno)}</strong> — ${escapeHtml(r.status)}${r.nota != null ? ` · nota ${String(r.nota).replace('.', ',')}` : ''}</summary>
          ${atividade.etapas.length ? `<p class="small muted" style="margin-top:8px">Etapas concluídas: ${r.etapasConcluidas.length}/${atividade.etapas.length}</p>` : ''}
          <ol style="margin:8px 0 0 18px">${atividade.questoes.map((q, i) => `<li><span class="muted small">${escapeHtml(q)}</span><br>${escapeHtml(r.respostas[i] || '—')}</li>`).join('')}</ol>
          ${r.feedbacks.map(f => `<p class="small" style="margin-top:8px"><span class="chip">${rotulo[f.tipo]}</span> ${escapeHtml(f.mensagem)}</p>`).join('')}
          <form data-feedback="${r.aluno_id}" style="display:grid;gap:8px;margin-top:10px">
            <div style="display:flex;gap:8px;flex-wrap:wrap"><select class="input" name="tipo" style="width:auto"><option value="Incentivo">Incentivo</option><option value="Correcao">Correção</option><option value="Orientacao" selected>Orientação</option></select>
            ${r.status === 'Enviada' ? '<input class="input" name="nota" type="number" min="0" max="10" step="0.1" placeholder="Nota (0 a 10)" style="width:150px">' : ''}</div>
            <textarea class="input" name="mensagem" rows="2" placeholder="Escreva um feedback para ${escapeHtml(r.aluno)}" required></textarea>
            <button class="btn btn-primary" type="submit" style="justify-self:start">Enviar feedback</button></form>
        </details>`).join('') || '<p class="muted">Nenhum aluno na turma.</p>';
      window.openModal?.(escapeHtml(atividade.titulo), `<div style="max-height:62vh;overflow:auto">${corpo}</div>`, '<button class="btn btn-light modal-close" type="button">Fechar</button>');
      const modal = [...document.querySelectorAll('.modal-backdrop')].pop();
      modal.querySelectorAll('[data-feedback]').forEach(form => form.addEventListener('submit', async event => {
        event.preventDefault();
        const f = new FormData(form);
        try {
          await AdaptEducaAPI.post('/feedbacks/', {
            atividade_id: atividade.id, aluno_id: Number(form.dataset.feedback), tipo: f.get('tipo'),
            mensagem: f.get('mensagem').trim(), nota: f.get('nota') || null
          });
          modal.remove();
          window.showToast?.('Feedback enviado!', 'success');
          abrirRespostas(atividade, Number(form.dataset.feedback));
        } catch (error) { window.showToast?.(error.message, 'error'); }
      }));
    } catch (error) { window.showToast?.(error.message, 'error'); }
  }

  function initAtividadeProfessorActions() {
    document.querySelector('#newAtividadeBtn')?.addEventListener('click', async () => {
      let turmas = [];
      try { turmas = (await AdaptEducaAPI.get('/turmas/')).dados || []; }
      catch (error) { window.showToast?.(error.message, 'error'); return; }
      if (!turmas.length) { window.showToast?.('Crie uma turma antes de criar atividades.', 'error'); return; }
      window.openModal?.('Nova atividade', `
        <form id="atividadeForm" class="auth-form" style="max-height:70vh;overflow:auto">
          <div class="input-group"><label>Turma</label><select class="input" name="turma_id" required>${turmas.map(t => `<option value="${t.id}">${escapeHtml(t.nome)}</option>`).join('')}</select></div>
          <div class="input-group"><label>Título</label><input class="input" name="titulo" required maxlength="120"></div>
          <div class="input-group"><label>Descrição</label><input class="input" name="descricao" placeholder="Orientações para o aluno"></div>
          <div class="input-group"><label>Prazo</label><input class="input" type="date" name="prazo"></div>
          <div class="input-group"><label>Etapas (opcional — uma por linha, “Título: instrução”)</label><textarea class="input" name="etapas" rows="3" placeholder="Leia o texto: leia com atenção&#10;Faça o resumo: em 5 linhas"></textarea></div>
          <div class="input-group"><label>Questões (uma por linha)</label><textarea class="input" name="questoes" rows="3" placeholder="Quanto é 2 + 2?"></textarea></div>
          <button class="btn btn-primary btn-block" type="submit">Publicar atividade</button>
        </form>`);
      document.querySelector('#atividadeForm').addEventListener('submit', async event => {
        event.preventDefault();
        const f = new FormData(event.target);
        if (!f.get('questoes').trim() && !f.get('etapas').trim()) { window.showToast?.('Informe ao menos uma questão ou etapa.', 'error'); return; }
        try {
          await AdaptEducaAPI.post('/atividades/', {
            turma_id: Number(f.get('turma_id')), titulo: f.get('titulo').trim(),
            descricao: f.get('descricao').trim() || null, prazo: f.get('prazo') || null,
            questoes: f.get('questoes'), etapas: f.get('etapas')
          });
          document.querySelector('.modal-backdrop')?.remove();
          window.showToast?.('Atividade publicada!', 'success');
          await renderAtividadesFromApi();
        } catch (error) { window.showToast?.(error.message, 'error'); }
      });
    });
  }

  // ── Atividades do aluno (RF15) ───────────────────────────────────────────
  let atividadesAluno = [];
  let filtroAluno = 'Pendente';

  async function renderAtividadesAluno() {
    const host = document.querySelector('#studentActivities');
    if (!host) return;
    atividadesAluno = (await AdaptEducaAPI.get('/atividades/')).dados || [];
    drawAtividadesAluno();
    if (host.dataset.ready) return;
    host.dataset.ready = '1';
    document.querySelectorAll('[data-atividade-filtro]').forEach(btn => btn.addEventListener('click', () => {
      document.querySelectorAll('[data-atividade-filtro]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      filtroAluno = btn.dataset.atividadeFiltro;
      drawAtividadesAluno();
    }));
  }

  function drawAtividadesAluno() {
    const host = document.querySelector('#studentActivities');
    const hoje = new Date().toISOString().slice(0, 10);
    const lista = atividadesAluno.filter(a => filtroAluno === 'Todas' || a.status === filtroAluno);
    host.innerHTML = lista.map(a => {
      const enviada = a.status === 'Concluida';
      const feitas = a.minhaResposta?.etapasConcluidas?.length || 0;
      const rascunho = a.minhaResposta && !enviada;
      const atrasada = !enviada && a.prazo && a.prazo < hoje;
      return `
      <article class="card card-pad">
        <div style="display:flex;justify-content:space-between;gap:12px">
          <div><span class="chip">${escapeHtml(a.turmaNome || '')}</span>
            <h3 style="margin-top:10px">${escapeHtml(a.titulo)}</h3>
            <p class="muted small">${a.questoes.length ? `${a.questoes.length} questão(ões) · ` : ''}${a.etapas.length ? `${feitas}/${a.etapas.length} etapa(s) · ` : ''}entrega em ${escapeHtml(formatDate(a.prazo))}</p></div>
          <span class="status ${enviada ? 'success' : 'progress'}">${enviada ? '✓ Enviada' : atrasada ? '! Atrasada' : rascunho ? '◷ Em andamento' : '◷ Pendente'}${a.nota != null ? ` · ${String(a.nota).replace('.', ',')}` : ''}</span>
        </div>
        ${a.etapas.length ? `<div class="progress" style="margin:14px 0 0"><span style="width:${Math.round(feitas / a.etapas.length * 100)}%"></span></div>` : ''}
        ${(a.feedbacks || []).slice(0, 1).map(f => `<p class="small" style="margin-top:12px"><strong>Feedback do professor:</strong> ${escapeHtml(f.mensagem)}</p>`).join('')}
        <button class="btn ${enviada ? 'btn-light' : 'btn-primary'}" style="margin-top:16px" data-abrir-atividade="${a.id}">
          ${enviada ? 'Ver minhas respostas' : rascunho ? 'Continuar atividade' : 'Começar atividade'}</button>
      </article>`;
    }).join('') || '<div class="card card-pad">Nenhuma atividade nesta aba.</div>';
    host.querySelectorAll('[data-abrir-atividade]').forEach(btn =>
      btn.addEventListener('click', () => openAtividadeAluno(atividadesAluno.find(a => a.id === Number(btn.dataset.abrirAtividade)))));
  }

  // RF11 + RF15: etapas com progresso salvo e questões respondidas na plataforma.
  function openAtividadeAluno(atividade) {
    const enviada = atividade.status === 'Concluida';
    const salvas = atividade.minhaResposta?.respostas || [];
    const feitas = new Set(atividade.minhaResposta?.etapasConcluidas || []);
    const etapas = atividade.etapas.map((e, i) => `
      <label class="choice checkbox" style="display:flex;gap:10px;align-items:flex-start;padding:10px 0">
        <input type="checkbox" data-etapa="${i}" ${feitas.has(i) ? 'checked' : ''} ${enviada ? 'disabled' : ''}>
        <span><strong>${i + 1}. ${escapeHtml(e.titulo)}</strong>${e.instrucao ? `<br><span class="muted small">${escapeHtml(e.instrucao)}</span>` : ''}</span></label>`).join('');
    const campos = atividade.questoes.map((q, i) => `
      <div class="input-group"><label>${i + 1}. ${escapeHtml(q)}</label>
        <textarea class="input" name="q${i}" rows="2" ${enviada ? 'disabled' : ''}>${escapeHtml(salvas[i] || '')}</textarea></div>`).join('');
    const feedbacks = (atividade.feedbacks || []).map(f => `<p class="small" style="margin-top:8px"><span class="chip">${escapeHtml(f.tipo)}</span> ${escapeHtml(f.mensagem)}</p>`).join('');
    window.openModal?.(escapeHtml(atividade.titulo), `
      <p class="muted small">${escapeHtml(atividade.descricao || '')}</p>
      <form id="respostaForm" class="auth-form" style="margin-top:12px;max-height:60vh;overflow:auto">
        ${etapas ? `<h4>Etapas</h4><div>${etapas}</div>` : ''}${campos}
        ${!etapas && !campos ? '<p class="muted">Esta atividade não tem questões.</p>' : ''}${feedbacks}</form>`,
      enviada ? '<button class="btn btn-light modal-close" type="button">Fechar</button>'
        : '<button class="btn btn-light" type="button" id="salvarRascunho">Salvar progresso</button><button class="btn btn-primary" type="button" id="enviarAtividade">Enviar</button>');
    if (enviada) return;

    const coletar = () => ({
      respostas: atividade.questoes.length ? atividade.questoes.map((_, i) => document.querySelector(`#respostaForm [name="q${i}"]`).value) : undefined,
      etapasConcluidas: [...document.querySelectorAll('#respostaForm [data-etapa]:checked')].map(c => Number(c.dataset.etapa))
    });
    const enviar = async finalizar => {
      try {
        // Ao enviar, o rascunho é salvo antes: se faltar algo, o que foi digitado não se perde.
        if (finalizar) await AdaptEducaAPI.put(`/atividades/${atividade.id}/resposta`, { ...coletar(), enviar: false });
        await AdaptEducaAPI.put(`/atividades/${atividade.id}/resposta`, { ...coletar(), enviar: finalizar });
        document.querySelector('.modal-backdrop')?.remove();
        window.showToast?.(finalizar ? 'Atividade enviada!' : 'Progresso salvo.', 'success');
        await renderAtividadesAluno();
      } catch (error) { window.showToast?.(error.message, 'error'); }
    };
    document.querySelector('#salvarRascunho').addEventListener('click', () => enviar(false));
    document.querySelector('#enviarAtividade').addEventListener('click', () => enviar(true));
    // cada etapa marcada é salva na hora
    document.querySelectorAll('#respostaForm [data-etapa]').forEach(box => box.addEventListener('change', async () => {
      try { await AdaptEducaAPI.put(`/atividades/${atividade.id}/resposta`, { etapasConcluidas: coletar().etapasConcluidas }); }
      catch (error) { window.showToast?.(error.message, 'error'); }
    }));
  }

}());
