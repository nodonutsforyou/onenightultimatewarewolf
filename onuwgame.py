import logging
import random
import json
import copy
from enum import Enum
from datetime import datetime
random.seed(datetime.now())


class Roles(Enum):
    WEREWOLF = "оборотень"
    VILLAGER = "мирный"
    TROUBLEMAKER = "баламут"
    ROBBER = "вор"
    SEER = "ясновидящий"
    # TANNER = "кожевник"
    # DRUNK = "пьяница"
    # HUNTER = "охотник"
    # MASON = "масон"
    INSOMNIAC = "лунатик"
    # MINION = "прихвостень"
    # DOPPELGANGER = "двойник"


# Globals
DEFAULT_ROLES = [
    Roles.WEREWOLF,
    Roles.WEREWOLF,
    Roles.VILLAGER,
    Roles.TROUBLEMAKER,
    Roles.ROBBER,
    Roles.SEER,
]
ROLES_DECRIPTION = {
    Roles.WEREWOLF: {
        "night_action_done": True,
        "night_action": 0,
    },
    Roles.VILLAGER: {
        "night_action_done": True,
        "night_action": 0,
    },
    Roles.TROUBLEMAKER: {
        "night_action_done": False,
        "night_action": [],
    },
    Roles.ROBBER: {
        "night_action_done": False,
        "night_action": -1,
    },
    Roles.SEER: {
        "night_action_done": False,
        "night_action": [],
    },
    Roles.INSOMNIAC: {
        "night_action_done": True,
        "night_action": 0,
    },
}
starting_players = [
    {
        "num": 1,
        "name": "Стол 1",
        "type": "bot"
    },
    {
        "num": 2,
        "name": "Стол 2",
        "type": "bot"
    },
    {
        "num": 3,
        "name": "Стол 3",
        "type": "bot"
    }
]


class Game:
    # Game Lobby status
    players_list = []

    # This session
    pl = []
    human_pl = []
    n = {}
    start_ts = datetime.now()

    # SESSION PART
    def get_player(self, user):
        for p in self.players_list:
            if p["id"] == user["id"]:
                return p
        return None

    def add_player(self, user):
        if self.get_player(user) is None:
            self.players_list.append(user)

    def get_list_of_players(self):
        r = [(str(p['first_name']) + ' ' + str(p['last_name'])) for p in self.players_list]
        return "\n".join(r)

    def get_num_of_players(self):
        return len(self.players_list)

    def get_buttons_list(self, tables=True, exclude_id=None, vote_all_str=None):
        ret_list = []
        if tables:
            ret_list.append([
                ("Стол 1", "1"),
                ("Стол 2", "2"),
                ("Стол 3", "3"),
            ])
        players_list = []
        for p in self.human_pl:
            if p["id"] != exclude_id:
                players_list.append((p["name"], str(p["num"])))
        ret_list.append(players_list)
        if vote_all_str is not None:
            ret_list.append([(vote_all_str, "0")])
        return ret_list

    def get_init_message(self, p):
        if p["starts_as"] == Roles.VILLAGER:
            return "Вы мирный житель\nПодождите пока остальные жители сделают свой ход", None
        if p["starts_as"] == Roles.WEREWOLF:
            return "Вы оборотень\nПодождите пока остальные жители сделают свой ход", None
        if p["starts_as"] == Roles.TROUBLEMAKER:
            return "Вы баламут\nвыберите двух игроков чтобы поменять их роли местами", self.get_buttons_list(exclude_id=p["id"])
        if p["starts_as"] == Roles.ROBBER:
            return "Вы вор\nвыберите номер игрока чтобы украсть его роль", self.get_buttons_list(exclude_id=p["id"])
        if p["starts_as"] == Roles.SEER:
            return "Вы ясновидящий\nвыберите номер игрока чтобы увидеть его роль.\nИли два номера ненастоящих игрков", self.get_buttons_list(exclude_id=p["id"])
        if p["starts_as"] == Roles.INSOMNIAC:
            return "Вы лунатик\nПодождите пока остальные жители сделают свой ход", None

    def shuffle_roles(self):
        roles = DEFAULT_ROLES[:len(self.pl)]
        while len(roles) < len(self.pl):
            roles.append(Roles.VILLAGER)
        random.shuffle(roles)
        logging.info("Roles are " + str(roles))
        return roles

    # GAME PART
    def init_game(self, roles = None):
        # зафиксируем список игроков
        self.pl = copy.deepcopy(starting_players)
        self.human_pl = []
        self.n = {}
        num = 4
        for human in self.players_list:
            name = str(human['first_name']) + ' ' + str(human['last_name'])
            p = {
                "num": num,
                "id": human['id'],
                "name": name,
                "type": "human",
                "votes_against": 0,
                "telegram_obj": human
            }
            self.pl.append(p)
            self.human_pl.append(p)
            num += 1

        # перемешаем роли
        if roles is None:
            roles = self.shuffle_roles()

        # раздаем роли
        i = 0
        for p in self.pl:
            p["starts_as"] = roles[i]
            p["new_role"] = roles[i]
            p["night_action"] = copy.deepcopy(ROLES_DECRIPTION[p["starts_as"]]["night_action"])
            p["night_action_done"] = ROLES_DECRIPTION[p["starts_as"]]["night_action_done"]
            p["vote"] = -1
            if p["type"] == "bot":
                p["night_action"] = 0
                p["vote"] = 0
            i += 1
        #logging.info("Stating game state with" + json.dumps(self.pl))

        #делаем номерной список
        for p in self.pl:
            self.n[p["num"]] = p

        # фиксируем время начала
        self.start_ts = datetime.now()
        logging.info("Starting timestamp " + str(self.start_ts))

    def list_of_players_by_number(self):
        msg = ""
        for key, p in self.n.items():
            msg += f'{key}: {p["name"]}\n'
        return msg

    def list_of_human_players_by_number_for_voting(self, vote_for_all=False):
        msg = ""
        if vote_for_all:
            msg = '0: Никого не убивать\n'
        for key, p in self.n.items():
            if p["type"] == "human":
                msg += f'{key}: {p["name"]}\n'
        return msg

    def action(self, user, action):
        if not isinstance(action, int):
            return False, f"Неверная команда '{action}'"
        if action <= 0:
            return False, f"Неверная команда '{action}' - выберите номер игрока"
        if action > len(self.pl):
            return False, f"Неверная команда '{action}' - такого игрока нет"
        for p in self.human_pl:
            if user['id'] == p['id']:
                if p["night_action_done"]:
                    return False, f'Нельзя выбирать второй раз'
                if action == p["num"]:
                    return False, f'Нельзя выбирать себя'
                if p["starts_as"] == Roles.TROUBLEMAKER:
                    if len(p["night_action"]) == 0:
                        p["night_action"].append(action)
                        return True, f'Принято {p["night_action"][0]}. Второй игрок?'
                    else:
                        if action in p["night_action"]:
                            return False, f'{action} уже выбран. Второй игрок?'
                        p["night_action"].append(action)
                        p["night_action_done"] = True
                        return True, f'Принято {p["night_action"][0]} и {p["night_action"][1]}'
                if p["starts_as"] == Roles.SEER:
                    p["night_action"].append(action)
                    if len(p["night_action"]) == 1:
                        if action > 3:
                            p["night_action_done"] = True
                            return True, f'Принято {p["night_action"][0]}'
                        else:
                            vals = [
                                "/1 Стол 1\n",
                                "/2 Стол 2\n",
                                "/3 Стол 3\n",
                            ]
                            del vals[action - 1]
                            return True, f'Принято {p["night_action"][0]}\nМожно выбрать еще одного:{"".join(vals)}'
                    else:
                        p["night_action_done"] = True
                        return True, f'Принято {p["night_action"][0]} и {p["night_action"][1]}'
                if p["starts_as"] == Roles.ROBBER:
                    p["night_action"] = action
                    p["night_action_done"] = True
                    return True, f'Принято {p["night_action"]}.'
        return False, f'Не удалось найти пользователя: {str(user)} (действие {str(action)})'

    def vote(self, user, vote):
        done = False
        if vote > 3 or vote == 0:
            for p in self.human_pl:
                if user['id'] == p['id']:
                    p["vote"] = vote
                    done = True
        if not done:
            logging.error(f'Не удалось найти пользователя: {str(user)} (голос {str(vote)})')
        #TODO check action correctness
        return True

    def check_actions_cast(self):
        result = True
        for p in self.human_pl:
            if not p["night_action_done"]:
                result = False
        return result

    def check_votes_cast(self):
        result = True
        for p in self.human_pl:
            if p["vote"] < 0:
                result = False
        return result

    def implement_actions(self):
        # main logic
        human_werewulfs = self.get_human_werewolves()
        for p in self.human_pl:
            # Мирный
            if p["starts_as"] == Roles.VILLAGER:
                p["msg"] = ""
            # Оборотень
            if p["starts_as"] == Roles.WEREWOLF:
                if len(human_werewulfs) == 1:
                    p["msg"] = 'Этой ночью вам пришлось выть на луну в одиночестве. Вы, кажется, единственный оборотень в этой деревне'
                else:
                    other_wolf = human_werewulfs[0] if human_werewulfs[1] == p["num"] else human_werewulfs[1]
                    p["msg"] = f'Этой ночью вам не пришлось выть на луну в одиночестве. Потому что {self.n[other_wolf]["name"]} - тоже оборотень'

            # Ясновидящий
            if p["starts_as"] == Roles.SEER:
                a = p["night_action"]
                if len(a) == 1:
                    p["msg"] = f'Зеркальный шар показал, что {self.n[a[0]]["name"]} -- {self.n[a[0]]["starts_as"]}'
                else:
                    p["msg"] = f'Зеркальный шар показал, что {self.n[a[0]]["name"]} -- {self.n[a[0]]["starts_as"]}, а {self.n[a[0]]["name"]} -- {self.n[a[0]]["starts_as"]}'
            # Вор
            if p["starts_as"] == Roles.ROBBER:
                a = p["night_action"]
                p["msg"] = f'Украденные документы подверждают, что вы теперь -- {self.n[a]["starts_as"]}'
                p["new_role"], self.n[a]["new_role"] = self.n[a]["new_role"], p["new_role"]
        for p in self.human_pl:
            # Баламут
            if p["starts_as"] == Roles.TROUBLEMAKER:
                a1 = p["night_action"][0]
                a2 = p["night_action"][1]
                p["msg"] = f'Вы подмешали роли {self.n[a1]["name"]} и {self.n[a2]["name"]}. Но они об этом не знают.'
                self.n[a1]["new_role"], self.n[a2]["new_role"] = self.n[a2]["new_role"], self.n[a1]["new_role"]
        for p in self.human_pl:
            # Лунатик
            if p["starts_as"] == Roles.INSOMNIAC:
                if p["new_role"] == p["starts_as"]:
                    p["msg"] = f'Вы проснулись среди ночи, чтобы узнать что ничего с вами не случилось.\nВы как были лунатиком, так и остались'
                else:
                    p["msg"] = f'Вы проснулись среди ночи, чтобы узнать что вы теперь не лунатик а {p["new_role"].value}'

    def implement_votes(self):
        # cast votes
        votes_for_nobody = 0
        for p in self.human_pl:
            if p["vote"] == 0:
                votes_for_nobody += 1
            else:
                self.n[p["vote"]]["votes_against"] += 1
        # count votes
        max_votes = votes_for_nobody
        for p in self.human_pl:
            if max_votes < p["votes_against"]:
                max_votes = p["votes_against"]
        # determine killed persons
        voted_out = []
        if max_votes > 1:
            for p in self.human_pl:
                if p["votes_against"] == max_votes:
                    voted_out.append(p)
        human_werewulfs = self.get_human_werewolves()

        # win/lose logic
        if len(human_werewulfs) == 0 and len(voted_out) == 0:
            return True, "Вы никого не убили, но в деревне не было оборотней. Вы все победили!"
        if len(human_werewulfs) > 0 and len(voted_out) == 0:
            msg = "Вы никого не убили, но "
            if len(human_werewulfs) == 1:
                msg += f'{self.n[human_werewulfs[0]]["name"]} оказался оборотнем. {self.n[human_werewulfs[0]]["name"]} победил!'
            else:
                msg += f'{self.n[human_werewulfs[0]]["name"]} и {self.n[human_werewulfs[1]]["name"]} оказались оборотнями. Они победили!'
            msg += "\nМирные проиграли!"
            return False, msg
        if len(human_werewulfs) == 0 and len(voted_out) > 0:
            if len(voted_out) == 1:
                msg = f'Убитый {voted_out[0]["name"]} оказался невиновным.'
            else:
                killed_list = ", ".join(v["name"] for v in voted_out)
                msg = f'Убитые {killed_list} оказались все невиновными.'
            return False, msg + "\nВ деревне не было оборотней. Вы все проиграли!"
        killed_werewolf = []
        for v in voted_out:
            if v["num"] in human_werewulfs:
                killed_werewolf.append(v["num"])
        if len(killed_werewolf) > 0:
            if len(killed_werewolf) == 1:
                msg = f'Убитый {self.n[killed_werewolf[0]]["name"]} оказался оборотнем.'
            else:
                msg = f'Убитые {self.n[killed_werewolf[0]]["name"]} и {self.n[killed_werewolf[1]]["name"]} оказались оборотнями.'
            msg += "\nМирные победили!"
            return True, msg
        if len(voted_out) == 1:
            return False, f'Убитый {voted_out[0]["name"]} оказался невинным человеком, а оборотни осталсь живы. Мирные проиграли!'
        killed_list = ", ".join(v["name"] for v in voted_out)
        return False, f'Убитые {killed_list} оказались все невинными, а оборотни осталсь живы. Мирные проиграли!'

    def get_personal_result(self, victory, id):
        msg = ""
        personal_victory = victory
        for p in self.human_pl:
            if p["id"] == id:
                if p["starts_as"] == p["new_role"]:
                    msg = f'Вы остались `{p["new_role"].value}` в конце игры\n'
                else:
                    msg = f'В конце игры вы оказались `{p["new_role"].value}`\n'
                if p["new_role"] == Roles.WEREWOLF:
                    personal_victory = not victory
                if personal_victory:
                    msg += "Вы победили!"
                else:
                    msg += "Вы проиграли!"
        return personal_victory, msg

    def get_human_werewolves(self):
        human_werewulfs = []
        for p in self.human_pl:
            if p["new_role"] == Roles.WEREWOLF:
                human_werewulfs.append(p["num"])
        return human_werewulfs

    def get_history(self):
        msg = ""
        for p in self.pl:
            if p["type"] == "bot":
                msg += f'{p["name"]} был {p["starts_as"].value} и закончил игру как {p["new_role"].value}\n'
            elif p["night_action"] == 0:
                msg += f'{p["name"]} был {p["starts_as"].value} и закончил игру как {p["new_role"].value}\n'
            else:
                msg += f'{p["name"]} был {p["starts_as"].value}, выбрал {str(p["night_action"])} и закончил игру как {p["new_role"].value}\n'
        return msg
