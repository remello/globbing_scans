class GlobbingException(Exception):
    """Базовое исключение для всех ошибок в библиотеке"""
    pass

class AuthenticationError(GlobbingException):
    """Ошибка аутентификации"""
    pass

class CaptchaError(AuthenticationError):
    """Ошибка при работе с reCAPTCHA"""
    pass

class RequestError(GlobbingException):
    """Ошибка при выполнении HTTP запроса"""
    pass

class SessionError(GlobbingException):
    """Ошибка при работе с сессией"""
    pass
