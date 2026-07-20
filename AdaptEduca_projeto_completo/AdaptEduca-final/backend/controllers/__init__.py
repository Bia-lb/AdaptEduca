from controllers.usuario_controller import usuario_bp, auth_bp
from controllers.professor_controller import professor_bp
from controllers.aluno_controller import aluno_bp
from controllers.responsavel_controller import responsavel_bp
from controllers.turma_controller import turma_bp
from controllers.conteudo_controller import conteudo_bp
from controllers.atividade_controller import atividade_bp
from controllers.adaptacao_controller import adaptacao_bp
from controllers.feedback_controller import feedback_bp
from controllers.relatorio_controller import relatorio_bp

blueprints = [usuario_bp, auth_bp, professor_bp, aluno_bp, responsavel_bp, turma_bp, conteudo_bp, atividade_bp, adaptacao_bp, feedback_bp, relatorio_bp]
