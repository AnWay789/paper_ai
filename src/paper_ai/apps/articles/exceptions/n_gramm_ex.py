class NGrammException(Exception):
    """Ошибка при работе с n-граммами"""
    pass

class MinNGrammsLengthException(Exception):
    """N-грамма не может быть короче {self.min_length} символов"""
    pass

class MaxNGrammsLengthException(Exception):
    """N-грамма не может быть длиннее {self.max_length} символов"""
    pass

class MinNGrammsCountException(Exception):
    """Количество n-грамм не может быть меньше {self.min_count}"""
    pass

class MaxNGrammsCountException(Exception):
    """Количество n-грамм не может быть больше {self.max_count}"""
    pass
