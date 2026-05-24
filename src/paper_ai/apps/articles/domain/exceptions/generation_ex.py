class GenerationException(Exception):
    """Ошибка при выполнении шага генерации"""
    pass


class InvalidGenerationStepException(GenerationException):
    """Статус не является шагом генерации с ответом LLM"""
    pass


class InvalidGenerationResponseException(GenerationException):
    """Ответ LLM не соответствует ожидаемому типу для шага генерации"""
    pass
