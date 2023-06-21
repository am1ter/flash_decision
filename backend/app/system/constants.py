from enum import Enum


class Environment(Enum):
    development = "development"
    production = "production"
    test = "test"


class UserStatus(Enum):
    active = "active"
    disabled = "disabled"


class AuthStatus(Enum):
    sign_up = "sign_up"
    sign_in = "sign_in"
    wrong_password = "wrong_password"  # noqa: S105
