from ninja import NinjaAPI

from ...domain.exceptions.generation_ex import GenerationException
from ...domain.exceptions.status_ex import InvalidStatusChangeException
from .routes.projects import projects_router

paper_ai_api = NinjaAPI(title="paper_ai", version="1.0.0")

paper_ai_api.add_router("/projects", projects_router)


@paper_ai_api.exception_handler(InvalidStatusChangeException)
def invalid_status_change(request, exc: InvalidStatusChangeException):
    return paper_ai_api.create_response(request, {"detail": str(exc)}, status=400)


@paper_ai_api.exception_handler(GenerationException)
def generation_error(request, exc: GenerationException):
    return paper_ai_api.create_response(request, {"detail": str(exc)}, status=400)
