import logging
import random
import json
import copy
from enum import Enum
from datetime import datetime
from player import Player
from game import Game
from util import *

random.seed(datetime.now())

class State(Enum):
    INIT = "INIT"
    PRESIDENT = "PRESIDENT"
    VOTE = "VOTE"
    LEGISLATURE_C = "LEGISLATURE_C"
    LEGISLATURE_P = "LEGISLATURE_P"
    VETO = "VETO"
    IMPLEMENTATION = "IMPLEMENTATION"
    IMPLEMENTATION_ACTION = "IMPLEMENTATION_ACTION"
    NEW_TURN = "NEW_TURN"
    END_GAME = "END_GAME"

class Roles(Enum):
    def toJSON(self):
        return str(self)
    LIBERAL = "✌ Человек"
    FASCIST = "🐌 Мозговой слизень"
    HITLER = "🐸 Лидер мозговых слизеней"

class Law(Enum):
    def toJSON(self):
        return str(self)
    LIBERAL = "lib" # 🕊️
    FASCIST = "fas" # 🎖️

class Actions(Enum):
    def toJSON(self):
        return str(self)
    INVESTIGATE = "🕵 проверить",
    ELECTION = "🗳 выборы",
    PEEK = "👀 подсмотреть",
    EXECUTION = "🔫 расстрелять",

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

VOTE_MARKUP = [[("✅ За", 1), ("❌ Против", -1)]]

LAWS_LIST = [
    {"type": Law.LIBERAL, "name": "lib law no 1", "description": "🕊️ либеральный: Увеличение пенсии"},
    {"type": Law.LIBERAL, "name": "lib law no 2", "description": "🕊️ либеральный: Пособие по безработнице"},
    {"type": Law.LIBERAL, "name": "lib law no 3", "description": "🕊️ либеральный: Проведение гей-парада"},
    {"type": Law.LIBERAL, "name": "lib law no 4", "description": "🕊️ либеральный: Материнский капитал"},
    {"type": Law.LIBERAL, "name": "lib law no 5", "description": "🕊️ либеральный: Запретить дискриминацию на рабочем месте"},
    {"type": Law.LIBERAL, "name": "lib law no 6", "description": "🕊️ либеральный: Бесплатное мороженое детям"},
    {"type": Law.FASCIST, "name": "fas law no 1", "description": "🎖️ авторитарный: Закон о назначении судей"},
    {"type": Law.FASCIST, "name": "fas law no 2", "description": "🎖️ авторитарный: Закон о Секретной полиции"},
    {"type": Law.FASCIST, "name": "fas law no 3", "description": "🎖️ авторитарный: Запрет несанкционированных митингов"},
    {"type": Law.FASCIST, "name": "fas law no 4", "description": "🎖️ авторитарный: Запрет Свидетелей Иеговы"},
    {"type": Law.FASCIST, "name": "fas law no 5", "description": "🎖️ авторитарный: Выслать или посадить цыган"},
    {"type": Law.FASCIST, "name": "fas law no 6", "description": "🎖️ авторитарный: Запретить иностранные кинофильмы"},
    {"type": Law.FASCIST, "name": "fas law no 7", "description": "🎖️ авторитарный: Закон об экстремизме"},
    {"type": Law.FASCIST, "name": "fas law no 8", "description": "🎖️ авторитарный: Запрет коммунистической партии"},
    {"type": Law.FASCIST, "name": "fas law no 9", "description": "🎖️ авторитарный: Смертная казнь для педофилов и врагов народа"},
    {"type": Law.FASCIST, "name": "fas law no 10", "description": "🎖️ авторитарный: Запретить ввоз иностранных продуктов питания"},
    {"type": Law.FASCIST, "name": "fas law no 11", "description": "🎖️ авторитарный: Создание патриотического союза молодежи"},
]


class SecretSlugsGame(Game):
    laws_deck = []
    laws_discard = []
    laws_in_action = []
    extra_turn_president = 0

    OPTION_SHUFFLE = True

    # Abstract methods redef
    def get_init_message(self, p):
        if p["role"] == Roles.LIBERAL:
            return "Вы ✌ Человек"
        if p["role"] == Roles.FASCIST:
            return "Вы 🐌 Мозговой слизень! " + self.get_fashists_list(exclude_p=p)
        if p["role"] == Roles.HITLER:
            return "Вы 🐸 Лидер мозговых слизеней! " + self.get_fashists_list(hitler=False)

    def do_next_step(self, unstack=False) -> Result:
        if self.check_next_step():
            s_state = self.state
            r = self._do_next_step()
            e_state = self.state
            if e_state is None:
                e_state = "None"
            else:
                e_state = e_state.value
            self.current_turn_state()["logs"].append((f"next_action state {s_state.value}->{e_state}", r))
            return r
        return Result()

    def _do_next_step(self) -> Result:
        if self.state == State.INIT:
            return None
        elif self.state == State.PRESIDENT:
            return None
        elif self.state == State.VOTE:
            return self.implement_votes()
        elif self.state == State.LEGISLATURE_C:
            return None
        elif self.state == State.LEGISLATURE_P:
            return None
        elif self.state == State.VETO:
            return None
        elif self.state == State.IMPLEMENTATION:
            return self.implement_action()
        elif self.state == State.IMPLEMENTATION_ACTION:
            return None
        elif self.state == State.NEW_TURN:
            return self.new_turn()
        elif self.state == State.END_GAME:
            return None
        if self.state is None:
            return None
        raise Exception(f"not yet implemented - {self.state}")

    def check_next_step(self) -> bool:
        if self.state == State.INIT:
            return False
        elif self.state == State.PRESIDENT:
            return False
        elif self.state == State.VOTE:
            for key, player in self.n.items():
                if key not in self.current_turn_state()["votes"] or self.current_turn_state()["votes"][key] is None:
                    return False
            return True
        elif self.state == State.LEGISLATURE_C:
            return False
        elif self.state == State.LEGISLATURE_P:
            return False
        elif self.state == State.VETO:
            return False
        elif self.state == State.IMPLEMENTATION:
            return True
        elif self.state == State.IMPLEMENTATION_ACTION:
            return False
        elif self.state == State.NEW_TURN:
            return self.new_turn()
        elif self.state == State.END_GAME:
            return False
        if self.state is None:
            return False
        raise Exception(f"not yet implemented - {self.state}")

    def _do_action(self, user, action) -> Result:
        if self.state == State.INIT:
            return None
        elif self.state == State.PRESIDENT:
            return self.pick_chancellor(user, action)
        elif self.state == State.VOTE:
            return self.vote(user, action)
        elif self.state == State.LEGISLATURE_C:
            return self.legislation_c(user, action)
        elif self.state == State.LEGISLATURE_P:
            return self.legislation_p(user, action)
        elif self.state == State.VETO:
            return self.veto(user, action)
        elif self.state == State.IMPLEMENTATION:
            return None
        elif self.state == State.IMPLEMENTATION_ACTION:
            return self.action(user, action)
        elif self.state == State.NEW_TURN:
            return None
        elif self.state == State.END_GAME:
            return None
        if self.state is None:
            return None
        raise Exception(f"not yet implemented - {self.state}")

    def get_chancellor_candidates_list(self):
        exclude_id = [self.get_current_president().id]
        if self.current_turn > 1:
            exclude_id.append(self.n[self.prev_turn_state()["president"]].id)
            c = self.prev_turn_state()["chancellor"]
            if c > 0:
                exclude_id.append(self.n[self.prev_turn_state()["chancellor"]].id)
        return self.get_buttons_list(exclude_id=exclude_id, exclude_dead=True)

    def get_fashists_list(self, hitler=True, exclude_p=None):
        init_msg = "Остальные Мозговые слизени: "
        msg = init_msg
        hitler_msg = ""
        for p in self.pl:
            if hitler and p["role"] == Roles.HITLER:
                hitler_msg = f"🐸 {p['name']} Лидер мозговых слизеней. "
            if p["role"] == Roles.FASCIST:# and (exclude_p is None or exclude_p["id"] != p["id"]):
                if msg != init_msg:
                    msg += ", "
                msg += f"🐌 {p['name']}"
        return hitler_msg + msg

    def shuffle_roles(self):
        roles = DEFAULT_ROLES[:len(self.pl)]
        while len(roles) < len(self.pl):
            roles.append(Roles.FASCIST)
            if len(roles) < len(self.pl):
                roles.append(Roles.LIBERAL)
        if self.OPTION_SHUFFLE:
            random.shuffle(roles)
        logging.info("Roles are " + str(roles))
        return roles

    def shuffle_laws(self):
        laws = copy.deepcopy(LAWS_LIST)
        if self.OPTION_SHUFFLE:
            random.shuffle(laws)
        logging.info("Laws are " + str(laws))
        return laws

    # GAME PART
    def init_game(self, roles=None, laws=None, starting_player=None):
        super().init_game()
        self.state = State.INIT
        # перемешаем роли
        if roles is None:
            roles = self.shuffle_roles()
        # раздаем роли
        i = 0
        for p in self.pl:
            p: Player
            p.role = roles[i]
            i += 1
        #заводим законы
        if laws is None:
            laws = self.shuffle_laws()
        self.laws_deck = laws
        self.laws_in_action = []
        self.laws_discard = []

        #Заводим игровой лог
        self.status = None
        self.extra_turn_president = 0

        # фиксируем время начала
        self.start_ts = datetime.now()
        logging.info("Starting timestamp " + str(self.start_ts))
        return self.new_turn(starting_player)

    def view_laws(self, n):
        self.shuffle_in_discarded()
        return self.laws_deck[:n]

    def pop_laws(self, n):
        poped = self.laws_deck[:n]
        self.laws_deck = self.laws_deck[n:]
        self.shuffle_in_discarded()
        return poped

    def shuffle_in_discarded(self):
        if len(self.laws_deck) < 4:
            self.laws_deck += self.laws_discard
            self.laws_discard = []
            if self.OPTION_SHUFFLE:
                random.shuffle(self.laws_deck)

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
            if p.role == Roles.HITLER:
                if p.dead:
                    self.status = False, True, "Гитлер убит! Либералы победили!"
                    return True
                else:
                    fas_alive += 1
            if p.role == Roles.FASCIST:
                if not p.dead:
                    fas_alive += 1
            if p.role == Roles.LIBERAL:
                if not p.dead:
                    lib_alive += 1
        if fas == 3:
            if self.current_turn_state()["chancellor"] > 0 and self.n[self.current_turn_state()["chancellor"]].role == Roles.HITLER:
                if self.current_turn_state()["law"] is None or self.current_turn_state()["law"]["type"] == Law.LIBERAL:
                    self.status = False, False, "Фашисты избрали Гитлера канцлером! Фашисты победили!"
                    return True
        if fas >= 4:
            if self.current_turn_state()["chancellor"] > 0 and self.n[self.current_turn_state()["chancellor"]].role == Roles.HITLER:
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

    def get_victory_message(self) -> Result:
        end, whom, msg = self.state
        return Result.notify_all(f"{msg}\n\n{self.get_fashists_list()}")

    def pick_next_president(self, president=None):
        if self.current_turn == 0:
            if president is None:
                return random.randint(1, len(self.pl))
            return president
        president = self.current_turn_state()["president"]
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
            if not self.n[president].dead:
                return president
        raise Exception("Everybody is dead?")

    def new_turn(self, president=None):
        president_n = self.pick_next_president(president)
        president = self.n[president_n]
        if self.current_turn > 1:
            victory = self.check_victory()
            if victory:
                return False
        self.current_turn += 1
        turn_obj = {
            "president": president_n,
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
            "logs": [],
        }
        if self.current_turn == 1:
            turn_obj["chaos_score"] = 0
        else:
            turn_obj["chaos_score"] = self.prev_turn_state()["chaos_score"]
        for key, p in self.n.items():
            if p.dead:
                turn_obj["votes"][key] = 0
            else:
                turn_obj["votes"][key] = None
        self.game_state[self.current_turn] = turn_obj
        candidates_list = self.get_chancellor_candidates_list()
        if len(candidates_list) == 0:
            self.state = State.IMPLEMENTATION
            return Result.notify_all("Нет ни одной подходящей кандидатуры на роль канцлера!", State.IMPLEMENTATION)
        r = Result.notify_all(f"{president.name} назначен президентом в этом ходу!\n{president.name} Выбирает себе канцлера", State.PRESIDENT)
        r.msg_to_id(president.id, "Выберите себе канцлера:", State.PRESIDENT, candidates_list)
        self.state = State.PRESIDENT
        return r

    def pick_chancellor(self, user, action):
        r = Game.check_input_values(action, 1, self.len)
        if r is not None:
            return r
        president = self.get_current_president()
        if user['id'] != president.id:
            return Result.error(f'{str(user)} не президент!')
        candidate = self.n[action]
        if president.num == candidate.num:
            return Result.error(f"Нельзя выбрать себя")
        if self.current_turn > 1:
            if action == self.prev_turn_state()['president']:
                return Result.error(f"Нельзя выбрать {candidate.name} - он был президентом в прошлом ходу")
            if action == self.prev_turn_state()['chancellor']:
                return Result.error(f"Нельзя выбрать {candidate.name} - он был канцлером в прошлом ходу")
            if candidate.dead:
                return Result.error(f"Нельзя выбрать {candidate.name} - он мертв")
        self.current_turn_state()["chancellor_candidate"] = action
        warnings = ""
        if self.check_hitler_chancellorship_wins_the_game():
            warnings += "* Если кандидат окажется *🐸 Лидером Мозговых Слизней*, то либералы проиграют игру\n"
        if self.check_next_fas_law_wins_the_game():
            warnings += "* Если президент вместе с канслером примут авторитарный закон, то либералы проиграют игру\n"
        if self.check_chaos_score():
            warnings += f"* Если парламент откажет {candidate.name}, то {president.name} примет следующий закон автоматически\n"
        next_action = self.desribe_next_action()
        if next_action is not None:
            warnings += next_action + "\n"
        msg = f"Президент {president.name} выбрал {candidate.name} кандидатом в канцлеры в этом ходу\n{warnings}Утвердить?"
        r = Result.notify_all(msg, State.VOTE, VOTE_MARKUP)
        self.state = State.VOTE
        return r

    def check_president_legislation_is_ready(self):
        if len(self.current_turn_state()["laws_short_list"]) > 0:
            return True
        return False

    def legislation_c(self, user, action):
        r = Game.check_input_values(action, 0, 2)
        if r is not None:
            return r
        chancellor = self.get_current_chancellor()
        president = self.get_current_president()
        if user['id'] != chancellor.id:
            return Result.error(f"Подождите пока канслер примет решение")
        self.current_turn_state()["laws_short_list"] = copy.deepcopy(self.current_turn_state()["laws_big_list"])
        self.laws_discard.append(self.current_turn_state()["laws_short_list"][action])
        del self.current_turn_state()["laws_short_list"][action]
        laws_descr = self.current_turn_state()["laws_short_list"][0]["description"] + " и " + self.current_turn_state()["laws_short_list"][1]["description"]
        r = Result.action("Выбраны законы " + laws_descr)
        laws = copy.deepcopy(self.current_turn_state()["laws_short_list"])
        decoration = self.decorate_laws_list(laws, self.check_veto_option())
        self.state = State.LEGISLATURE_P
        r.msg_to_id(president.id, "Выберите закон для принятия:", State.LEGISLATURE_P, decoration)
        return r

    def legislation_p(self, user, action):
        r = Game.check_input_values(action, -1, 2)
        if r is not None:
            return r
        chancellor = self.get_current_chancellor()
        president = self.get_current_president()
        if user['id'] != president.id:
            return Result.error(f"Подождите пока президент примет решение")
        if action < 0:
            if not self.check_veto_option():
                return False, f"Неверная команда '{action}'"
            if not self.current_turn_state()["veto_p"] is None:
                return False, f"Нельзя назначать вето дважды '{action}'"
            self.current_turn_state()["veto"] = True
            self.current_turn_state()["veto_p"] = True
            r = Result.action(f"Запрошено Вето на законы '{action}'", State.VETO)
            r.msg_to_id(chancellor.id, f"Запрошено Вето на законы '{action}'", State.VETO, VOTE_MARKUP)
            self.state = State.VETO
            return r
        self.current_turn_state()["law"] = self.current_turn_state()["laws_short_list"][action]
        self.laws_in_action.append(self.current_turn_state()["law"])
        if action == 1:
            discarded = 0
        else:
            discarded = 1
        self.laws_discard.append(self.current_turn_state()["laws_short_list"][discarded])
        self.state = State.IMPLEMENTATION
        return Result.notify_all("Выбран закон " + self.current_turn_state()["law"]["description"], State.IMPLEMENTATION)

    def veto(self, user, action):
        r = Game.check_input_values(action, -1, 1)
        if r is not None:
            return r
        chancellor = self.get_current_chancellor()
        president = self.get_current_president()
        if user['id'] == chancellor.id:
            return Result.error(f"Подождите пока канслер примет решение")
        self.current_turn_state()["veto_c"] = action
        r = Result()
        if action == 1:
            r = Result.action(f"Принят голос за наложение вето")
            r.notify_all_others(f"Президент и канслер наложили вето на все законы")
            self.current_turn_state()["chaos_score"] += 1
            self.state = State.IMPLEMENTATION
        else:
            r = Result.action(f"Принят голос притив наложения вето")
            r.notify_all_others(f"Канслер отклонил наложение вето на все законы")
            laws = copy.deepcopy(self.current_turn_state()["laws_short_list"])
            decoration = self.decorate_laws_list(laws)
            r.msg_to_id(president.id, "Выберите закон для принятия:", State.LEGISLATURE_P, decoration)
            self.state = State.LEGISLATURE_P
        return r

    def vote(self, user, vote) -> Result:
        r = Game.check_input_values(vote, -1, 1)
        if r is not None:
            return r
        player = self.get_player_by_id(user['id'])
        if player is None:
            return Result.error("Вы не участвуете в игре!")
        candidate = self.n[self.current_turn_state()["chancellor_candidate"]]
        self.current_turn_state()["votes"][player.num] = vote
        if vote > 0:
            voted_name = "Принят голос за канцлера " + candidate.name
        else:
            voted_name = "Принят голос против канцлера " + candidate.name
        return Result.action(voted_name)

    def implement_votes(self):
        result = 0
        for key, p in self.n.items():
            vote = self.current_turn_state()["votes"][key]
            result += vote
        if result > 0:
            self.current_turn_state()["chancellor"] = self.current_turn_state()["chancellor_candidate"]
            chancellor = self.get_current_chancellor()
            if self.check_victory():
                self.state = State.END_GAME
                return Result.notify_all(f"{self.n[self.current_turn_state()['chancellor']].name} оказался Гитлером!")
            self.current_turn_state()["laws_big_list"] += self.pop_laws(3)
            decoration = self.decorate_laws_list(self.current_turn_state()["laws_big_list"])
            msg = "Вас выбрали Канцлером!\nСписок законов на увержедние (вы можете отклонить один из них):"
            r = Result.notify_all(f"{chancellor.name} избран канцлером")
            r.msg_to_id(chancellor.id, msg, State.LEGISLATURE_C, decoration)
            self.state = State.LEGISLATURE_C
            return r
        self.current_turn_state()["chaos_score"] += 1
        self.state = State.IMPLEMENTATION
        r = Result.notify_all(f"{self.n[self.current_turn_state()['chancellor_candidate']].name} отвергнут как кандидат")
        r.trigger_action()
        return r

    def chaos_popup_law(self):
        popped = self.pop_laws(1)
        self.current_turn_state()["chaos_score"] = 0
        self.current_turn_state()["law"] = popped[0]
        self.laws_in_action.append(self.current_turn_state()["law"])
        return self.current_turn_state()["law"]

    def check_veto_option(self):
        lib, fas = self.count_laws()
        n = fas
        if self.current_turn_state()["veto"] or not self.current_turn_state()["veto_p"] is None:
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
        return self.current_turn_state()['chaos_score'] >= 2

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
            return "При принятии следующего авторитарного закона у президента появится возможность посмотреть следующие 3 закона"
        if action == Actions.EXECUTION:
            return "При принятии следующего авторитарного закона у президента появится власть казнить одного игрока"
        if action == Actions.INVESTIGATE:
            return "При принятии следующего авторитарного закона у президента появится возможность проверить лояльность одного игрока"
        if action == Actions.ELECTION:
            return "При принятии следующего авторитарного закона у президента появится возможность назначить внеочередного президента"
        return None

    def action(self, user, action) -> Result:
        r = Game.check_input_values(action, 1, self.len)
        if r is not None:
            return r
        president = self.get_current_president()
        if user['id'] != president.id:
            return Result.error("Подождите действия президента")
        target = self.n[action]
        lib, fas = self.count_laws()
        action_type = self.select_action(fas)
        if action_type == Actions.INVESTIGATE:
            self.current_turn_state()["action"] = action
            role = target.role
            if role == Roles.LIBERAL:
                msg = f'Проверка показала, что {target.name} - либерал'
            else:
                msg = f'Проверка показала, что {target.name} - фашист'
            self.state = State.NEW_TURN
            return Result.action(msg, State.NEW_TURN)
        if action_type == Actions.ELECTION:
            if president.id == target.id:
                return Result.error(f'Нельзя назначить себя экстренным президентом')
            self.current_turn_state()["action"] = action
            self.extra_turn_president = action
            self.state = State.NEW_TURN
            return Result.notify_all(f"Президент {president.name} назначил экстренного президента. В следующем ходу {target.name} будет президентом вне очереди", State.NEW_TURN)
        if action_type == Actions.EXECUTION:
            self.current_turn_state()["action"] = action
            target.dead = True
            self.check_victory()
            if target.role == Roles.HITLER:
                self.state = State.END_GAME
                return Result.notify_all(f'{target.name} приговорен к расстрелу. {target.name} оказался Гитлером! Либералы победили', State.END_GAME)
            self.state = State.NEW_TURN
            return Result.notify_all(f'Президент {president.name} приговорил {target.name} приговорен к расстрелу', State.NEW_TURN)
        return Result.error(f"Неизвестное действие {action_type}")

    def implement_action(self) -> Result:
        lib, fas = self.count_laws()
        msg_all = ""
        if self.current_turn_state()["law"] is None:
            if self.check_chaos_score():
                law = self.chaos_popup_law()
                msg_all += f"Народ недоволен бездействием парламента! Народ потребовал принятия закона {law['description']}"
                if self.current_turn_state()["law"]["type"] == Law.LIBERAL:
                    self.state = State.NEW_TURN
                    r = Result.notify_all(msg_all, State.NEW_TURN)
                    r.trigger_action()
                    return r
            else:
                self.current_turn_state()["action"] = 0
                self.state = State.NEW_TURN
                r = Result.notify_all(f"В этом ходу не принято ни одного закона. Народ недовлен на {self.current_turn_state()['chaos_score']}/3", State.NEW_TURN)
                r.trigger_action()
                return r
        elif self.current_turn_state()["law"]["type"] == Law.LIBERAL:
            self.current_turn_state()["action"] = 0
            self.state = State.NEW_TURN
            r = Result.notify_all(f"В этом ходу был принят либеральный закон {self.current_turn_state()['law']['description']}", State.NEW_TURN)
            r.trigger_action()
            return r
        else:
            msg_all += f'Принят закон: {self.current_turn_state()["law"]["description"]}'
        action = self.select_action(fas)
        president = self.get_current_president()
        if action is Actions.PEEK:
            self.current_turn_state()["action"] = 0
            r = Result.notify_all(f'{msg_all}\nЭтот закон дал президенту возможность подсмотреть следующие 3 закона', State.NEW_TURN)
            peeked_result = self.view_laws(3)
            peeked_str = '\n'.join([l["description"] for l in peeked_result])
            r.msg_to_id(president.id, f"Следующие 3 закона в колоде:\n{peeked_str}", State.NEW_TURN)
            r.trigger_action()
            self.state = State.NEW_TURN
            return r
        if action == Actions.INVESTIGATE:
            buttons = self.get_buttons_list(exclude_id=president.id)
            r = Result.notify_all(f'{msg_all}\nЭтот закон дал президенту возможность проверить одного игрока', State.IMPLEMENTATION_ACTION)
            r.msg_to_id(president.id, "Выберите игрока на проверку", State.IMPLEMENTATION_ACTION, buttons)
            self.state = State.IMPLEMENTATION_ACTION
            return r
        if action == Actions.ELECTION:
            buttons = self.get_buttons_list(exclude_id=president.id, exclude_dead=True)
            r = Result.notify_all(f'{msg_all}\nЭтот закон дал президенту возможность назначить следующего внеочередного президента', State.IMPLEMENTATION_ACTION)
            r.msg_to_id(president.id, "Выберите следующего президента", State.IMPLEMENTATION_ACTION, buttons)
            self.state = State.IMPLEMENTATION_ACTION
            return r
        if action == Actions.EXECUTION:
            buttons = self.get_buttons_list(exclude_id=president.id, exclude_dead=True)
            r = Result.notify_all(f'{msg_all}\nЭтот закон дал президенту возможность растрелять одного игрока', State.IMPLEMENTATION_ACTION)
            r.msg_to_id(president.id, "Выберите игрока на растрел", State.IMPLEMENTATION_ACTION, buttons)
            self.state = State.IMPLEMENTATION_ACTION
            return r
        # action is None
        self.current_turn_state()["action"] = 0
        self.state = State.NEW_TURN
        r = Result.notify_all(f'{msg_all}\nЭтот закон не дает дополнительных полномочий правительству', State.NEW_TURN)
        r.trigger_action()
        return r

    def implement_legislature(self):
        pass

    def get_current_president(self) -> Player:
        return self.n[self.current_turn_state()['president']]

    def get_current_chancellor(self) -> Player:
        return self.n[self.current_turn_state()['chancellor']]

    def decorate_laws_list(self, laws, veto=False):
        list = []
        i = 0
        for l in laws:
            item = [(str(l["description"]), i)]
            i += 1
            list.append(item)
        if veto:
            item = [("Предолжить наложить вето", -1)]
            list.append(item)
        return list
