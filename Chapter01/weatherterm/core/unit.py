from enum import auto, unique
from .base_enum import BaseEnum


@unique
class Unit(BaseEnum):
    CELSIUS = auto()
    FAHRENHEIT = auto()
