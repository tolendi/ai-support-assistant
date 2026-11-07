from app.schemas.classification import TicketStatus


ALLOWED_STATUS_TRANSITIONS = {
    TicketStatus.NEW: {
        TicketStatus.IN_PROGRESS,
    },
    TicketStatus.IN_PROGRESS: {
        TicketStatus.RESOLVED,
    },
    TicketStatus.RESOLVED: {
        TicketStatus.CLOSED,
        TicketStatus.IN_PROGRESS,
    },
    TicketStatus.CLOSED: set(),
}


def is_status_transition_allowed(
    current_status: TicketStatus,
    new_status: TicketStatus,
) -> bool:
    allowed_statuses = ALLOWED_STATUS_TRANSITIONS[current_status]

    return new_status in allowed_statuses