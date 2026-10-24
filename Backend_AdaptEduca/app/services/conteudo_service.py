import json
import os
import re
import uuid
from datetime import date
from io import BytesIO
from typing import List, Optional

from flask import current_app
from werkzeug.utils import secure_filename

from app import db
from app.models.adaptacao import Adaptacao
from app.models.aluno import Aluno
from app.models.conteudo import Conteudo
from app.models.turma import Turma
from app.services import adaptacao_engine as motor
from app.services import ia_adaptacao
from app.services.turma_service import TurmaService

TIPOS = ("Texto", "PDF", "Link", "Video")
MAX_PDF = 10 * 1024 * 1024


def extrair_texto_pdf(dados: bytes) -> str:
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError
    if not dados.startswith(b"%PDF"):
        raise ValueError("O arquivo enviado não é um PDF válido.")
    try:
        leitor = PdfReader(BytesIO(dados))
        if leitor.is_encrypted:
            raise ValueError("O PDF está protegido por senha.")
        texto = "\n\n".join((pagina.extract_text() or "") for pagina in leitor.pages)
    except (PdfReadError, KeyError, ValueError) as exc:
        if isinstance(exc, ValueError) and "senha" in str(exc):
            raise
        raise ValueError("Não foi possível ler o PDF.")
    texto = motor.limpar(texto)
    if len(texto) < 40:
        raise ValueError("Não foi possível extrair texto do PDF (pode ser um PDF escaneado como imagem).")
    return texto


class ConteudoService:
    def __init__(self) -> None:
        self._turmas = TurmaService()

    def listar_para(self, usuario_id: int, perfil: str) -> List[dict]:
        turmas = self._turmas.listar_para(usuario_id, perfil)
        nomes = {t.id: t.nome for t in turmas}
        if not nomes:
            return []
        itens = (Conteudo.query.filter(Conteudo.turma_id.in_(nomes))
                 .order_by(Conteudo.dataPostagem.desc(), Conteudo.id.desc()).all())
        saida = []
        for c in itens:
            d = c.to_dict()
            d["turmaNome"] = nomes[c.turma_id]
            d["temTexto"] = bool(c.texto)
            saida.append(d)
        return saida

    def buscar_visivel(self, id: int, usuario_id: int, perfil: str) -> Optional[Conteudo]:
        c = db.session.get(Conteudo, id)
        if c and self._turmas.tem_acesso(c.turma, usuario_id, perfil):
            return c
        return None

    def criar(self, dados: dict, arquivo, professor_id: int) -> Conteudo:
        try:
            turma = db.session.get(Turma, int(dados.get("turma_id")))
        except (TypeError, ValueError):
            turma = None
        if not turma or turma.professor_id != professor_id:
            raise PermissionError("Você só pode publicar conteúdo nas suas turmas.")
        titulo = (dados.get("titulo") or "").strip()
        tipo = dados.get("tipo") or ("PDF" if arquivo else "Texto")
        if not titulo:
            raise ValueError("O título é obrigatório.")
        if tipo not in TIPOS:
            raise ValueError(f"Tipo inválido. Use: {', '.join(TIPOS)}.")

        texto, nome_arquivo, original = None, None, None
        if tipo == "PDF":
            if not arquivo:
                raise ValueError("Envie o arquivo PDF.")
            conteudo_bytes = arquivo.read(MAX_PDF + 1)
            if len(conteudo_bytes) > MAX_PDF:
                raise ValueError("O PDF deve ter no máximo 10 MB.")
            texto = extrair_texto_pdf(conteudo_bytes)
            pasta = current_app.config["UPLOAD_DIR"]
            os.makedirs(pasta, exist_ok=True)
            nome_arquivo = f"{uuid.uuid4().hex}.pdf"
            with open(os.path.join(pasta, nome_arquivo), "wb") as f:
                f.write(conteudo_bytes)
            original = secure_filename(arquivo.filename or "conteudo.pdf")[:255]
        elif tipo == "Texto":
            texto = motor.limpar(dados.get("texto") or "")
            if len(texto) < 40:
                raise ValueError("Digite o texto do conteúdo (mínimo de 40 caracteres).")
        else:  # Link / Video
            nome_arquivo = (dados.get("arquivo") or "").strip()
            if not re.match(r"^https?://", nome_arquivo):
                raise ValueError("Informe um link começando com http:// ou https://.")
            texto = motor.limpar(dados.get("texto") or "") or None

        conteudo = Conteudo(titulo=titulo, tipo=tipo, arquivo=nome_arquivo, arquivoOriginal=original,
                            texto=texto, dataPostagem=date.today(), turma_id=turma.id)
        db.session.add(conteudo)
        db.session.commit()
        return conteudo

    def caminho_pdf(self, conteudo: Conteudo) -> Optional[str]:
        if conteudo.tipo != "PDF" or not conteudo.arquivo:
            return None
        caminho = os.path.join(current_app.config["UPLOAD_DIR"], os.path.basename(conteudo.arquivo))
        return caminho if os.path.exists(caminho) else None

    def deletar(self, conteudo: Conteudo) -> None:
        caminho = self.caminho_pdf(conteudo)
        for a in list(conteudo.adaptacoes):
            db.session.delete(a)
        db.session.delete(conteudo)
        db.session.commit()
        if caminho:
            try:
                os.remove(caminho)
            except OSError:
                pass

    # ── adaptação (RF07/08/09/10/13) ────────────────────────────────────────
    def adaptar(self, conteudo: Conteudo, modo: str, aluno: Optional[Aluno] = None,
               usuario_id: Optional[int] = None) -> dict:
        recomendado = False
        if modo in ("para-mim", "", None):
            quest = aluno.respostas_questionario() if aluno else {}
            modo, recomendado = motor.modo_recomendado(quest), True
        if modo not in motor.MODOS:
            raise ValueError(f"Modo inválido. Use: {', '.join(motor.MODOS)}.")
        if not conteudo.texto:
            raise ValueError("Este conteúdo não tem texto para adaptar (é apenas um link).")
        rotulo = motor.MODOS[modo][0]
        salvo = Adaptacao.query.filter_by(conteudo_id=conteudo.id, modo=rotulo).first()
        resultado = json.loads(salvo.resultado) if salvo and salvo.resultado else None
        # Cache compartilhado: um resultado gerado por regras é refeito com IA quando ela estiver disponível.
        melhorar = (resultado is not None and resultado.get("fonte") != "ia"
                    and ia_adaptacao.pode_usar(modo, conteudo.texto))
        if resultado is None or melhorar:
            resultado = ia_adaptacao.adaptar_com_fallback(usuario_id, modo, conteudo.texto)
            texto_json = json.dumps(resultado, ensure_ascii=False)
            if salvo:
                salvo.resultado = texto_json
            else:
                db.session.add(Adaptacao(
                    conteudo_id=conteudo.id, modo=rotulo, resultado=texto_json,
                    audio=(modo == "audio"), mapaMental=(modo == "mapa")))
            db.session.commit()
        return {"conteudo_id": conteudo.id, "modo": modo, "recomendado": recomendado, "resultado": resultado}
