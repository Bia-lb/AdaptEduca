"""Ativa a IA do AdaptEduca: escolhe o provedor (tem opções GRÁTIS), grava a chave no .env."""
import os
import subprocess
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.join(PASTA, ".env")
EXEMPLO = os.path.join(PASTA, ".env.example")

PROVEDORES = {
    "1": {"nome": "Google Gemini (GRATIS, sem cartao)", "site": "aistudio.google.com/apikey  (botao 'Create API key')",
          "prefixo": "AIza", "conf": {"IA_PROVIDER": "openai", "IA_BASE_URL": "https://generativelanguage.googleapis.com/v1beta/openai/",
                                      "IA_MODEL": "gemini-2.5-flash"}, "chave": "IA_API_KEY"},
    "2": {"nome": "Groq (GRATIS, sem cartao)", "site": "console.groq.com/keys  (botao 'Create API Key')",
          "prefixo": "gsk_", "conf": {"IA_PROVIDER": "openai", "IA_BASE_URL": "https://api.groq.com/openai/v1",
                                      "IA_MODEL": "llama-3.3-70b-versatile"}, "chave": "IA_API_KEY"},
    "3": {"nome": "Claude da Anthropic (PAGO, melhor qualidade)", "site": "console.anthropic.com  (API Keys > Create Key)",
          "prefixo": "sk-ant-", "conf": {"IA_PROVIDER": "anthropic", "ANTHROPIC_MODEL": "claude-sonnet-5-5"}, "chave": "ANTHROPIC_API_KEY"},
}


def definir(linhas, chave, valor):
    novas, achou = [], False
    for l in linhas:
        if l.split("=", 1)[0].strip() == chave:
            novas.append(f"{chave}={valor}")
            achou = True
        else:
            novas.append(l)
    if not achou:
        novas.append(f"{chave}={valor}")
    return novas


def main():
    print("=== Ativar a IA do AdaptEduca ===\n")
    for k, p in PROVEDORES.items():
        print(f"  {k}) {p['nome']}")
    esc = input("\nEscolha 1, 2 ou 3: ").strip()
    if esc not in PROVEDORES:
        print("Opcao invalida. Nada foi alterado.")
        return 1
    p = PROVEDORES[esc]
    print(f"\nCrie a chave em: {p['site']}")
    chave = input("Cole a chave aqui e aperte Enter: ").strip().strip('"').strip("'")
    if not chave.startswith(p["prefixo"]) or len(chave) < 20:
        print(f"\nEssa chave nao parece valida (deve comecar com {p['prefixo']}). Nada foi alterado.")
        return 1
    origem = ENV if os.path.exists(ENV) else EXEMPLO
    linhas = open(origem, encoding="utf-8").read().splitlines() if os.path.exists(origem) else []
    for k, v in p["conf"].items():
        linhas = definir(linhas, k, v)
    linhas = definir(linhas, p["chave"], chave)
    with open(ENV, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print("\nConfiguracao salva em .env")
    if esc == "3":
        print("Instalando a biblioteca da Anthropic...")
        if subprocess.run([sys.executable, "-m", "pip", "install", "-q", "anthropic"]).returncode != 0:
            print("Nao consegui instalar. Rode: pip install -r requirements.txt")
            return 1
    print("\nPronto! Agora feche o backend (Ctrl+C) e rode de novo:  python app.py")
    return 0


if __name__ == "__main__":
    code = main()
    input("\nAperte Enter para fechar.")
    sys.exit(code)
