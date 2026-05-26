class WidthException(Exception):
    """Ошибка при работе с шириной статьи"""
    pass

class MinWidthLengthException(Exception):
    """Ширина статьи не может быть короче {self.min_length} символов"""
    pass

class MaxWidthLengthException(Exception):
    """Ширина статьи не может быть длиннее {self.max_length} символов"""
    pass
