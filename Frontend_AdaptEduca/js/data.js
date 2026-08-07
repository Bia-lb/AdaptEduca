window.AdaptEducaData={
  demoUsers:[
    {id:1,name:'Maria Silva',email:'aluno@adapteduca.com',password:'123456',role:'aluno',questionnaireCompleted:true,learningMethods:['Visual (Vídeos)','Mapas Mentais']},
    {id:2,name:'Carlos Santos',email:'professor@adapteduca.com',password:'123456',role:'professor',questionnaireCompleted:true},
    {id:3,name:'Sr(a). Silva',email:'responsavel@adapteduca.com',password:'123456',role:'responsavel',questionnaireCompleted:true}
  ],
  courses:[
    {subject:'Matemática',title:'Equações do 2º Grau',tags:['▶ Vídeo','▤ Resumo','◉ Exercício'],progress:100,status:'Concluído'},
    {subject:'Matemática',title:'Geometria Espacial',tags:['▶ Vídeo','♧ Mapa','♬ Áudio'],progress:60,status:'60%'},
    {subject:'Matemática',title:'Funções Trigonométricas',tags:['▶ Vídeo','▤ Resumo','◉ Exercício'],progress:0,status:'Não iniciado'},
    {subject:'Português',title:'Análise Sintática',tags:['▶ Vídeo','▤ Resumo','◉ Quiz'],progress:35,status:'35%'},
    {subject:'História',title:'Revolução Francesa',tags:['▤ Resumo','♧ Mapa','◉ Exercício'],progress:48,status:'48%'},
    {subject:'Ciências',title:'Ecossistemas',tags:['▶ Vídeo','♬ Áudio','◉ Exercício'],progress:10,status:'10%'}
  ],
  students:[
    {name:'Maria Silva',className:'9º Ano A',progress:85,done:24,ongoing:6,status:'Bom Desempenho',difficulty:'Geometria Espacial'},
    {name:'João Santos',className:'9º Ano A',progress:92,done:28,ongoing:4,status:'Excelente',difficulty:''},
    {name:'Carla Mendes',className:'8º Ano A',progress:88,done:26,ongoing:3,status:'Excelente',difficulty:''},
    {name:'Lucas Rocha',className:'9º Ano B',progress:68,done:17,ongoing:8,status:'Precisa de Atenção',difficulty:'Interpretação de Texto'}
  ],
  classes:[
    {name:'9º Ano A',students:32,progress:78},{name:'9º Ano B',students:28,progress:82},{name:'8º Ano A',students:30,progress:65}
  ],
  materials:[
    {title:'Equações do 2º Grau',subject:'Matemática',className:'9º Ano A',format:'PDF + Vídeo',date:'01/08/2026',views:128},
    {title:'Análise Sintática',subject:'Português',className:'9º Ano B',format:'Apresentação',date:'30/07/2026',views:96},
    {title:'Revolução Francesa',subject:'História',className:'8º Ano A',format:'Texto',date:'28/07/2026',views:84}
  ],
  communications:[
    {from:'Prof. Carlos Santos',title:'Progresso da Maria em Matemática',preview:'Gostaria de parabenizá-los pelo excelente desempenho da Maria...',when:'2 dias atrás'},
    {from:'Prof. Ana Costa',title:'Reforço em Português - João',preview:'Notei que o João está com dificuldade em análise sintática...',when:'3 dias atrás'},
    {from:'Coordenação Pedagógica',title:'Reunião de Pais - Próxima Semana',preview:'Convidamos todos os responsáveis para a reunião...',when:'5 dias atrás'}
  ]
};
