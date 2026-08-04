(function(){
  const key='adapteduca_theme';
  function apply(theme){document.documentElement.dataset.theme=theme;localStorage.setItem(key,theme);updateButtons(theme)}
  function updateButtons(theme){document.querySelectorAll('[data-theme-toggle]').forEach(btn=>{btn.textContent=theme==='dark'?'☀':'☾';btn.setAttribute('aria-label',theme==='dark'?'Ativar modo claro':'Ativar modo escuro')})}
  window.AdaptTheme={toggle(){apply(document.documentElement.dataset.theme==='dark'?'light':'dark')},apply};
  document.addEventListener('DOMContentLoaded',()=>{const theme=localStorage.getItem(key)||document.documentElement.dataset.theme||'light';document.documentElement.dataset.theme=theme;updateButtons(theme);document.addEventListener('click',e=>{if(e.target.closest('[data-theme-toggle]'))window.AdaptTheme.toggle()})});
})();
