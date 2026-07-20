from controllers.crud_controller import criar_blueprint
from services.feedback_service import feedback_service

feedback_bp = criar_blueprint("feedbacks", feedback_service)
