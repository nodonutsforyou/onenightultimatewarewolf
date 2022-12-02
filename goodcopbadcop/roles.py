from enum import Enum


class Roles(Enum):
    def toJSON(self):
        return str(self)
    GOOD = "👮 Хороший коп"
    AGENT = "🕵 Комиссар"
    BAD = "💰 Плохой коп"
    KINGPIN = "😈 Вор в законе"