document.addEventListener('DOMContentLoaded', function() {
  const apiBase = window.location.protocol === 'file:' ? 'http://127.0.0.1:5000/api' : '/api';
  const menuBtn = document.querySelector('.mobile-menu-btn');
  const navLinks = document.querySelector('.nav-links');

  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', function() {
      navLinks.classList.toggle('open');
    });
  }

  document.querySelectorAll('[data-chip-group]').forEach(group => {
    const chips = group.querySelectorAll('.chip');
    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        chips.forEach(item => item.classList.remove('active'));
        chip.classList.add('active');
      });
    });
  });

  document.querySelectorAll('.profile-type').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.profile-type').forEach(item => item.classList.remove('selected'));
      card.classList.add('selected');
    });
  });

  document.querySelectorAll('[data-option-group]').forEach(group => {
    const mode = group.getAttribute('data-mode') || 'multi';
    const cards = group.querySelectorAll('.option-card');
    cards.forEach(card => {
      card.addEventListener('click', () => {
        if (mode === 'single') {
          cards.forEach(item => item.classList.remove('selected'));
          card.classList.add('selected');
        } else {
          card.classList.toggle('selected');
        }
      });
    });
  });

  document.querySelectorAll('[data-tab-group]').forEach(group => {
    const buttons = group.querySelectorAll('.tab-btn');
    buttons.forEach(button => {
      button.addEventListener('click', () => {
        buttons.forEach(item => item.classList.remove('active'));
        button.classList.add('active');
      });
    });
  });

  function normalizarPerfil(valor) {
    const perfil = valor.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    if (perfil.includes('professor')) return 'professor';
    if (perfil.includes('responsavel')) return 'responsavel';
    return 'aluno';
  }

  function destinoPerfil(perfil) {
    return {
      aluno: 'aluno.html',
      professor: 'professor.html',
      responsavel: 'responsavel.html'
    }[perfil] || 'aluno.html';
  }

  function exibirMensagem(form, mensagem, erro) {
    let aviso = form.querySelector('.form-message');
    if (!aviso) {
      aviso = document.createElement('div');
      aviso.className = 'form-message';
      aviso.style.marginTop = '12px';
      aviso.style.fontSize = '14px';
      aviso.style.textAlign = 'center';
      form.appendChild(aviso);
    }
    aviso.textContent = mensagem;
    aviso.style.color = erro ? '#b91c1c' : '#047857';
  }

  async function enviarCadastro(form) {
    const nome = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const senha = document.getElementById('reg-pwd').value;
    const confirmarSenha = document.getElementById('reg-pwd2').value;
    const selectedProfile = form.querySelector('.profile-type.selected h4');
    const perfil = normalizarPerfil(selectedProfile ? selectedProfile.textContent : 'aluno');

    if (senha !== confirmarSenha) {
      throw new Error('As senhas não coincidem.');
    }

    const response = await fetch(`${apiBase}/usuarios`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({nome, email, senha, tipoPerfil: perfil})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.erro || 'Não foi possível criar a conta.');
    localStorage.setItem('adaptEduca_user', JSON.stringify({...data, perfil, logado: true}));
    return perfil;
  }

  async function enviarLogin() {
    const email = document.getElementById('login-email').value.trim();
    const senha = document.getElementById('login-pwd').value;
    const response = await fetch(`${apiBase}/auth/login`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({email, senha})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.erro || 'E-mail ou senha inválidos.');
    const perfil = normalizarPerfil(data.tipoPerfil || 'aluno');
    localStorage.setItem('adaptEduca_user', JSON.stringify({...data, perfil, logado: true}));
    return perfil;
  }

  document.querySelectorAll('form[data-form]').forEach(form => {
    form.addEventListener('submit', async event => {
      event.preventDefault();
      const tipo = form.getAttribute('data-form');
      const button = form.querySelector('button[type="submit"]');
      const textoOriginal = button ? button.innerHTML : '';
      if (button) {
        button.innerHTML = 'Processando...';
        button.disabled = true;
      }
      try {
        const perfil = tipo === 'login' ? await enviarLogin() : await enviarCadastro(form);
        exibirMensagem(form, tipo === 'login' ? 'Login realizado com sucesso.' : 'Conta criada com sucesso.', false);
        window.setTimeout(() => {
          window.location.href = destinoPerfil(perfil);
        }, 500);
      } catch (error) {
        exibirMensagem(form, error.message, true);
      } finally {
        if (button) {
          button.innerHTML = textoOriginal;
          button.disabled = false;
        }
      }
    });
  });

  document.querySelectorAll('[data-logout]').forEach(button => {
    button.addEventListener('click', event => {
      event.preventDefault();
      localStorage.removeItem('adaptEduca_user');
      window.location.href = 'index.html';
    });
  });

  document.querySelectorAll('.progress-bar[data-progress]').forEach(bar => {
    const progresso = bar.getAttribute('data-progress');
    bar.style.width = '0%';
    window.setTimeout(() => {
      bar.style.width = `${progresso}%`;
    }, 80);
  });

  const sessao = JSON.parse(localStorage.getItem('adaptEduca_user') || 'null');
  if (sessao && sessao.nome && window.location.pathname.endsWith('aluno.html')) {
    const titulo = document.querySelector('.dash-hero h1');
    if (titulo) titulo.textContent = `Olá, ${sessao.nome.split(' ')[0]}! 👋`;
  }
});
