/* RF03: recuperação de senha */
(function () {
  const $ = s => document.querySelector(s);
  document.addEventListener('DOMContentLoaded', () => {
    $('#forgotForm')?.addEventListener('submit', async e => {
      e.preventDefault();
      const btn = e.target.querySelector('button[type=submit]');
      btn.disabled = true;
      try {
        const r = await AdaptEducaAPI.post('/auth/esqueci-senha', { email: new FormData(e.target).get('email').trim() });
        $('#forgotMsg').textContent = r.mensagem;
      } catch (err) { $('#forgotMsg').textContent = err.message; btn.disabled = false; }
    });

    $('#resetForm')?.addEventListener('submit', async e => {
      e.preventDefault();
      const f = new FormData(e.target), msg = $('#resetMsg');
      const token = new URLSearchParams(location.search).get('token');
      if (!token) { msg.textContent = 'Link inválido. Peça um novo em “Esqueceu a senha?”.'; return; }
      if (f.get('password') !== f.get('confirm')) { msg.textContent = 'As senhas não coincidem.'; return; }
      try {
        const r = await AdaptEducaAPI.post('/auth/redefinir-senha', { token, senha: f.get('password') });
        msg.textContent = r.mensagem;
        setTimeout(() => { location.href = 'login.html'; }, 1500);
      } catch (err) { msg.textContent = err.message; }
    });
  });
})();
