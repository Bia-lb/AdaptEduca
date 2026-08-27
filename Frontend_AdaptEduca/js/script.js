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

    const courses = AdaptEducaData.courses.filter((course) => course.subject === subject);
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
      window.showToast?.('Conteúdo adaptado com sucesso!', 'success');
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

    document.querySelector('#chatForm')?.addEventListener('submit', (event) => {
      event.preventDefault();
      const input = event.target.elements.message;
      if (!input.value.trim()) return;
      const messages = document.querySelector('#chatMessages');
      messages?.insertAdjacentHTML('beforeend', `<div class="chat-bubble user">${escapeHtml(input.value)}</div>`);
      const question = input.value;
      input.value = '';
      setTimeout(() => {
        messages?.insertAdjacentHTML('beforeend', `<div class="chat-bubble">Com base no conteúdo enviado, posso explicar “${escapeHtml(question)}” em etapas curtas e com exemplos práticos.</div>`);
        if (messages) messages.scrollTop = messages.scrollHeight;
      }, 500);
    });
  }

  function renderOutput(mode, text) {
    const pane = document.querySelector('#outputPane');
    if (!pane) return;
    const clean = escapeHtml(text.slice(0, 900));

    if (mode.includes('Mapa')) {
      pane.innerHTML = '<div class="mind-map"><div class="mind-node">Tema central</div><div class="mind-node">Conceito 1</div><div class="mind-node">Conceito 2</div><div class="mind-node">Exemplo</div><div class="mind-node">Revisão</div></div>';
      return;
    }

    if (mode.includes('Áudio')) {
      pane.innerHTML = '<div class="audio-player"><button class="btn btn-primary" type="button" data-play-audio>▶</button><div style="flex:1"><strong>Narração adaptada</strong><div class="progress" style="margin-top:8px"><span style="width:38%"></span></div></div><span class="muted small">02:34</span></div>';
      pane.querySelector('[data-play-audio]')?.addEventListener('click', () => window.showToast?.('Reprodução simulada iniciada.', 'success'));
      return;
    }

    const modeHint = mode.includes('TDAH')
      ? 'Organizado em blocos curtos, com foco nos pontos essenciais.'
      : mode.includes('TEA')
        ? 'Estruturado com linguagem literal, previsível e objetiva.'
        : mode.includes('Simplificado')
          ? 'Reescrito com palavras simples e frases diretas.'
          : 'Resumido com os conceitos mais importantes.';

    pane.innerHTML = `<h3>${escapeHtml(mode)}</h3><p class="muted" style="margin-top:10px;line-height:1.8">${clean}</p><hr style="border:0;border-top:1px solid var(--border);margin:18px 0"><h4>Pontos principais</h4><ul style="display:grid;gap:8px;margin-top:10px"><li>• ${modeHint}</li><li>• Ideias separadas para facilitar a revisão.</li><li>• Exemplo prático para reforçar a compreensão.</li></ul>`;
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
  }
}());

  async function initApiPages() {
    if (!window.AdaptEducaAPI) return;
    const page = document.body?.dataset.page;

    try {
      if (page === 'alunos') await renderAlunosFromApi();
      if (page === 'turmas') await renderTurmasFromApi();
      if (page === 'atividades-professor') await renderAtividadesFromApi();
      if (page === 'dashboard-responsavel') await renderResponsavelFromApi();
    } catch (error) {
      console.error(error);
      window.showToast?.(`Não foi possível carregar a API: ${error.message}`, 'error');
    }
  }

  async function renderAlunosFromApi() {
    const table = document.querySelector('#studentsTable tbody');
    if (!table) return;
    const result = await AdaptEducaAPI.get('/alunos/');
    const alunos = result.dados || [];
    table.innerHTML = alunos.map(aluno => `
      <tr>
        <td><strong>${escapeHtml(aluno.nome)}</strong></td>
        <td>—</td>
        <td>${Number(aluno.progresso || 0)}%</td>
        <td>—</td>
        <td><span class="chip">${Number(aluno.progresso || 0) >= 80 ? 'Bom desempenho' : 'Acompanhar'}</span></td>
        <td><button class="btn btn-light" data-modal-title="${escapeHtml(aluno.nome)}"
          data-modal-message="Matrícula: ${escapeHtml(aluno.matricula || '—')}. Progresso: ${Number(aluno.progresso || 0)}%.">
          Detalhes
        </button></td>
      </tr>`).join('') || '<tr><td colspan="6">Nenhum aluno cadastrado.</td></tr>';
    initReferenceInteractions();
  }

  async function renderTurmasFromApi() {
    const host = document.querySelector('.class-overview');
    if (!host) return;
    const result = await AdaptEducaAPI.get('/turmas/');
    const turmas = result.dados || [];
    host.innerHTML = turmas.map(turma => `
      <article class="class-card card">
        <h3>${escapeHtml(turma.nome)}</h3>
        <p class="muted small">Código: ${escapeHtml(turma.codigo)}</p>
        <div class="class-metrics">
          <span>Professor</span><strong>${escapeHtml(String(turma.professor_id))}</strong>
          <span>Descrição</span><strong>${escapeHtml(turma.descricao || '—')}</strong>
        </div>
        <button class="btn btn-light btn-block" data-modal-title="${escapeHtml(turma.nome)}"
          data-modal-message="Código: ${escapeHtml(turma.codigo)}. Professor ID: ${turma.professor_id}.">
          Ver turma
        </button>
      </article>`).join('') || '<div class="card card-pad">Nenhuma turma cadastrada.</div>';
    initReferenceInteractions();
  }

  async function renderAtividadesFromApi() {
    const grid = document.querySelector('.grid.grid-2');
    if (!grid) return;
    const result = await AdaptEducaAPI.get('/atividades/');
    const atividades = result.dados || [];
    grid.innerHTML = atividades.map(a => `
      <article class="card card-pad">
        <span class="chip">Turma #${a.turma_id}</span>
        <h3 style="margin:12px 0 5px">${escapeHtml(a.titulo)}</h3>
        <p class="muted small">${escapeHtml(a.descricao || 'Sem descrição')} · prazo: ${escapeHtml(a.prazo || '—')}</p>
        <p class="small"><strong>Status:</strong> ${escapeHtml(a.status)}</p>
        <button class="btn btn-light" style="margin-top:14px" data-modal-title="${escapeHtml(a.titulo)}"
          data-modal-message="Status: ${escapeHtml(a.status)}. Turma: ${a.turma_id}.">
          Ver detalhes
        </button>
      </article>`).join('') || '<div class="card card-pad">Nenhuma atividade cadastrada.</div>';
    initReferenceInteractions();
  }

  async function renderResponsavelFromApi() {
    const user = window.AdaptAuth?.session();
    if (!user?.id) return;
    const result = await AdaptEducaAPI.get(`/responsavel/api/${user.id}/dashboard`);
    const dados = result.dados;
    const heroName = document.querySelector('[data-user-name]');
    if (heroName) heroName.textContent = dados.responsavel.nome;
    const stats = document.querySelectorAll('.reference-stat-card .stat-copy strong');
    if (stats[0]) stats[0].textContent = dados.totalFilhos;
    if (stats[1]) stats[1].textContent = `${dados.progressoMedio}%`;
    const cards = document.querySelectorAll('.reference-child-card');
    (dados.alunos || []).forEach((aluno, index) => {
      const card = cards[index];
      if (!card) return;
      const title = card.querySelector('.child-identity h2');
      const progress = card.querySelector('.child-progress strong');
      const metrics = card.querySelectorAll('.child-metric strong');
      if (title) title.textContent = aluno.nome;
      if (progress) progress.textContent = `${aluno.progresso || 0}%`;
      if (metrics[0]) metrics[0].textContent = aluno.atividadesConcluidas;
      if (metrics[1]) metrics[1].textContent = aluno.emAndamento;
      const bar = card.querySelector('.progress span');
      if (bar) bar.style.width = `${aluno.progresso || 0}%`;
    });
  }
