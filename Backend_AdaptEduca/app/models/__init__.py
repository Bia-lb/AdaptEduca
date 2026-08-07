# Expõe todos os modelos para uso externo
from .usuario import Usuario
from .aluno import Aluno
from .professor import Professor
from .responsavel import Responsavel
from .turma import Turma
from .conteudo import Conteudo
from .atividade import Atividade
from .adaptacao import Adaptacao
from .feedback import Feedback
from .relatorio import Relatorio

__all__ = [
    "Usuario", "Aluno", "Professor", "Responsavel",
    "Turma", "Conteudo", "Atividade",
    "Adaptacao", "Feedback", "Relatorio",
]
