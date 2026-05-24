class KeywordException(Exception):
    """Ошибка при работе с ключевыми словами"""
    pass

class MinKeywordLengthException(Exception):
    """Ключевое слово не может быть короче {self.min_length} символов"""
    pass

class MaxKeywordLengthException(Exception):
    """Ключевое слово не может быть длиннее {self.max_length} символов"""
    pass

class MinKeywordCountException(Exception):
    """Количество ключевых слов не может быть меньше {self.min_count}"""
    pass

class MaxKeywordCountException(Exception):
    """Количество ключевых слов не может быть больше {self.max_count}"""
    pass
