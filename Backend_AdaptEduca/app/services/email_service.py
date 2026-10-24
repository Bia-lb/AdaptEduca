"""Envio de e-mail. Sem MAIL_HOST configurado, o e-mail vai para o log do servidor
(útil em desenvolvimento) e fica em app.extensions["outbox"] (usado nos testes)."""
import logging
import smtplib
from email.message import EmailMessage

from flask import current_app

log = logging.getLogger("adapteduca.email")


def enviar(destino: str, assunto: str, corpo: str) -> None:
    cfg = current_app.config
    if not cfg.get("MAIL_HOST"):
        current_app.extensions.setdefault("outbox", []).append(
            {"para": destino, "assunto": assunto, "corpo": corpo})
        log.warning("E-mail (SMTP não configurado) para %s: %s\n%s", destino, assunto, corpo)
        print(f"\n[E-MAIL SIMULADO] Para: {destino}\nAssunto: {assunto}\n{corpo}\n")
        return
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = cfg["MAIL_FROM"], destino, assunto
    msg.set_content(corpo)
    with smtplib.SMTP(cfg["MAIL_HOST"], cfg["MAIL_PORT"], timeout=15) as smtp:
        smtp.starttls()
        if cfg.get("MAIL_USER"):
            smtp.login(cfg["MAIL_USER"], cfg["MAIL_PASSWORD"])
        smtp.send_message(msg)
