"""
Жизненный цикл новости.
Валидация переходов между статусами.
"""
from database.models.news import NewsStatus


class InvalidTransitionError(Exception):
    """Ошибка недопустимого перехода."""
    pass


class NotFoundError(Exception):
    """Сущность не найдена."""
    pass


class NewsLifecycle:
    """
    Логика жизненного цикла новости.
    Разрешённые переходы заданы явно.
    """

    ALLOWED_TRANSITIONS = {
        NewsStatus.CREATED: [NewsStatus.ACTIVE],
        NewsStatus.ACTIVE: [NewsStatus.COMPLETED, NewsStatus.CANCELLED],
        NewsStatus.COMPLETED: [],   # тупик
        NewsStatus.CANCELLED: [],   # тупик
    }

    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        """Проверяет, разрешён ли переход."""
        allowed = cls.ALLOWED_TRANSITIONS.get(from_status, [])
        return to_status in allowed

    @classmethod
    def validate_transition(cls, from_status: str, to_status: str):
        """
        Валидирует переход.
        Бросает InvalidTransitionError, если переход запрещён.
        """
        if not cls.can_transition(from_status, to_status):
            raise InvalidTransitionError(
                f"Переход {from_status} → {to_status} запрещён. "
                f"Разрешённые: {cls.ALLOWED_TRANSITIONS.get(from_status, [])}"
            )