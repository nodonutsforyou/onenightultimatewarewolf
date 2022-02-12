from __future__ import annotations
from collections import namedtuple
from enum import Enum

dummy_players = [
    {'first_name': 'Peotr', 'last_name': 'I', 'id': "1", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Vaysa', 'last_name': 'II', 'id': "2", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Goasha', 'last_name': 'III', 'id': "3", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'IVAN', 'last_name': 'IV', 'id': "4", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Sputnik', 'last_name': 'V', 'id': "5", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Ruslan', 'last_name': 'VI', 'id': "6", 'language_code': 'en', 'is_bot': False},
]

dummy_players_large_list = [
    {'first_name': 'Peotr', 'last_name': 'I', 'id': "1", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Vaysa', 'last_name': 'II', 'id': "2", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Goasha', 'last_name': 'III', 'id': "3", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'IVAN', 'last_name': 'IV', 'id': "4", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Sputnik', 'last_name': 'V', 'id': "5", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Ruslan', 'last_name': 'VI', 'id': "6", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Peotr', 'last_name': 'I', 'id': "11", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Vaysa', 'last_name': 'II', 'id': "12", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Goasha', 'last_name': 'III', 'id': "13", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'IVAN', 'last_name': 'IV', 'id': "14", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Sputnik', 'last_name': 'V', 'id': "15", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Ruslan', 'last_name': 'VI', 'id': "16", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Peotr', 'last_name': 'I', 'id': "21", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Vaysa', 'last_name': 'II', 'id': "22", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Goasha', 'last_name': 'III', 'id': "23", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'IVAN', 'last_name': 'IV', 'id': "24", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Sputnik', 'last_name': 'V', 'id': "25", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Ruslan', 'last_name': 'VI', 'id': "26", 'language_code': 'en', 'is_bot': False},
]

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    ret = []
    for i in range(0, len(lst), n):
        ret.append(lst[i:i + n])
    return ret


def flatten_buttons(buttons):
    list = []
    for r in buttons:
        for i in r:
            text, cmd = i
            list.append(int(cmd))
    return list


class ReplyTo(Enum):
    def toJSON(self):
        return str(self)
    CALLER = "reply to caller"
    ALL = "message all"
    ALL_OTHERS = "message all except caller"


class Message:
    msg = None
    commands = None
    expected_action = None

    def __init__(self, msg, expected_action=None, commands=None):
        self.msg = msg
        self.commands = commands


class Result:
    result = None
    next_actions = {}
    game_end = False

    def __str__(self):
        return str(self.next_actions)

    @staticmethod
    def error(msg) -> Result:
        r = Result()
        r.result = False
        r.next_actions[ReplyTo.CALLER] = Message(msg)
        return r

    @staticmethod
    def action(msg, expected_action=None, commands=None) -> Result:
        r = Result()
        r.next_actions[ReplyTo.CALLER] = Message(msg, expected_action, commands)
        return r

    @staticmethod
    def action_by_id(player_id, msg, expected_action=None, commands=None) -> Result:
        r = Result()
        r.next_actions[player_id] = Message(msg, expected_action, commands)
        return r

    @staticmethod
    def notify_all(msg, expected_action=None, commands=None) -> Result:
        r = Result()
        r.next_actions[ReplyTo.ALL] = Message(msg, expected_action, commands)
        return r

    def __init__(self):
        self.next_actions = {}
        self.result = True

    def notify_all_others(self, msg, expected_action=None, commands=None):
        self.next_actions[ReplyTo.ALL_OTHERS] = Message(msg, expected_action, commands)

    def msg_to_id(self, id, msg, expected_action=None, commands=None):
        self.next_actions[id] = Message(msg, expected_action, commands)


