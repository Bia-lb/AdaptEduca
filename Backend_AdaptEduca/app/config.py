import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "adapteduca-dev-key")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5500")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads"))
    MAX_CONTENT_LENGTH = 12 * 1024 * 1024  # PDFs de até ~10 MB
    RESET_TOKEN_MAX_AGE = 60 * 60          # link de recuperação vale 1 hora
    MAIL_HOST = os.getenv("MAIL_HOST", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USER = os.getenv("MAIL_USER", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM = os.getenv("MAIL_FROM", "AdaptEduca <nao-responda@adapteduca.local>")
    TOKEN_MAX_AGE = int(os.getenv("TOKEN_MAX_AGE", str(60 * 60 * 12)))  # 12h
    # Agentes de IA (Anthropic). A chave fica SOMENTE no servidor.
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    IA_LIMITE_DIARIO = int(os.getenv("IA_LIMITE_DIARIO", "40"))   # chamadas por usuário/dia
    IA_TIMEOUT = float(os.getenv("IA_TIMEOUT", "40"))             # segundos
    IA_MAX_CARACTERES_CONTEUDO = int(os.getenv("IA_MAX_CARACTERES_CONTEUDO", "12000"))
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "adapteduca")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:"
        f"{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    DEBUG = False

    @classmethod
    def validar(cls):
        if cls.SECRET_KEY == "adapteduca-dev-key":
            raise RuntimeError("Defina SECRET_KEY no ambiente para usar em produção.")


class TestingConfig(Config):
    TESTING = True
    UPLOAD_DIR = os.path.join(os.getenv("TMPDIR", "/tmp"), "adapteduca-test-uploads")
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ANTHROPIC_API_KEY = ""  # testes nunca chamam a API real


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
