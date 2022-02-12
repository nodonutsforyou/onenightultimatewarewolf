import logging
import random
import json
import copy
from enum import Enum
from datetime import datetime
random.seed(datetime.now())


class Roles(Enum):
    def toJSON(self):
        return str(self)
    LIBERAL = "либерал"
    FASCIST = "фашист"
    HITLER = "Гитлер"

class Law(Enum):
    def toJSON(self):
        return str(self)
    LIBERAL = "lib"
    FASCIST = "fas"

class Actions(Enum):
    def toJSON(self):
        return str(self)
    INVESTIGATE = "investigate",
    ELECTION = "election",
    PEEK = "peek",
    EXECUTION = "execution",

# Globals
DEFAULT_ROLES = [
    Roles.LIBERAL,
    Roles.HITLER,
    Roles.LIBERAL,
    Roles.FASCIST,
    Roles.LIBERAL,
    Roles.LIBERAL,
    Roles.FASCIST,
    Roles.LIBERAL,
    Roles.FASCIST,
    Roles.LIBERAL,
]
ROLES_DECRIPTION = {
    Roles.LIBERAL: {
    },
    Roles.FASCIST: {
    },
    Roles.HITLER: {
    },
}

LAWS_LIST = [
    {"type": Law.LIBERAL, "name": "lib law no 1", "description": "либеральный: Увеличение пенсии"},
    {"type": Law.LIBERAL, "name": "lib law no 2", "description": "либеральный: Пособие по безработнице"},
    {"type": Law.LIBERAL, "name": "lib law no 3", "description": "либеральный: Проведение гей-парада"},
    {"type": Law.LIBERAL, "name": "lib law no 4", "description": "либеральный: Материнский капитал"},
    {"type": Law.LIBERAL, "name": "lib law no 5", "description": "либеральный: Запретить дискриминацию на рабочем месте"},
    {"type": Law.LIBERAL, "name": "lib law no 6", "description": "либеральный: Бесплатное мороженое детям"},
    {"type": Law.FASCIST, "name": "fas law no 1", "description": "фашистский: Закон о назначении судей"},
    {"type": Law.FASCIST, "name": "fas law no 2", "description": "фашистский: Закон о Секретной полиции"},
    {"type": Law.FASCIST, "name": "fas law no 3", "description": "фашистский: Запрет несанкционированных митингов"},
    {"type": Law.FASCIST, "name": "fas law no 4", "description": "фашистский: Запрет Свидетелей Иеговы"},
    {"type": Law.FASCIST, "name": "fas law no 5", "description": "фашистский: Выслать или посадить цыган"},
    {"type": Law.FASCIST, "name": "fas law no 6", "description": "фашистский: Запретить иностранные кинофильмы"},
    {"type": Law.FASCIST, "name": "fas law no 7", "description": "фашистский: Закон об экстремизме"},
    {"type": Law.FASCIST, "name": "fas law no 8", "description": "фашистский: Запрет коммунистической партии"},
    {"type": Law.FASCIST, "name": "fas law no 9", "description": "фашистский: Смертная казнь для педофилов и врагов народа"},
    {"type": Law.FASCIST, "name": "fas law no 10", "description": "фашистский: Запретить ввоз иностранных продуктов питания"},
    {"type": Law.FASCIST, "name": "fas law no 11", "description": "фашистский: Создание патриотического союза молодежи"},
]


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    ret = []
    for i in range(0, len(lst), n):
        ret.append(lst[i:i + n])
    return ret


class Game:
    # Game Lobby status
    players_list = []

    # This session
    pl = []
    n = {}
    start_ts = datetime.now()
    game_state = {}
    current_turn = 0
    laws_deck = []
    laws_discard = []
    laws_in_action = []
    status = None
    extra_turn_president = 0

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

    def get_buttons_list(self, exclude_id=None, vote_all_str=None, exclude_dead=False):
        ret_list = []
        players_list = []
        if not isinstance(exclude_id, list):
            exclude_id = [exclude_id]
        for p in self.pl:
            if p["id"] not in exclude_id:
                if not exclude_dead and not p["dead"]:
                    players_list.append((p["name"], str(p["num"])))
        ret_list += chunks(players_list, 3)
        if vote_all_str is not None:
            ret_list.append([(vote_all_str, "0")])
        return ret_list

    def get_chancellor_candidates_list(self):
        exclude_id = [self.n[self.curent_turn_state()["president"]]["id"]]
        if self.current_turn > 1:
            exclude_id.append(self.n[self.prev_turn_state()["president"]]["id"])
            c = self.prev_turn_state()["chancellor"]
            if c > 0:
                exclude_id.append(self.n[self.prev_turn_state()["chancellor"]]["id"])
            for p in self.pl:
                if p["dead"]:
                    exclude_id.append(p["id"])
        return self.get_buttons_list(exclude_id=exclude_id)

    def get_ok_button(self):
        return [[("Ok", "OK")]]

    def get_fashists_list(self, hitler=True, exclude_p=None):
        init_msg = "Остальные фашисты: "
        msg = init_msg
        hitler_msg = ""
        for p in self.pl:
            if hitler and p["role"] == Roles.HITLER:
                hitler_msg = f"{p['name']} Гитлер "
            if p["role"] == Roles.FASCIST:# and (exclude_p is None or exclude_p["id"] != p["id"]):
                if msg != init_msg:
                    msg += ", "
                msg += f"{p['name']}"
        return hitler_msg + msg

    def get_init_message(self, p):
        if p["role"] == Roles.LIBERAL:
            return "Вы либерал"
        if p["role"] == Roles.FASCIST:
            return "Вы фашист! " + self.get_fashists_list(exclude_p=p)
        if p["role"] == Roles.HITLER:
            return "Вы Гитлер! " + self.get_fashists_list(hitler=False)

    def shuffle_roles(self):
        roles = DEFAULT_ROLES[:len(self.pl)]
        while len(roles) < len(self.pl):
            roles.append(Roles.FASCIST)
            if len(roles) < len(self.pl):
                roles.append(Roles.LIBERAL)
        random.shuffle(roles)
        logging.info("Roles are " + str(roles))
        return roles

    def shuffle_laws(self):
        laws = copy.deepcopy(LAWS_LIST)
        random.shuffle(laws)
        logging.info("Laws are " + str(laws))
        return laws

    # GAME PART
    def init_game(self, roles=None, laws=None, starting_player=None):
        # зафиксируем список игроков
        self.pl = []
        self.n = {}
        self.game_state = {}
        num = 1
        status = False
        for human in self.players_list:
            name = str(human['first_name']) + ' ' + str(human['last_name'])
            p = {
                "num": num,
                "id": human['id'],
                "name": name,
                "telegram_obj": human,
                "dead": False
            }
            self.pl.append(p)
            num += 1

        # перемешаем роли
        if roles is None:
            roles = self.shuffle_roles()


        # раздаем роли
        i = 0
        for p in self.pl:
            p["role"] = roles[i]
            p["vote"] = {1: -1}
            i += 1
        #logging.info("Stating game state with" + json.dumps(self.pl))

        #делаем номерной список
        for p in self.pl:
            self.n[p["num"]] = p

        #заводим законы
        if laws is None:
            laws = self.shuffle_laws()
        self.laws_deck = laws
        self.laws_in_action = []
        self.laws_discard = []

        #Заводим игровой лог
        self.current_turn = 0
        self.new_turn(starting_player)
        self.status = None
        self.extra_turn_president = 0

        # фиксируем время начала
        self.start_ts = datetime.now()
        logging.info("Starting timestamp " + str(self.start_ts))

    def list_of_players_by_number(self):
        msg = ""
        for key, p in self.n.items():
            msg += f'{key}: {p["name"]}\n'
        return msg

    def list_of_alive_players_by_number(self):
        msg = ""
        for key, p in self.n.items():
            if not p["dead"]:
                msg += f'{key}: {p["name"]}\n'
        return msg

    def list_of_human_players_by_number_for_voting(self, vote_for_all=False):
        msg = ""
        if vote_for_all:
            msg = '0: Никого не убивать\n'
        for key, p in self.n.items():
            msg += f'{key}: {p["name"]}\n'
        return msg

    def view_laws(self, n, shuffle=True):
        if len(self.laws_deck) < 4:
            self.laws_deck += self.laws_discard
            if shuffle:
                random.shuffle(self.laws_deck)
        return self.laws_deck[:n]

    def pop_laws(self, n, shuffle=True):
        poped = self.laws_deck[:n]
        self.laws_deck = self.laws_deck[n:]
        if len(self.laws_deck) < 4:
            self.laws_deck += self.laws_discard
            self.laws_discard = []
            if shuffle:
                random.shuffle(self.laws_deck)
        return poped

    def count_laws(self):
        lib = 0
        fas = 0
        for l in self.laws_in_action:
            if l["type"] == Law.LIBERAL:
                lib += 1
            if l["type"] == Law.FASCIST:
                fas += 1
        return lib, fas

    def check_victory(self):
        lib, fas = self.count_laws()
        lib_alive, fas_alive = 0, 0
        for p in self.pl:
            if p["role"] == Roles.HITLER:
                if p["dead"]:
                    self.status = False, True, "Гитлер убит! Либералы победили!"
                    return True
                else:
                    fas_alive += 1
            if p["role"] == Roles.FASCIST:
                if not p["dead"]:
                    fas_alive += 1
            if p["role"] == Roles.LIBERAL:
                if not p["dead"]:
                    lib_alive += 1
        if fas == 3:
            if self.curent_turn_state()["chancellor"] > 0 and self.n[self.curent_turn_state()["chancellor"]]["role"] == Roles.HITLER:
                if self.curent_turn_state()["law"] is None or self.curent_turn_state()["law"]["type"] == Law.LIBERAL:
                    self.status = False, False, "Фашисты избрали Гитлера канцлером! Фашисты победили!"
                    return True
        if fas >= 4:
            if self.curent_turn_state()["chancellor"] > 0 and self.n[self.curent_turn_state()["chancellor"]]["role"] == Roles.HITLER:
                self.status = False, False, "Фашисты избрали Гитлера канцлером! Фашисты победили!"
                return True
        if fas >= 6:
            self.status = False, False, "Фашисты избрали 6 законов! Фашисты победили!"
            return True
        if lib >= 6:
            self.status = False, True, "Либералы избрали 6 законов! Либералы победили!"
            return True
        self.status = True, None, f"Принято {lib} либеральных законов и {fas} фашистских законов"
        if fas_alive > lib_alive:
            self.status = False, False, "Фашисты убили либералов и теперь в большинстве"
            return True
        return False

    def pick_next_president(self, president=None):
        if self.current_turn == 0:
            if president is None:
                return random.randint(1, len(self.pl))
            return president
        president = self.curent_turn_state()["president"]
        if self.extra_turn_president > 0:
            president, self.extra_turn_president = self.extra_turn_president, -president
            if not self.n[president]["dead"]:
                return president
        if self.extra_turn_president < 0:
            president, self.extra_turn_president = -self.extra_turn_president, 0
        for i in range(len(self.pl)):
            president += 1
            if president > len(self.n):
                president = 1
            if not self.n[president]["dead"]:
                return president
        raise Exception("Everybody is dead?")

    def new_turn(self, president=None, shuffle=True):
        president = self.pick_next_president(president)
        if self.current_turn > 1:
            victory = self.check_victory()
            if victory:
                return False
        self.current_turn += 1
        turn_obj = {
            "president": president,
            "chancellor": -1,
            "chancellor_candidate": -1,
            "votes": {},
            "laws_big_list": [],
            "laws_short_list": [],
            "law": None,
            "veto": False,
            "veto_p": None,
            "veto_c": None,
            "action": -1,
        }
        if self.current_turn == 1:
            turn_obj["chaos_score"] = 0
        else:
            turn_obj["chaos_score"] = self.prev_turn_state()["chaos_score"]
        for key, p in self.n.items():
            if p["dead"]:
                turn_obj["votes"][key] = 0
            else:
                turn_obj["votes"][key] = None
        self.game_state[self.current_turn] = turn_obj
        return True

    def curent_turn_state(self):
        return self.game_state[self.current_turn]

    def prev_turn_state(self):
        return self.game_state[self.current_turn - 1]

    def pick_chancellor(self, user, action):
        if not isinstance(action, int):
            if str(action) == "OK":
                return True
            return False, f"Неверная команда '{action}'"
        if action <= 0:
            return False, f"Неверная команда '{action}'"
        if action > len(self.pl):
            return False, f"Неверная команда '{action}'"
        if user['id'] == self.n[self.curent_turn_state()['president']]['id']:
            candidate = self.n[action]
            if action == self.curent_turn_state()['president']:
                return False, f"Нельзя выбрать себя"
            if self.current_turn > 1:
                if action == self.prev_turn_state()['president']:
                    return False, f"Нельзя выбрать {candidate['name']} - он был президентом в прошлом ходу"
                if action == self.prev_turn_state()['chancellor']:
                    return False, f"Нельзя выбрать {candidate['name']} - он был канцлером в прошлом ходу"
                if candidate["dead"]:
                    return False, f"Нельзя выбрать {candidate['name']} - он мертв"
            self.curent_turn_state()["chancellor_candidate"] = action
            return True, f'{candidate["name"]} назначается кандидатом в канцлеры'
        return False, f'{str(user)} не президент!'

    def check_president_legislation_is_ready(self):
        if len(self.curent_turn_state()["laws_short_list"]) > 0:
            return True
        return False

    def legislation(self, user, action):
        if not isinstance(action, int):
            if str(action) == "OK":
                return True
            return False, f"Неверная команда '{action}'"
        if action > len(self.pl) and action > 3:
            return False, f"Неверная команда '{action}'"
        for p in self.pl:
            if user['id'] == self.n[self.curent_turn_state()['chancellor']]['id']:
                if action >= 3:
                    return False, f"Неверная команда для канцлера '{action}'"
                if action < 0:
                    return False, f"Неверная команда '{action}'"
                self.curent_turn_state()["laws_short_list"] = copy.deepcopy(self.curent_turn_state()["laws_big_list"])
                self.laws_discard.append(self.curent_turn_state()["laws_short_list"][action])
                del self.curent_turn_state()["laws_short_list"][action]
                laws_descr = self.curent_turn_state()["laws_short_list"][0]["description"] + " и " + self.curent_turn_state()["laws_short_list"][1]["description"]
                return True, "Выбраны законы " + laws_descr
            if user['id'] == self.n[self.curent_turn_state()['president']]['id']:
                if action >= 2:
                    return False, f"Неверная команда для президента '{action}'"
                if action < 0:
                    if not self.check_veto_option():
                        return False, f"Неверная команда '{action}'"
                    if not self.curent_turn_state()["veto_p"] is None:
                        return False, f"Нельзя назначать вето дважды '{action}'"
                    self.curent_turn_state()["veto"] = True
                    self.curent_turn_state()["veto_p"] = True
                    return True, f"Запрошено Вето на все законы '{action}'"
                self.curent_turn_state()["law"] = self.curent_turn_state()["laws_short_list"][action]
                self.laws_in_action.append(self.curent_turn_state()["law"])
                if action == 1:
                    discarded = 0
                else:
                    discarded = 1
                self.laws_discard.append(self.curent_turn_state()["laws_short_list"][discarded])
                return True, "Выбран закон " + self.curent_turn_state()["law"]["description"]
        return False, f'Не удалось найти пользователя: {str(user)} (действие {str(action)})'

    def veto(self, user, action):
        if not isinstance(action, int):
            if str(action) == "OK":
                return True
            return False, f"Неверная команда '{action}'"
        if action > 1 or action < 0:
            return False, f"Неверная команда '{action}'"
        action = action == 1
        for p in self.pl:
            if user['id'] == self.n[self.curent_turn_state()['chancellor']]['id']:
                self.curent_turn_state()["veto_c"] = action
                if action:
                    return True, f"Принят голос за наложение вето"
                else:
                    return True, f"Принят голос притив наложения вето"
            if user['id'] == self.n[self.curent_turn_state()['president']]['id']:
                self.curent_turn_state()["veto_p"] = action
                if action:
                    return True, f"Принят голос за наложение вето"
                else:
                    return True, f"Принят голос притив наложения вето"
        return False, f'Не удалось найти пользователя: {str(user)} (действие {str(action)})'

    def vote(self, user, vote):
        if not isinstance(vote, int):
            if str(vote) == "OK":
                return True, None
            return False, f"Неверная команда '{vote}'"
        done = False
        voted_name = None
        for p in self.pl:
            if user['id'] == p['id']:
                i = p["num"]
                if vote > 0:
                    self.curent_turn_state()["votes"][i] = 1
                else:
                    self.curent_turn_state()["votes"][i] = -1
                done = True
                candidate = self.curent_turn_state()["chancellor_candidate"]
                if vote > 0:
                    voted_name = "Принят голос за канцлера " + self.n[candidate]["name"]
                else:
                    voted_name = "Принят голос против канцлера " + self.n[candidate]["name"]
        if not done:
            msg = f'Не удалось найти пользователя: {str(user)} (голос {str(vote)})'
            logging.error(msg)
            return False, msg
        #TODO check action correctness
        return True, voted_name

    def check_legislation_done(self):
        if self.curent_turn_state()["law"] is None:
            if self.check_votes_cast() and self.curent_turn_state()["chancellor"] == -1:
                return True
            if self.curent_turn_state()["chancellor"] == -1 and len(self.get_chancellor_candidates_list()) == 0:
                return True
            return False
        return True

    def check_votes_cast(self):
        result = True
        for p in self.pl:
            i = p["num"]
            if self.curent_turn_state()["votes"][i] is None:
                result = False
        return result

    def implement_votes(self, shuffle=True):
        result = 0
        for p in self.pl:
            i = p["num"]
            vote = self.curent_turn_state()["votes"][i]
            if not self.curent_turn_state()["votes"][i] is None:
                result += vote
        if result > 0:
            self.curent_turn_state()["chancellor"] = self.curent_turn_state()["chancellor_candidate"]
            if self.check_victory():
                return None, f"{self.n[self.curent_turn_state()['chancellor']]['name']} оказался Гитлером!"
            self.curent_turn_state()["laws_big_list"] += self.pop_laws(3, shuffle=shuffle)
            return True, f"{self.n[self.curent_turn_state()['chancellor']]['name']} избран канцлером"
        self.curent_turn_state()["chaos_score"] += 1
        if self.curent_turn_state()["chaos_score"] > 2:
            self.chaos_popup_law(shuffle=shuffle)
            return False, f"{self.n[self.curent_turn_state()['chancellor_candidate']]['name']} отвергнут как кандидат. Народ потребовал принятия закона {self.curent_turn_state()['law']['description']}"
        return False, f"{self.n[self.curent_turn_state()['chancellor_candidate']]['name']} отвергнут как кандидат"

    def chaos_popup_law(self, shuffle=True):
        popped = self.pop_laws(1, shuffle=shuffle)
        self.curent_turn_state()["chaos_score"] = 0
        self.curent_turn_state()["law"] = popped[0]
        self.laws_in_action.append(self.curent_turn_state()["law"])

    def implement_veto(self, shuffle=True):
        veto_p, veto_c = self.curent_turn_state()["veto_p"], self.curent_turn_state()["veto_c"]
        if veto_p is None or veto_c is None:
            return False, None, None
        self.curent_turn_state()["veto"] = False
        if veto_c and veto_p:
            self.curent_turn_state()["chaos_score"] += 1
            if self.curent_turn_state()["chaos_score"] > 2:
                self.chaos_popup_law(shuffle=shuffle)
                return True, True, f"Наложено вето. Народ потребовал принятия закона {self.curent_turn_state()['law']['description']}"
            return True, True, f"Наложено вето. Народ недовлен на {self.curent_turn_state()['chaos_score']}/3"
        return True, False, "Вето отклонено"

    def check_veto_option(self):
        lib, fas = self.count_laws()
        n = fas
        if self.curent_turn_state()["veto"] or not self.curent_turn_state()["veto_p"] is None:
            return False
        if fas == 5:
            return True
        return False

    def check_hitler_chancellorship_wins_the_game(self):
        lib, fas = self.count_laws()
        return fas >= 3

    def check_next_fas_law_wins_the_game(self):
        lib, fas = self.count_laws()
        return fas >= 5

    def check_chaos_score(self):
        return self.curent_turn_state()['chaos_score'] >= 2

    def check_next_action(self):
        lib, fas = self.count_laws()
        return self.select_action(fas+1)

    def select_action(self, n=None):
        if n is None:
            lib, fas = self.count_laws()
            n = fas
        if len(self.pl) <= 6:
            if n == 3:
                return Actions.PEEK
            if n >= 4:
                return Actions.EXECUTION
        else:
            if len(self.pl) <= 8:
                if n == 2:
                    return Actions.INVESTIGATE
                if n == 3:
                    return Actions.ELECTION
                if n >= 4:
                    return Actions.EXECUTION
            else:
                if n <= 2:
                    return Actions.INVESTIGATE
                if n == 3:
                    return Actions.ELECTION
                if n >= 4:
                    return Actions.EXECUTION
        return None

    def desribe_next_action(self):
        action = self.check_next_action()
        if action == Actions.PEEK:
            return "При принятии следующего фашистского закона у президента появится возможность посмотреть следующие 3 закона"
        if action == Actions.EXECUTION:
            return "При принятии следующего фашистского закона у президента появится власть казнить одного игрока"
        if action == Actions.INVESTIGATE:
            return "При принятии следующего фашистского закона у президента появится возможность проверить лояльность одного игрока"
        if action == Actions.ELECTION:
            return "При принятии следующего фашистского закона у президента появится возможность назначить внеочередного президента"
        return None

    def action(self, user, action):
        if not isinstance(action, int):
            if str(action) == "OK":
                return True
            return False, f"Неверная команда '{action}'", None
        if action <= 0:
            return False, f"Неверная команда '{action}'", None
        if action > len(self.pl):
            return False, f"Неверная команда '{action}'", None
        president = self.n[self.curent_turn_state()['president']]
        if user['id'] == president['id']:
            target = self.n[action]
            lib, fas = self.count_laws()
            action_type = self.select_action(fas)
            if action_type == Actions.INVESTIGATE:
                self.curent_turn_state()["action"] = action
                role = target["role"]
                if role == Roles.LIBERAL:
                    msg = f'Проверка показала, что {target["name"]} - либерал'
                else:
                    msg = f'Проверка показала, что {target["name"]} - фашист'
                return True, msg, f"Президент {president['name']} провел *расследование* на предмет лояльности некоторых членов парламента"
            if action_type == Actions.ELECTION:
                if user['id'] == target['id']:
                    return False, f'Нельзя назначить себя экстренным президентом', None
                self.curent_turn_state()["action"] = action
                self.extra_turn_president = action
                return True, f'Следующим президентом назначается {target["name"]}', f"Президент {president['name']} назначил экстренного президента. В следующем ходу {target['name']} будет президентом вне очереди"
            if action_type == Actions.EXECUTION:
                self.curent_turn_state()["action"] = action
                target["dead"] = True
                self.check_victory()
                if target["role"] == Roles.HITLER:
                    return True, f'{target["name"]} приговорен к расстрелу. {target["name"]} оказался Гитлером! Либералы победили', None
                return True, f'{target["name"]} приговорен к расстрелу', f'Президент {president["name"]} приговорил {target["name"]} приговорен к расстрелу'
        return False, f'{str(user)} не президент!', None

    def implement_action(self):
        lib, fas = self.count_laws()
        if self.curent_turn_state()["law"] is None:
            self.curent_turn_state()["action"] = 0
            return True, f"В этом ходу не принято ни одного закона. Народ недовлен на {self.curent_turn_state()['chaos_score']}/3"
        if self.curent_turn_state()["law"]["type"] == Law.LIBERAL:
            self.curent_turn_state()["action"] = 0
            return True, f"В этом ходу был принят либеральный закон {self.curent_turn_state()['law']['description']}"
        if fas > 3 and self.curent_turn_state()["chancellor"] > 0 and self.n[self.curent_turn_state()["chancellor"]]["role"] == Roles.HITLER:
            self.curent_turn_state()["action"] = 0
            return True, f"В этом ходу Гитлер был избран канцлером"
        action = self.select_action(fas)
        if action is Actions.PEEK:
            self.curent_turn_state()["action"] = 0
            return False, f'Принят закон: {self.curent_turn_state()["law"]["description"]}'
        if action is None:
            self.curent_turn_state()["action"] = 0
            return True, f'Принят закон: {self.curent_turn_state()["law"]["description"]}'
        return self.curent_turn_state()["action"] >= 0, None

    def implement_legislature(self):
        pass
