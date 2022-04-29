from enum import Enum
from pathlib import WindowsPath
from passlib.context import CryptContext
import pytz


LOCAL_TIME_ZONE = pytz.timezone("Asia/Yangon")
BasePath = WindowsPath("d:/c_channel_images")

class Product(Enum):
    ds = "Deck Sheet"
    c_purlin = "C Purlin"
    u_beam = "U Beam"
    i_beam = "I Beam"
    c_channel = "C Channel"
    hollow = "Hollow"
    plain = "Plain"
    roof = "Roof"

class ProductionStage(Enum):
    pending = 'pending'
    producing = 'producing'
    done = 'done'

class ColorPlainManufacturer(Enum):
    taiwan = "taiwan"
    china = "china"
    vietnam = "vietnam"


class Gender(Enum):
    male = "male"
    female = "female"


class TransType(Enum):
    insert = "insert"
    update = "update"
    delete = "delete"


class ManagerType(Enum):
    admin = "admin"
    issuer = "issuer"
    listener = "listener"

    @classmethod
    def is_admin(cls, type: str) -> bool:
        return type == cls.admin.value

    @classmethod
    def is_issuer(cls, type: str) -> bool:
        return type == cls.issuer.value or cls.is_admin(type)

    @classmethod
    def is_listener(cls, type: str) -> bool:
        return type == cls.listener.value or cls.is_admin(type)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashing(password):
    return pwd_context.hash(password)


def verify(password, real_password):
    return pwd_context.verify(password, real_password)


class DeckSheetEnv:
    # python name mangling
    __depth = {1.5, 2, 3}
    __zinc_grade = {0, 40, 60, 80, 120}

    @classmethod
    def get_depth(cls) -> set:
        return cls.__depth

    @classmethod
    def verify_thickness(cls, value: float) -> bool:
        return value >= 0.6 and value <= 2.0

    @classmethod
    def get_zinc_grade(cls) -> set:
        return cls.__zinc_grade


class CChannelEnv:
    __zinc_grade = {0, 40, 60, 80, 120}
    __width = {1, 1.5, 2, 3}
    __height = {1, 2, 3, 4, 5, 6, 7, 8}

    @classmethod
    def verify_thickness(cls, value: float) -> bool:
        return value >= 0.6 and value <= 2.0

    @classmethod
    def get_zinc_grade(cls) -> set:
        return cls.__zinc_grade

    @classmethod
    def verify_width(cls, value: float) -> bool:
        return value in cls.__width

    @classmethod
    def verify_height(cls, value: float) -> bool:
        return value in cls.__height


class RoofEnv:
    @classmethod
    def verify_thickness(cls, value: float) -> bool:
        return value >= 0.25 and value <= 1.5
