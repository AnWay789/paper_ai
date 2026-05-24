class ArticlePaperException(Exception):
    pass

class ArticlePaperNotFound(ArticlePaperException):
    pass

class ArticlePaperAlreadyExists(ArticlePaperException):
    pass

class ArticlePaperDoesNotExist(ArticlePaperException):
    pass

class ArticlePaperTitleDoesNotExist(ArticlePaperException):
    pass

class ArticlePaperIntroductionDoesNotExist(ArticlePaperException):
    pass

class ArticlePaperChaptersNameDoesNotExist(ArticlePaperException):
    pass

class ArticlePaperChaptersContentDoesNotExist(ArticlePaperException):
    pass

class ArticlePaperFinalArticleDoesNotExist(ArticlePaperException):
    pass
