class ArticleProjectException(Exception):
    """Ошибка при работе с проектом статьи"""
    pass

class ArticleProjectAlredyInProgressException(Exception):
    """Проект статьи уже в процессе"""
    pass

