class StatusChangeException(Exception):
    """Ошибка при изменении статуса"""
    pass

class InvalidStatusException(Exception):
    """Неизвестный статус"""
    pass

class InvalidStatusChangeException(Exception):
    """Недопустимый переход из статуса {self.status} в статус {status}"""
    pass
