(function(){
  const USERS='adapteduca_users',SESSION='adapteduca_session',QUESTIONNAIRE='adapteduca_questionnaire';
  const root=()=>document.body?.dataset.root||'./';
  function users(){let current=[];try{current=JSON.parse(localStorage.getItem(USERS)||'[]')}catch{};if(!current.length){current=window.AdaptEducaData.demoUsers;try{localStorage.setItem(USERS,JSON.stringify(current))}catch{}}return current}
  function saveUsers(value){try{localStorage.setItem(USERS,JSON.stringify(value))}catch{}}
  function nameState(){try{return JSON.parse(window.name||'{}')}catch{return {}}}
  function saveNameSession(value){const state=nameState();if(value)state.adapteducaSession=value;else delete state.adapteducaSession;try{window.name=JSON.stringify(state)}catch{}}
  function session(){try{const local=JSON.parse(localStorage.getItem(SESSION)||'null');if(local)return local}catch{}return nameState().adapteducaSession||null}
  function setSession(user){const safe={id:user.id,name:user.name,email:user.email,role:user.role,questionnaireCompleted:!!user.questionnaireCompleted,learningMethods:user.learningMethods||[]};try{localStorage.setItem(SESSION,JSON.stringify(safe))}catch{}saveNameSession(safe);return safe}
  function login(email,password){const user=users().find(u=>u.email.toLowerCase()===email.trim().toLowerCase()&&u.password===password);if(!user)return null;return setSession(user)}
  function register(data){const all=users();if(all.some(u=>u.email.toLowerCase()===data.email.toLowerCase()))throw new Error('Já existe uma conta com este e-mail.');const user={...data,id:Date.now(),questionnaireCompleted:data.role!=='aluno'};all.push(user);saveUsers(all);return setSession(user)}
  function logout(){try{localStorage.removeItem(SESSION)}catch{}saveNameSession(null);location.href=root()+'login.html'}
  function dashboardPath(role){return root()+'dashboard-'+role+'.html'}
  function goToDashboard(user=session()){if(!user){location.href=root()+'login.html';return}if(user.role==='aluno'&&!user.questionnaireCompleted){location.href=root()+'questionario-aluno.html';return}location.href=dashboardPath(user.role)}
  function completeQuestionnaire(answers){try{localStorage.setItem(QUESTIONNAIRE,JSON.stringify(answers))}catch{}const s=session();if(!s)return;const all=users();const idx=all.findIndex(u=>u.id===s.id);if(idx>=0){all[idx].questionnaireCompleted=true;all[idx].learningMethods=answers.formats||[];saveUsers(all);s.questionnaireCompleted=true;s.learningMethods=answers.formats||[];setSession(s)}}
  function guard(){const body=document.body;if(!body)return;const isPrivate=body.dataset.private==='true';if(!isPrivate)return;const s=session();if(!s){const redirect=encodeURIComponent(location.pathname.split('/').pop());location.replace(root()+'login.html?redirect='+redirect);return}const allowed=body.dataset.role;if(allowed&&allowed!==s.role){location.replace(dashboardPath(s.role));return}if(s.role==='aluno'&&!s.questionnaireCompleted&&!location.pathname.endsWith('questionario-aluno.html'))location.replace(root()+'questionario-aluno.html')}
  window.AdaptAuth={users,session,login,register,logout,goToDashboard,completeQuestionnaire,dashboardPath};
  guard();
  document.addEventListener('DOMContentLoaded',()=>{
    document.addEventListener('click',e=>{if(e.target.closest('[data-logout]'))logout()});
    const loginForm=document.querySelector('#loginForm');
    if(loginForm)loginForm.addEventListener('submit',e=>{e.preventDefault();const data=new FormData(loginForm);const user=login(data.get('email'),data.get('password'));if(!user){window.showToast?.('E-mail ou senha incorretos.','error');return}window.showToast?.('Login realizado com sucesso!','success');setTimeout(()=>goToDashboard(user),350)});
    document.querySelectorAll('[data-demo-login]').forEach(btn=>btn.addEventListener('click',()=>{const role=btn.dataset.demoLogin;const demo=window.AdaptEducaData.demoUsers.find(u=>u.role===role);setSession(demo);goToDashboard(demo)}));
    const requestedProfile=new URLSearchParams(location.search).get('perfil');if(requestedProfile){const option=document.querySelector(`.role-option input[value="${requestedProfile}"]`)?.closest('.role-option');if(option){document.querySelectorAll('.role-option').forEach(o=>o.classList.remove('selected'));option.classList.add('selected');option.querySelector('input').checked=true}}
    const registerForm=document.querySelector('#registerForm');
    if(registerForm)registerForm.addEventListener('submit',e=>{e.preventDefault();const data=new FormData(registerForm);if(!data.get('terms')){window.showToast?.('Você precisa aceitar os Termos de Uso.','error');return}if(data.get('password')!==data.get('confirmPassword')){window.showToast?.('As senhas não coincidem.','error');return}try{const user=register({name:data.get('name'),email:data.get('email'),password:data.get('password'),role:data.get('role')||'aluno'});window.showToast?.('Conta criada com sucesso!','success');setTimeout(()=>goToDashboard(user),350)}catch(err){window.showToast?.(err.message,'error')}});
  });
})();
