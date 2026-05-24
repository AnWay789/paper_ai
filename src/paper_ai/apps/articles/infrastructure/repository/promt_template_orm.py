from ...aplication.adapters.promt_template_rep import PromtTemplateRepository
from ..orm.promts import PromtTemplateORM
from ...domain.value_objects.project_statuses import ProjectStatus

class PromtTemplateORMRepository(PromtTemplateRepository):
    def get_template_by_status(self, status: ProjectStatus) -> str:
        return PromtTemplateORM.objects.get(status=status.value).template
