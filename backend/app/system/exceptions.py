from starlette import status


class BaseError(Exception):
    msg: str

    def __init__(self, *args: object) -> None:
        super().__init__(self.msg, *args)


class BaseHTTPError(BaseError):
    status_code: int
    headers: dict | None = None


class BaseValidationError(BaseError):
    pass


class BaseHTTPValidationError(BaseHTTPError, BaseValidationError):
    status_code = status.HTTP_400_BAD_REQUEST


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


class DbObjectCannotBeCreatedError(BaseHTTPError):
    msg = "This object could not be saved in the database, because of the database constraints."
    status_code = status.HTTP_400_BAD_REQUEST


class JwtExpiredError(BaseHTTPError):
    msg = "Your session is expired. Please authenticate again."
    status_code = status.HTTP_401_UNAUTHORIZED
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidJwtError(BaseHTTPError):
    msg = "Your access token is invalid. Please authenticate again."
    status_code = status.HTTP_403_FORBIDDEN
    headers = {"WWW-Authenticate": "Bearer"}  # part of OAuth2 specification


class ProviderAccessError(BaseHTTPError):
    msg = "The external data provider responded with a wrong status code. Please try again later."
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class SessionConfigurationError(BaseHTTPError):
    msg = "The current session has invalid configuration options."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ProviderInvalidDataError(BaseHTTPError):
    msg = "The data received from the external data provider is invalid."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class UnsupportedModeError(BaseHTTPError):
    msg = "Specified mode is not yet supported yet"
    status_code = status.HTTP_501_NOT_IMPLEMENTED


class ConfigHTTPHardcodedBackendUrlError(BaseValidationError):
    msg = "Set `BACKEND_URL` in environment variables is not allowed. Please remove it."


class ConfigHTTPWrongURLError(BaseValidationError):
    msg = "Some of HTTP environment variables have wrong format."


class EmailValidationError(BaseHTTPValidationError):
    msg = "The email address you entered does not match the expected format."


class IpAddressValidationError(BaseHTTPValidationError):
    msg = "The http request has invalid IP address format."
