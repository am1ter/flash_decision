from starlette import status


class BaseError(Exception):
    msg: str

    def __init__(self, *args: object) -> None:
        super().__init__(self.msg, *args)


class BaseHTTPError(BaseError):
    status_code: int


class BaseValidationError(BaseError):
    pass


class UserNotFoundError(BaseHTTPError):
    msg = "The user you are trying to access could not be found."
    status_code = status.HTTP_404_NOT_FOUND


class UserDisabledError(BaseHTTPError):
    msg = "This user account has been disabled. Please contact the administrator for assistance."
    status_code = status.HTTP_403_FORBIDDEN


class WrongPasswordError(BaseHTTPError):
    msg = "The password you entered is incorrect. Please double-check your input and try again."
    status_code = status.HTTP_403_FORBIDDEN


class DbConnectionError(BaseHTTPError):
    msg = "The connection to the database could not be established."
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class DbObjectNotFoundError(BaseHTTPError):
    msg = "This object could not be found in the database."
    status_code = status.HTTP_404_NOT_FOUND


class DbObjectDuplicateError(BaseHTTPError):
    msg = "This object could not be saved in the database, because such an object already exists."
    status_code = status.HTTP_404_NOT_FOUND


class ConfigHTTPInconsistentError(BaseValidationError):
    msg = "BACKEND_HOST and BACKEND_URL are inconsistent"


class ConfigHTTPWrongURLError(BaseValidationError):
    msg = "BACKEND_URL has wrong format"
