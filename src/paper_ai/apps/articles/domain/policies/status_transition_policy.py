from ..value_objects.project_statuses import ProjectStatus
from ..value_objects.generation_step import GENERATION_STEPS

_RESTARTABLE_STATUSES = frozenset({
    ProjectStatus.COMPLETED,
    ProjectStatus.CANCELLED,
    ProjectStatus.ERROR,
})

_STARTABLE_STATUSES = frozenset({
    ProjectStatus.NEW,
    ProjectStatus.NOT_STARTED,
}) | _RESTARTABLE_STATUSES


def build_allowed_status_transitions() -> dict[ProjectStatus | None, list[ProjectStatus]]:
    transitions: dict[ProjectStatus | None, list[ProjectStatus]] = {
        None: [ProjectStatus.NEW],
        ProjectStatus.NOT_STARTED: [
            ProjectStatus.GENERATE_TITLE,
            ProjectStatus.CANCELLED,
            ProjectStatus.ERROR,
        ],
        ProjectStatus.NEW: [
            ProjectStatus.GENERATE_TITLE,
            ProjectStatus.CANCELLED,
            ProjectStatus.ERROR,
        ],
        ProjectStatus.STARTED: [
            ProjectStatus.GENERATE_TITLE,
            ProjectStatus.CANCELLED,
            ProjectStatus.ERROR,
        ],
    }

    for status, step in GENERATION_STEPS.items():
        transitions[status] = [
            step.next_status,
            ProjectStatus.CANCELLED,
            ProjectStatus.ERROR,
        ]

    for status in _RESTARTABLE_STATUSES:
        transitions[status] = [
            ProjectStatus.GENERATE_TITLE,
            ProjectStatus.CANCELLED,
            ProjectStatus.ERROR,
        ]

    return transitions


ALLOWED_STATUS_TRANSITIONS = build_allowed_status_transitions()


def can_start_generation(status: ProjectStatus) -> bool:
    return status in _STARTABLE_STATUSES
