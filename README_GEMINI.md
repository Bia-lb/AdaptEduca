# AdaptEduca — integração Gemini (ambiente local)

Esta versão substitui o cliente Anthropic por `google-genai` nas chamadas dos agentes existentes.
Não inclua seu `.env` real no GitHub.

## Instalação

1. Abra a pasta principal `AdaptEduca-main` no VS Code.
2. Dentro de `Backend_AdaptEduca`, crie ou edite `.env` com as variáveis MySQL existentes e:
   ```
   GEMINI_API_KEY=SUA_CHAVE_GERADA_NO_GOOGLE_AI_STUDIO
   GEMINI_MODEL=gemini-2.5-flash
   IA_LIMITE_DIARIO=20
   IA_TIMEOUT=40
   ```
3. No terminal da pasta principal:
   ```powershell
   cd Backend_AdaptEduca
   py -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe app.py
   ```
4. No segundo terminal da pasta principal:
   ```powershell
   cd Frontend_AdaptEduca
   py -m http.server 5500
   ```
5. Teste `http://127.0.0.1:5000/api/health` e abra `http://localhost:5500/login.html`.
6. Entre com um aluno ou professor existente e teste "Conversar com a IA". Em seguida, teste Resumo, Mapa Mental, TDAH, TEA e Simplificado.

## Notas

- Somente o backend lê a chave Gemini; não coloque a chave no frontend.
- Os dados MySQL existentes são preservados: esta integração não contém migração SQL.
- A rota `/api/ia/status` indica se existe configuração local, mas não verifica a cota remota do Google.
- O plano gratuito da API tem limites externos, variáveis conforme modelo, região e conta. Consulte https://ai.google.dev/gemini-api/docs/pricing .
- A análise pedagógica executa consultas autorizadas no servidor e envia os resultados resumidos ao Gemini. Não é um agente de ferramentas interativas como o Claude anterior.
- Não foi possível realizar chamadas reais ao Google sem uma chave válida e acesso ao servidor do usuário. Valide no ambiente local antes da apresentação.
- A chave e os dados enviados a modelos gratuitos podem ter regras de retenção/uso; use dados de demonstração, não dados pessoais de alunos reais.
