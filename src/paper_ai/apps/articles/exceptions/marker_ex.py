class EmptyMarkerException(Exception):
    """Маркер не может быть пустым"""
    pass

class MaxMarkerLengthException(Exception):
    """Маркер не может быть длиннее {self.max_length} символов"""
    pass

class MinMarkerLengthException(Exception):
    """Маркер не может быть короче {self.min_length} символов"""
    pass

class MarkerAlreadySetException(Exception):
    """Маркер уже установлен"""
    pass
