from starlette import status


class BaseHTTPError(Exception):
    msg: str
    status_code: int


class UserNotFoundError(BaseHTTPError):
    msg = "The user you are trying to access could not be found."
    status_code = status.HTTP_404_NOT_FOUND


class UserDisabledError(BaseHTTPError):
    msg = "This user account has been disabled. Please contact the administrator for assistance."
    status_code = status.HTTP_403_FORBIDDEN


class WrongPasswordError(BaseHTTPError):
    msg = "The password you entered is incorrect. Please double-check your input and try again."
    status_code = status.HTTP_403_FORBIDDEN


class BaseValidationError(ValueError):
    msg: str

    def __init__(self, *args: object) -> None:
        super().__init__(self.msg, *args)


class ConfigHTTPInconsistentError(BaseValidationError):
    msg = "BACKEND_HOST and BACKEND_URL are inconsistent"


class ConfigHTTPWrongURLError(BaseValidationError):
    msg = "BACKEND_URL has wrong format"
