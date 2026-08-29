(function(){
  const SESSION='adapteduca_session', QUESTIONNAIRE='adapteduca_questionnaire';
  const root=()=>document.body?.dataset.root||'./';

  function session(){try{return JSON.parse(localStorage.getItem(SESSION)||'null')}catch{return null}}
  function setSession(user){
    const safe={id:user.id,name:user.nome,email:user.email,role:(user.tipoPerfil||'').toLowerCase(),questionnaireCompleted:!!user.questionnaireCompleted,learningMethods:user.learningMethods||[]};
    try{localStorage.setItem(SESSION,JSON.stringify(safe))}catch{}
    return safe;
  }
  async function login(email,password){
    const response=await window.AdaptEducaAPI.login({email,senha:password});
    return setSession(response.dados);
  }
  async function register(data){
    const response=await window.AdaptEducaAPI.register({
      nome:data.name,email:data.email,senha:data.password,tipoPerfil:data.role,
      matricula:data.matricula || undefined
    });
    return setSession(response.dados);
  }
  function logout(){try{localStorage.removeItem(SESSION)}catch{}location.href=root()+'login.html'}
  function dashboardPath(role){return root()+'dashboard-'+role+'.html'}
  function goToDashboard(user=session()){
    if(!user){location.href=root()+'login.html';return}
    if(user.role==='aluno'&&!user.questionnaireCompleted){location.href=root()+'questionario-aluno.html';return}
    location.href=dashboardPath(user.role)
  }
  function completeQuestionnaire(answers){
    try{localStorage.setItem(QUESTIONNAIRE,JSON.stringify(answers))}catch{}
    const s=session(); if(!s)return;
    s.questionnaireCompleted=true;s.learningMethods=answers.formats||[];
    try{localStorage.setItem(SESSION,JSON.stringify(s))}catch{}
  }
  function guard(){
    const body=document.body;if(!body||body.dataset.private!=='true')return;
    const s=session();
    if(!s){const redirect=encodeURIComponent(location.pathname.split('/').pop());location.replace(root()+'login.html?redirect='+redirect);return}
    const allowed=body.dataset.role;
    if(allowed&&allowed!==s.role){location.replace(dashboardPath(s.role));}
    if(s.role==='aluno'&&!s.questionnaireCompleted&&!location.pathname.endsWith('questionario-aluno.html'))location.replace(root()+'questionario-aluno.html')
  }
  window.AdaptAuth={session,login,register,logout,goToDashboard,completeQuestionnaire,dashboardPath};
  guard();
  document.addEventListener('DOMContentLoaded',()=>{
    document.addEventListener('click',e=>{if(e.target.closest('[data-logout]'))logout()});
    const loginForm=document.querySelector('#loginForm');
    if(loginForm)loginForm.addEventListener('submit',async e=>{
      e.preventDefault(); const data=new FormData(loginForm);
      try{const user=await login(data.get('email'),data.get('password'));window.showToast?.('Login realizado com sucesso!','success');setTimeout(()=>goToDashboard(user),350)}
      catch(err){window.showToast?.(err.message,'error')}
    });
    document.querySelectorAll('[data-demo-login]').forEach(btn=>btn.addEventListener('click',async()=>{
      const demos={
        aluno:['maria.silva@aluno.com','senha123'],
        professor:['joao.costa@adapteduca.com','senha123'],
        responsavel:['responsavel.silva@gmail.com','senha123']
      };
      const credentials=demos[btn.dataset.demoLogin];
      if(!credentials)return;
      try{const user=await login(...credentials);goToDashboard(user)}
      catch(err){window.showToast?.(err.message,'error')}
    }));
    const registerForm=document.querySelector('#registerForm');
    if(registerForm)registerForm.addEventListener('submit',async e=>{
      e.preventDefault();const data=new FormData(registerForm);
      if(!data.get('terms')){window.showToast?.('Você precisa aceitar os Termos de Uso.','error');return}
      if(data.get('password')!==data.get('confirmPassword')){window.showToast?.('As senhas não coincidem.','error');return}
      const roleMap={aluno:'Aluno',professor:'Professor',responsavel:'Responsavel'};
      try{const user=await register({name:data.get('name'),email:data.get('email'),password:data.get('password'),role:roleMap[data.get('role')]||'Aluno'});window.showToast?.('Conta criada com sucesso!','success');setTimeout(()=>goToDashboard(user),350)}
      catch(err){window.showToast?.(err.message,'error')}
    });
  });
})();
