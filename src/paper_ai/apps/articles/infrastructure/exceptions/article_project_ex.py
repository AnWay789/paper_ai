class ArticleProjectException(Exception):
    pass
class ArticleProjectNotFoundException(ArticleProjectException):
    pass
class ArticleProjectAlreadyExistsException(ArticleProjectException):
    pass
class ArticleProjectInvalidException(ArticleProjectException):
    pass
class ArticleProjectValidationException(ArticleProjectException):
    pass

