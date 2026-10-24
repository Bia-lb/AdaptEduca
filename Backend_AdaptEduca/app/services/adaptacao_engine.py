"""Motor de adaptação de conteúdo (RF07, RF08, RF09, RF10, RF13, RF14).

Funciona sem serviços externos: usa processamento de texto em português
(frequência de termos, pontuação de frases e regras de reescrita). Cada função
recebe o texto original e devolve uma estrutura JSON pronta para o frontend.
"""
import math
import re
from collections import Counter
from typing import Dict, List

MAX_CARACTERES = 50_000

_STOPWORDS = set("""
a o as os um uma uns umas de do da dos das em no na nos nas por para pra com sem sob sobre entre ate
e ou mas que se como quando onde porque pois porem contudo todavia entretanto logo assim entao
eu tu ele ela nos vos eles elas me te lhe lhes meu minha seu sua nosso nossa este esta isto esse essa isso
aquele aquela aquilo ao aos à às pelo pela pelos pelas num numa nuns numas dum duma
ser sou e eh somos sao era eram foi foram sera serao seja sejam sendo sido estar esta estao estava
estive esteve estamos ter tem tinha tinham teve tenho temos haver ha havia houve
ja ainda tambem so apenas muito muita muitos muitas pouco pouca mais menos tao tanto tanta cada todo toda todos todas
outro outra outros outras mesmo mesma qual quais quem cujo cuja isso nao sim ate depois antes durante
pode podem podia poder deve devem dever faz fazem fazer feito fazendo ser vez vezes
""".split())

_CONECTIVOS = {
    "entretanto": "mas", "contudo": "mas", "todavia": "mas", "no entanto": "mas",
    "portanto": "então", "logo": "então", "ademais": "além disso", "outrossim": "além disso",
    "porquanto": "porque", "visto que": "porque", "uma vez que": "porque", "haja vista": "porque",
    "a fim de": "para", "dessa forma": "assim", "desse modo": "assim", "de modo que": "então",
    "bem como": "e também", "mediante": "por meio de", "ao passo que": "enquanto",
    "não obstante": "mesmo assim", "destarte": "assim", "outrossim,": "além disso,",
    "dado que": "porque", "tendo em vista que": "porque", "em virtude de": "por causa de",
    "a despeito de": "apesar de", "acerca de": "sobre", "utilizar": "usar", "utiliza": "usa",
    "utilizam": "usam", "denominado": "chamado", "denominada": "chamada", "diversos": "vários",
    "inúmeros": "muitos", "adquirir": "obter", "primordial": "principal", "fundamental": "muito importante",
}

_EXPRESSOES = {
    "chover no molhado": "repetir algo que todos já sabem",
    "quebrar a cabeça": "pensar muito para resolver um problema",
    "pisar na bola": "errar ou decepcionar alguém",
    "matar dois coelhos": "resolver dois problemas de uma vez",
    "de olho": "prestando atenção",
    "dar a volta por cima": "superar uma dificuldade",
    "custar os olhos da cara": "ser muito caro",
    "estar com a corda no pescoço": "estar em grande dificuldade",
    "pagar o pato": "receber a culpa por algo que não fez",
    "pé de chumbo": "que dirige muito rápido",
    "dar um branco": "esquecer de repente",
    "abrir o jogo": "falar a verdade com clareza",
    "ficar de braços cruzados": "não fazer nada para ajudar",
    "tirar o cavalo da chuva": "desistir de uma ideia",
    "uma faca de dois gumes": "algo que tem lado bom e lado ruim",
    "bater o martelo": "tomar uma decisão final",
    "engolir sapo": "aceitar algo ruim sem reclamar",
    "meter o bedelho": "dar opinião onde não foi chamado",
}


def _norm(palavra: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", palavra.lower()) if unicodedata.category(c) != "Mn")


def limpar(texto: str) -> str:
    texto = (texto or "").replace("\r", "\n").replace(" ", " ")
    texto = re.sub(r"-\n(?=[a-zà-ú])", "", texto)           # palavras hifenizadas em PDF
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def validar(texto: str) -> str:
    texto = limpar(texto)
    if len(texto) < 40:
        raise ValueError("Texto muito curto. Envie ao menos algumas frases.")
    if len(texto) > MAX_CARACTERES:
        raise ValueError(f"Texto muito longo (máximo {MAX_CARACTERES} caracteres).")
    return texto


def frases(texto: str) -> List[str]:
    texto = limpar(texto)
    # quebra em fim de frase; linhas curtas sem pontuação (títulos) viram frase própria
    pedacos: List[str] = []
    for linha in texto.split("\n"):
        linha = linha.strip()
        if not linha:
            continue
        partes = re.split(r"(?<=[.!?…])\s+(?=[A-ZÀ-Ú0-9\"“(])", linha)
        pedacos.extend(p.strip() for p in partes if p.strip())
    return pedacos


def _palavras(frase: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\-]{2,}", frase)


def _pontuacao_termos(texto: str) -> Counter:
    contagem: Counter = Counter()
    for p in _palavras(texto):
        n = _norm(p)
        if n not in _STOPWORDS and len(n) > 3:
            contagem[n] += 1
    return contagem


def _forma_exibicao(texto: str) -> Dict[str, str]:
    """Para cada termo normalizado, a forma mais frequente como aparece no texto."""
    formas: Dict[str, Counter] = {}
    for p in _palavras(texto):
        formas.setdefault(_norm(p), Counter())[p.lower()] += 1
    return {k: v.most_common(1)[0][0] for k, v in formas.items()}


def palavras_chave(texto: str, n: int = 8) -> List[str]:
    contagem = _pontuacao_termos(texto)
    exibicao = _forma_exibicao(texto)
    return [exibicao[t] for t, _ in contagem.most_common(n)]


def _pontuar_frases(lista: List[str], texto: str) -> List[float]:
    termos = _pontuacao_termos(texto)
    pontos = []
    for i, f in enumerate(lista):
        ps = [_norm(p) for p in _palavras(f)]
        base = sum(termos.get(p, 0) for p in set(ps))
        score = base / math.sqrt(max(len(ps), 1))
        if i == 0:
            score *= 1.3
        if len(ps) < 4:
            score *= 0.4
        pontos.append(score)
    return pontos


def _selecionar(lista: List[str], texto: str, k: int) -> List[str]:
    pontos = _pontuar_frases(lista, texto)
    melhores = sorted(range(len(lista)), key=lambda i: pontos[i], reverse=True)[:k]
    return [lista[i] for i in sorted(melhores)]


def _simplificar_frase(frase: str) -> List[str]:
    for original, simples in sorted(_CONECTIVOS.items(), key=lambda kv: -len(kv[0])):
        frase = re.sub(rf"\b{re.escape(original)}\b", simples, frase, flags=re.IGNORECASE)
    frase = re.sub(r"\s*\([^)]{0,80}\)", "", frase)          # remove parênteses curtos
    frase = re.sub(r"\s+", " ", frase).strip()
    if len(frase.split()) <= 20:
        return [frase]
    # frases longas: quebra em ";" ou em vírgula antes de conjunção/relativo
    partes = re.split(r";\s+|,\s+(?=(?:mas|e|pois|porque|então|enquanto)\b)", frase)
    partes = [p.strip(" ,") for p in partes if len(p.strip(" ,")) > 0]
    saida: List[str] = []
    for p in partes:
        if saida and len(p.split()) < 4:
            saida[-1] += ", " + p
        else:
            saida.append(p)
    return saida or [frase]


def _com_ponto(frase: str) -> str:
    frase = re.sub(r"^(mas|então|assim|porém),\s+", r"\1 ", frase.strip(), flags=re.IGNORECASE)
    frase = frase[0].upper() + frase[1:] if frase else frase
    return frase if re.search(r"[.!?…:]$", frase) else frase + "."


# ── modos de adaptação ──────────────────────────────────────────────────────
def resumo(texto: str) -> dict:
    """RF08: resumo extrativo com as frases mais relevantes, na ordem original."""
    texto = validar(texto)
    lista = frases(texto)
    k = min(max(2, math.ceil(len(lista) * 0.3)), 6, len(lista))
    pontos = [_com_ponto(f) for f in _selecionar(lista, texto, k)]
    chave = palavras_chave(texto, 6)
    return {
        "modo": "Resumo", "pontos": pontos, "palavrasChave": chave,
        "reducao": f"{len(' '.join(pontos).split())} de {len(texto.split())} palavras",
    }


def simplificado(texto: str) -> dict:
    """Texto com frases curtas e vocabulário mais simples."""
    texto = validar(texto)
    paragrafos = []
    for bloco in re.split(r"\n\s*\n", texto):
        saida: List[str] = []
        for f in frases(bloco):
            saida.extend(_com_ponto(p) for p in _simplificar_frase(f))
        if saida:
            paragrafos.append(" ".join(saida))
    return {"modo": "Texto simplificado", "paragrafos": paragrafos, "palavrasChave": palavras_chave(texto, 6)}


def tdah(texto: str) -> dict:
    """RF07 (TDAH): blocos curtos, destaque dos termos-chave, tempo e checkpoint."""
    texto = validar(texto)
    simples = [s for f in frases(texto) for s in _simplificar_frase(f)]
    chave = palavras_chave(texto, 12)
    blocos = []
    for i in range(0, len(simples), 3):
        grupo = [_com_ponto(s) for s in simples[i:i + 3]]
        ref = " ".join(grupo)
        destaques = [k for k in chave if _norm(k) in _norm(ref)][:3]
        tema = destaques[0] if destaques else (palavras_chave(ref, 1) or ["ideia"])[0]
        palavras = len(ref.split())
        blocos.append({
            "titulo": f"Parte {len(blocos) + 1} · {tema.capitalize()}",
            "itens": grupo, "destaques": destaques,
            "minutos": max(1, round(palavras / 180)),
            "checkpoint": f"Pausa rápida: explique com suas palavras o que você leu sobre “{tema}”.",
        })
    return {"modo": "TDAH", "blocos": blocos, "totalBlocos": len(blocos),
            "tempoTotal": max(1, round(len(texto.split()) / 180)),
            "dica": "Leia um bloco por vez e respire antes do próximo."}


def tea(texto: str) -> dict:
    """RF07 (TEA): estrutura previsível, linguagem literal e glossário."""
    texto = validar(texto)
    simples = [_com_ponto(s) for f in frases(texto) for s in _simplificar_frase(f)]
    chave = palavras_chave(texto, 8)
    baixo = texto.lower()
    expressoes = [{"expressao": e, "significado": m} for e, m in _EXPRESSOES.items() if e in baixo]
    visao = f"Este texto fala sobre: {', '.join(chave[:3])}." if chave else "Este texto apresenta informações."
    glossario = []
    for termo in chave[:6]:
        exemplo = next((s for s in simples if termo in s.lower()), None)
        if exemplo:
            glossario.append({"termo": termo, "exemplo": exemplo})
    return {
        "modo": "TEA", "visaoGeral": visao,
        "estrutura": f"Este texto tem {len(simples)} ideias. Cada ideia está em uma linha numerada.",
        "passos": simples, "glossario": glossario, "expressoes": expressoes,
        "aviso": "Todas as frases foram escritas de forma direta. Quando houver uma expressão figurada, ela é explicada abaixo.",
    }


def mapa_mental(texto: str) -> dict:
    """RF10: mapa mental com tema central e ramos baseados nos termos mais relevantes."""
    texto = validar(texto)
    lista = frases(texto)
    chave = palavras_chave(texto, 12)
    centro = " ".join(chave[:2]).title() if chave else "Tema central"
    ramos, usadas = [], set()
    for termo in chave[2:] or chave:
        if len(ramos) >= 6:
            break
        candidatas = [f for f in lista if _norm(termo) in _norm(f) and f not in usadas]
        if not candidatas:
            continue
        filhos = []
        for f in candidatas[:3]:
            usadas.add(f)
            curto = " ".join(f.split()[:9]).rstrip(".,;:") + ("…" if len(f.split()) > 9 else "")
            filhos.append(curto)
        ramos.append({"titulo": termo.capitalize(), "filhos": filhos})
    if not ramos:
        ramos = [{"titulo": "Ideias", "filhos": [" ".join(f.split()[:9]) for f in lista[:4]]}]
    return {"modo": "Mapa mental", "centro": centro, "ramos": ramos}


def audio(texto: str) -> dict:
    """RF09: segmentos prontos para síntese de voz (pt-BR) no navegador."""
    texto = validar(texto)
    segmentos, atual = [], ""
    for f in frases(texto):
        if atual and len(atual) + len(f) > 240:
            segmentos.append(atual)
            atual = ""
        atual = (atual + " " + f).strip()
    if atual:
        segmentos.append(atual)
    palavras = len(texto.split())
    return {"modo": "Audio", "lang": "pt-BR", "segmentos": segmentos,
            "palavras": palavras, "duracaoSegundos": round(palavras / 2.6)}


def flashcards(texto: str) -> dict:
    """RF14 (modo revisão): cartões pergunta/resposta por termo-chave."""
    texto = validar(texto)
    lista = frases(texto)
    cartoes, usadas = [], set()
    for termo in palavras_chave(texto, 12):
        f = next((x for x in lista if _norm(termo) in _norm(x) and x not in usadas and len(x.split()) >= 5), None)
        if f:
            usadas.add(f)
            cartoes.append({"frente": f"O que o texto diz sobre “{termo}”?", "verso": _com_ponto(f)})
        if len(cartoes) >= 8:
            break
    return {"modo": "Flashcards", "cartoes": cartoes}


MODOS = {
    "resumo": ("Resumo", resumo), "simplificado": ("Texto simplificado", simplificado),
    "tdah": ("TDAH", tdah), "tea": ("TEA", tea), "mapa": ("Mapa mental", mapa_mental),
    "audio": ("Audio", audio), "flashcards": ("Flashcards", flashcards),
}


def gerar(modo: str, texto: str) -> dict:
    if modo not in MODOS:
        raise ValueError(f"Modo inválido. Use: {', '.join(MODOS)}.")
    return MODOS[modo][1](texto)


# ── personalização (RF13) e modos de estudo (RF14) ──────────────────────────
def modo_recomendado(questionario: dict) -> str:
    necessidades = questionario.get("necessidades") or []
    formatos = questionario.get("formats") or []
    if "TDAH" in necessidades:
        return "tdah"
    if "TEA" in necessidades:
        return "tea"
    if "Dislexia" in necessidades or "Baixa visão" in necessidades:
        return "audio"
    if "Mapas Mentais" in formatos:
        return "mapa"
    if "Áudios" in formatos:
        return "audio"
    if "Resumos" in formatos:
        return "resumo"
    if "Flashcards" in formatos:
        return "flashcards"
    return "simplificado"


_MINUTOS_FOCO = {"Menos de 15 minutos": 10, "15 a 30 minutos": 20, "30 a 60 minutos": 30, "Mais de 1 hora": 45}


def modos_de_estudo(questionario: dict) -> dict:
    foco = _MINUTOS_FOCO.get(questionario.get("concentracao"), 25)
    return {
        "recomendado": modo_recomendado(questionario),
        "modos": [
            {"id": "leitura", "nome": "Leitura", "descricao": "Lê o conteúdo adaptado no seu ritmo."},
            {"id": "foco", "nome": "Foco", "descricao": f"Um bloco por vez com temporizador de {foco} min e pausas.",
             "minutosFoco": foco, "minutosPausa": 5 if foco <= 20 else 10},
            {"id": "revisao", "nome": "Revisão", "descricao": "Flashcards com os pontos principais."},
            {"id": "audio", "nome": "Áudio", "descricao": "Ouça o conteúdo narrado."},
        ],
        "horarioPreferido": questionario.get("horario"),
    }
