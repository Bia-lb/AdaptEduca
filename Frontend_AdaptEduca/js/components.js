(function () {
  const root = () => document.body.dataset.root || './';
  const page = () => document.body.dataset.page || '';

  const isCurrent = (href) => page() === href.split('/').pop().replace('.html', '');
  const link = (href, label, icon = '', extraClass = '') =>
    `<a href="${root()}${href}" class="${isCurrent(href) ? 'active ' : ''}${extraClass}">${icon ? `<span aria-hidden="true">${icon}</span>` : ''}${label}</a>`;

  function referenceHeader() {
    const currentPage = page();
    const roleClass = (role) => currentPage === `dashboard-${role}` ? 'active reference-active' : '';

    return `
      <header class="site-header reference-header">
        <div class="container header-inner">
          <a class="brand" href="${root()}index.html" aria-label="AdaptEduca - Início">
            <span class="brand-mark" aria-hidden="true"></span>
            <span>AdaptEduca</span>
          </a>
          <nav class="main-nav" id="mainNav" aria-label="Navegação principal">
            <a href="${root()}index.html">Início</a>
            <a href="${root()}demo.html"><span aria-hidden="true">✣</span> Demo</a>
            <a class="${roleClass('aluno')}" href="${root()}login.html?perfil=aluno"><span aria-hidden="true">♙</span> Aluno</a>
            <a class="${roleClass('professor')}" href="${root()}login.html?perfil=professor"><span aria-hidden="true">♧</span> Professor</a>
            <a class="${roleClass('responsavel')}" href="${root()}login.html?perfil=responsavel"><span aria-hidden="true">♧</span> Responsável</a>
            <a href="${root()}planos.html"><span aria-hidden="true">$</span> Preços</a>
          </nav>
          <div class="header-actions">
            <button class="theme-toggle" type="button" data-theme-toggle aria-label="Alternar tema">☾</button>
            <a class="desktop-only reference-login" href="${root()}login.html"><span aria-hidden="true">↪</span> Entrar</a>
            <a class="btn btn-primary reference-register" href="${root()}cadastro.html">Cadastrar</a>
            <button class="menu-toggle" type="button" data-menu-toggle aria-label="Abrir menu">☰</button>
          </div>
        </div>
      </header>`;
  }

  function header() {
    if (document.body.dataset.referenceHeader === 'true') return referenceHeader();

    const session = window.AdaptAuth?.session();
    const publicNav = `${link('index.html', 'Início')}${link('demo.html', 'Demo', '✣')}${link('login.html?perfil=aluno', 'Aluno', '♙')}${link('login.html?perfil=professor', 'Professor', '♧')}${link('login.html?perfil=responsavel', 'Responsável', '♧')}${link('planos.html', 'Preços', '$')}`;
    const roleLinks = session ? roleNav(session.role) : '';

    return `<header class="site-header"><div class="container header-inner"><a class="brand" href="${root()}index.html" aria-label="AdaptEduca - Início"><span class="brand-mark" aria-hidden="true"></span><span>AdaptEduca</span></a><nav class="main-nav" id="mainNav" aria-label="Navegação principal">${session ? roleLinks : publicNav}</nav><div class="header-actions"><button class="theme-toggle" type="button" data-theme-toggle aria-label="Alternar tema">☾</button>${session ? `<div class="profile-menu"><button class="profile-button" type="button" data-profile-toggle><span class="avatar">${session.name.charAt(0)}</span><span class="desktop-only">${session.name.split(' ')[0]}</span>⌄</button><div class="dropdown" data-profile-dropdown><a href="${window.AdaptAuth.dashboardPath(session.role)}">Meu painel</a><a href="${settingsPath(session.role)}">Configurações</a><button type="button" data-logout>Sair</button></div></div>` : `<a class="desktop-only" href="${root()}login.html">↪ Entrar</a><a class="btn btn-primary" href="${root()}cadastro.html">Cadastrar</a>`}<button class="menu-toggle" type="button" data-menu-toggle aria-label="Abrir menu">☰</button></div></div></header>`;
  }

  function settingsPath(role) {
    if (role === 'aluno') return root() + 'perfil-aluno.html';
    if (role === 'professor') return root() + 'configuracoes-professor.html';
    return root() + 'configuracoes-responsavel.html';
  }

  function roleNav(role) {
    if (role === 'aluno') return `${link('dashboard-aluno.html', 'Início')}${link('conteudos-aluno.html', 'Conteúdos', '▤')}${link('atividades-aluno.html', 'Atividades', '✓')}${link('historico-aluno.html', 'Histórico', '◷')}${link('adaptacao-conteudo.html', 'Adaptar com IA', '✣')}`;
    if (role === 'professor') return `${link('dashboard-professor.html', 'Dashboard')}${link('turmas.html', 'Turmas')}${link('alunos.html', 'Alunos')}${link('enviar-conteudo.html', 'Enviar Conteúdo')}${link('materiais.html', 'Materiais')}${link('atividades-professor.html', 'Atividades')}${link('relatorios-professor.html', 'Relatórios')}`;
    return `${link('dashboard-responsavel.html', 'Dashboard')}${link('acompanhamento.html', 'Acompanhamento')}${link('desempenho.html', 'Desempenho')}${link('progresso-responsavel.html', 'Progresso')}${link('relatorios-responsavel.html', 'Relatórios')}${link('comunicados.html', 'Comunicados')}`;
  }

  function footer() {
    return `<footer class="section" style="padding:32px 0;border-top:1px solid var(--border);background:var(--surface)"><div class="container" style="display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap"><div class="brand"><span class="brand-mark"></span><span>AdaptEduca</span></div><nav style="display:flex;gap:16px;flex-wrap:wrap"><a href="${root()}funcionalidades.html">Funcionalidades</a><a href="${root()}demo.html">Demo</a><a href="${root()}planos.html">Planos</a></nav><p class="muted small">© 2026 AdaptEduca</p></div></footer>`;
  }

  function init() {
    const headerHost = document.querySelector('#site-header');
    if (headerHost) headerHost.innerHTML = header();

    const currentUser = window.AdaptAuth?.session();
    if (currentUser) {
      document.querySelectorAll('[data-user-name]').forEach((element) => { element.textContent = currentUser.name; });
      document.querySelectorAll('[data-user-first]').forEach((element) => { element.textContent = currentUser.name.split(' ')[0]; });
    }

    const footerHost = document.querySelector('#site-footer');
    if (footerHost) footerHost.innerHTML = footer();

    document.body.insertAdjacentHTML('beforeend', '<button class="help-fab" type="button" data-help aria-label="Ajuda">?</button><div class="toast-stack" id="toastStack" aria-live="polite"></div>');
    window.AdaptTheme?.apply(document.documentElement.dataset.theme || 'light');

    document.addEventListener('click', (event) => {
      if (event.target.closest('[data-menu-toggle]')) document.querySelector('#mainNav')?.classList.toggle('open');
      if (event.target.closest('[data-profile-toggle]')) document.querySelector('[data-profile-dropdown]')?.classList.toggle('open');
      if (event.target.closest('[data-help]')) showHelp();
    });
  }

  function showHelp() {
    window.openModal?.('Central de Ajuda', 'Esta é uma demonstração funcional do AdaptEduca. Navegue pelas páginas e use os dados de teste disponíveis na tela de login.');
  }

  document.addEventListener('DOMContentLoaded', init);
}());
