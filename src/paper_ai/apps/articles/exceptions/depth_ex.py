class DepthException(Exception):
    """Ошибка при работе с глубиной"""
    pass

class MinDepthLengthException(Exception):
    """Глубина не может быть короче {self.min_length} символов"""
    pass

class MaxDepthLengthException(Exception):
    """Глубина не может быть длиннее {self.max_length} символов"""
    pass
