import logging
import random
import json
import copy
import math
from enum import Enum
from datetime import datetime
from player import Player
from game import Game
from util import *
random.seed(datetime.now())


class Roles(Enum):
    def toJSON(self):
        return str(self)
    GOOD = "👮 Хороший коп"
    AGENT = "🕵 Комиссар"
    BAD = "💰 Плохой коп"
    KINGPIN = "😈 Вор в законе"

# Globals
DEFAULT_CARDS = [
    Roles.AGENT,
    Roles.KINGPIN,
    Roles.GOOD,
    Roles.BAD,
]

class Equipment(Enum):
    def toJSON(self):
        return str(self)
    TRUTH_SERUM = "💉 сыворотка правды"
    FLASHBANG = "💣 Светошумовая граната"
    BLACKMAIL = "👹 шантаж"
    RESTRAINING_ORDER = "📑 приказ начальства"
    K_9_UNIT = "🐶 служебная собака"
    POLYGRAPTH = "📈 полиграф"
    PLANTED_EVIDENCE = "🔪 подброшенная улика"
    METAL_DETECTOR = "🔧 металоискатель"
    EVIDENCE_BAG = "💼 пакет для улик"
    REPORT_AUDIT = "📝 прокурорская проверка"
    DEFIBRILLATOR = "🩺 дефибриллятор"
    SURVEILLANCE_CAMERA = "🎥 скрытое видеонаблюдение"
    TAZER = "⚡ электрошокер"
    COFFEE = "☕️ кофе"
    BRIBE = "💵 взятка"
    WIRETAP = "🎧 прослушка"
    
EQUIPMENT_INIT_DECK = [
    Equipment.TRUTH_SERUM,
    Equipment.FLASHBANG,
    Equipment.BLACKMAIL,
    Equipment.RESTRAINING_ORDER,
    Equipment.K_9_UNIT,
    Equipment.POLYGRAPTH,
    Equipment.PLANTED_EVIDENCE,
    # Equipment.METAL_DETECTOR,
    Equipment.EVIDENCE_BAG,
    # Equipment.REPORT_AUDIT,
    Equipment.DEFIBRILLATOR,
    Equipment.SURVEILLANCE_CAMERA,
    Equipment.TAZER,
    # Equipment.COFFEE,
    # Equipment.BRIBE,
    Equipment.WIRETAP,
]

EQUIPMENT_DESCRIPTION = {
    Equipment.TRUTH_SERUM: "💉 сыворотка правды: выбранный игрок открывает всем одну свою карту",
    Equipment.FLASHBANG: "💣 Светошумовая граната: закрыть и перемешать все свои открытые карты",
    Equipment.BLACKMAIL: "👹 шантаж: поменять местами две карты у двух других игроков",
    Equipment.RESTRAINING_ORDER: "📑 приказ начальства: выбранный игрок с пистолетом обязан выбрать другую цель",
    Equipment.K_9_UNIT: "🐶 служебная собака: выбранный игрок с пистолетом бросает пистолет",
    Equipment.POLYGRAPTH: "📈 полиграф: выбранный игрок показывает вам все свои карты. А вы показываете ему все свои",
    Equipment.PLANTED_EVIDENCE: "🔪 подброшенная улика: меняет у выбранного игрока все карты Хорошего Копа на карты Плохого Копа и наоборот",
    Equipment.METAL_DETECTOR: "🔧 металоискатель: проверить по одной карте у всех игроков с пистолетом",
    Equipment.EVIDENCE_BAG: "💼 пакет для улик: заберите предмет у выбранного игрока (не пистолет)",
    Equipment.REPORT_AUDIT: "📝 прокурорская проверка: каждый игрок, у которого еще нет открытых карт, открывает одну карту",
    Equipment.DEFIBRILLATOR: "🩺 дефибриллятор: оживить мертвого игрока", #TODO и поменять карты на одну из карт
    Equipment.SURVEILLANCE_CAMERA: "🎥 скрытое видеонаблюдение: посмотреть карту, которую последний раз смотрел другой игрок",
    Equipment.TAZER: "⚡ электрошокер: забрать пистолет у выбранного игрока",
    Equipment.COFFEE: "☕ кофе: сделать два действия",
    Equipment.BRIBE: "💵 взятка: Посмотреть карту дрого игрока. После этого можно поменять эту его карту на любую свою карту",
    Equipment.WIRETAP: "🎧 прослушка: вы узнаете результат следующей проверки карты другим игроком",
}

class Actions(Enum):
    def toJSON(self):
        return str(self)
    INVESTIGATE = "проверить"
    EQUIP = "экипировка"
    ARM = "вооружиться"
    SHOOT = "выстрелить"
    AIM = "прицелиться"
    USE = "использовать предмет"

class States(Enum):
    def toJSON(self):
        return str(self)
    INIT = "INIT"
    ACTION_SELECT = "ACTION_SELECT"
    INVESTIGATE = "INVESTIGATE"
    INVESTIGATE_CARD_SELECT = "INVESTIGATE_CARD_SELECT"
    FLIP_ONE_CARD = "FLIP_ONE_CARD"
    AIM = "AIM"
    USE = "USE"
    USE_PLAYER_SELECT = "USE_PLAYER_SELECT"
    USE_CARD_SELECT = "USE_CARD_SELECT"
    USE_ACTION_SELECT = "USE_ACTION_SELECT"
    DISCARD = "DISCARD"
    END_TURN = "END_TURN"
    END_GAME = "END_GAME"

ACTION_DICT = {
    1: Actions.INVESTIGATE,
    2: Actions.EQUIP,
    3: Actions.ARM,
    4: Actions.SHOOT,
    5: Actions.AIM,
    6: Actions.USE,
}


class CopPlayer(Player):
    cards = {}
    public_cards = {}
    gun = False
    aim = -1
    wounded = False
    equipment = []

    def has_more_than_one_item(self):
        return len(self.equipment) > 1

    def get_equipment(self):
        return self.equipment[0]

    def has_equipment(self):
        return len(self.equipment) > 0

    def get_card_numbers_list(self, public=None):
        ret = []
        for key, value in self.cards.items():
            if public is None or self.public_cards[key] == public:
                ret.append(key)
        return ret

    def get_cards_list(self, public=None):
        ret = []
        for key, value in self.cards.items():
            if public is None or self.public_cards[key] == public:
                ret.append(value)
        return ret

    def get_cards_dict(self, public=None):
        ret = {}
        for key, value in self.cards.items():
            if public is None or self.public_cards[key] == public:
                ret[key] = value
        return ret

    def check_has_3_cards(self):
        if len(self.cards) != 3:
            return False
        if 1 not in self.cards:
            return False
        if 2 not in self.cards:
            return False
        if 3 not in self.cards:
            return False
        return isinstance(self.cards[1], Roles) and isinstance(self.cards[2], Roles) and isinstance(self.cards[3], Roles)

    def flip_all_up(self):
        self.public_cards[1] = True
        self.public_cards[2] = True
        self.public_cards[3] = True

    def has_unfliped_cards(self):
        if not self.public_cards[1] or not self.public_cards[2] or not self.public_cards[3]:
            return True
        return False

    def check_winner(self):
        cards = 0
        for key, value in self.cards.items():
            if value == Roles.AGENT:
                cards += 1
            if value == Roles.KINGPIN:
                cards += 1
        return cards > 1

    def check_leader(self):
        for key, value in self.cards.items():
            if value == Roles.AGENT:
                return True
            if value == Roles.KINGPIN:
                return True
        return False

    def check_agent(self):
        for key, value in self.cards.items():
            if value == Roles.AGENT:
                return True
        return False

    def check_kingpin(self):
        for key, value in self.cards.items():
            if value == Roles.KINGPIN:
                return True
        return False

    def team(self):
        good, bad = 0, 0
        for key, value in self.cards.items():
            if value == Roles.AGENT:
                return Roles.GOOD
            if value == Roles.KINGPIN:
                return Roles.BAD
            if value == Roles.GOOD:
                good += 1
            if value == Roles.BAD:
                bad += 1
        if good >= bad:
            return Roles.GOOD
        elif good <= bad:
            return Roles.BAD
        return None

    def role(self):
        good, bad = 0, 0
        for key, value in self.cards.items():
            if value == Roles.AGENT:
                return Roles.AGENT
            if value == Roles.KINGPIN:
                return Roles.KINGPIN
            if value == Roles.GOOD:
                good += 1
            if value == Roles.BAD:
                bad += 1
        if good > bad:
            return Roles.GOOD
        elif good < bad:
            return Roles.BAD
        return None

    def set_cards(self, c1: Roles, c2: Roles, c3: Roles):
        self.cards = {
            1: c1,
            2: c2,
            3: c3,
        }
        self.public_cards = {
            1: False,
            2: False,
            3: False,
        }


class CopGame(Game):

    OPTIONS_VIEW_KNOWN_FACTS = True
    OPTIONS_USE_EQIPMENT = True
    equipment_deck = []
    last_investigated_card = None
    wiretap_id = None

    # Abstract methods redef
    def get_init_message(self, p: Player):
        p: CopPlayer
        role = p.role()
        cards_str = CopGame.decorate_cards_dict(p.get_cards_dict())
        if self.OPTIONS_USE_EQIPMENT:
            equipment = p.get_equipment()
            eq_msg = f"\nТакже у вас есть {EQUIPMENT_DESCRIPTION[equipment]}"
        else:
            eq_msg = ""
        if role == Roles.KINGPIN:
            return f"Вы Вор в законе. Вы лидер Плохих копов\nВаши карты: {cards_str}{eq_msg}"
        if role == Roles.AGENT:
            return f"Вы Комиссар. Вы лидер Хороших копов\nВаши карты: {cards_str}{eq_msg}"
        if role == Roles.GOOD:
            return f"Вы Хороший коп\nВаши карты: {cards_str}{eq_msg}"
        if role == Roles.BAD:
            return f"Вы Плохой коп\nВаши карты: {cards_str}{eq_msg}"

    def do_next_step(self, unstack=False) -> Result:
        if self.check_next_step():
            s_state = self.state
            r = self._do_next_step(unstack=unstack)
            e_state = self.state
            if e_state is None:
                e_state = "None"
            else:
                e_state = e_state.value
            self.current_turn_state()["logs"].append((f"next_action state {s_state.value}->{e_state}", r))
            return r
        return Result()

    def _do_next_step(self, unstack=False) -> Result:
        #self.current_turn_state()['action_done']
        if self.state == States.INIT:
            raise None
        if (self.state == States.ACTION_SELECT
                or self.state == States.FLIP_ONE_CARD
                or self.state == States.INVESTIGATE
                or self.state == States.INVESTIGATE_CARD_SELECT):
            self.state = States.AIM
        if (self.state == States.USE
                or self.state == States.USE_CARD_SELECT
                or self.state == States.USE_ACTION_SELECT
                or self.state == States.USE_PLAYER_SELECT):
            r = self._use_do_next_step()
            if r is not None:
                return r
            self.state = States.AIM
        if self.state == States.DISCARD:
            r = Result()
            for p in self.pl:
                p: CopPlayer
                if p.has_more_than_one_item():
                    r.msg_to_id(p.id, "У вас слишком много предметов. Нужно оставить только один.", States.DISCARD, self.get_discard_actions(p))
            if len(r.next_actions) > 0:
                return r
            else:
                self.state = States.AIM
        if self.state == States.AIM:
            active_player = self.n[self.current_turn_state()['active_player']]
            active_player: CopPlayer
            if 'COFFEE' in self.current_turn_state() and not self.current_turn_state()['COFFEE']:
                self.current_turn_state()['COFFEE'] = True
                self.current_turn_state()['action_done'] = False
                return Result.action("☕️ кофе помогает вам совершить второе действие в этом ходу:", States.USE_ACTION_SELECT, self._main_action_options())
            if active_player.gun:
                return Result.action_by_id(active_player.id, "В кого направить пистолет?", States.AIM, self.get_list_of_aimable_players(active_player))
            self.state = States.END_TURN
        if self.state == States.END_TURN:
            return self.new_turn()
        if self.state == States.END_GAME:
            self.state = None
            return self.get_victory_message()
        if self.state is None:
            return Result()
        raise Exception(f"not yet implemented - {self.state}")

    def check_next_step(self) -> bool:
        #self.current_turn_state()['action_done']
        if self.state == States.INIT:
            return False
        if (self.state == States.ACTION_SELECT
                or self.state == States.FLIP_ONE_CARD
                or self.state == States.INVESTIGATE
                or self.state == States.INVESTIGATE_CARD_SELECT):
            return self.current_turn_state()['action_done']
        if self.state == States.AIM:
            return True
        if self.state == States.DISCARD:
            return True
        if (self.state == States.END_TURN
                or self.state == States.END_GAME):
            return True
        if (self.state == States.USE
                or self.state == States.USE_PLAYER_SELECT
                or self.state == States.USE_ACTION_SELECT
                or self.state == States.USE_CARD_SELECT):
            return self.check_use_is_done()
        if self.state is None:
            return False
        raise Exception(f"not yet implemented - {self.state}")

    def do_action(self, user, action) -> Result:
        s_state = self.state
        r = self._do_action(user, action)
        self.current_turn_state()["logs"].append((f"user {str(user)} action {str(action)} on state {s_state.value}->{self.state.value}", r))
        return r

    def _do_action(self, user, action) -> Result:
        #self.current_turn_state()['action_done']
        if (self.state == States.INIT
                or self.state == States.END_TURN
                or self.state == States.END_GAME):
            return None
        if self.state == States.ACTION_SELECT:
            return self.main_action(user, action)
        if self.state == States.FLIP_ONE_CARD:
            return self.self_card_flip(user, action)
        if self.state == States.INVESTIGATE:
            return self.investigate(user, action)
        if self.state == States.INVESTIGATE_CARD_SELECT:
            return self.investigate_card_pick(user, action)
        if self.state == States.AIM:
            return self.aim(user, action)
        if self.state == States.DISCARD:
            return self.discard(user, action)
        if (self.state == States.USE
                or self.state == States.USE_PLAYER_SELECT
                or self.state == States.USE_ACTION_SELECT
                or self.state == States.USE_CARD_SELECT):
            return self.use_action(user, action)
        if self.state is None:
            return None
        raise Exception(f"not yet implemented - {self.state}")

    # end Abstract methods
    def shuffle_roles(self):
        num_cards = len(self.pl) * 3
        roles = copy.deepcopy(DEFAULT_CARDS)
        while len(roles) < num_cards:
            roles.append(Roles.GOOD)
            roles.append(Roles.BAD)
        random.shuffle(roles)
        logging.info("Roles are " + str(roles))
        return roles

    # end Abstract methods
    def shuffle_equipment(self):
        num_cards = len(self.pl) * 3
        eq = copy.deepcopy(EQUIPMENT_INIT_DECK)
        random.shuffle(eq)
        logging.info("Equipment is " + str(eq))
        self.equipment_deck = eq
        return eq

    def pop_equipment(self) -> Equipment:
        return self.equipment_deck.pop()

    def _check_cards_dealt_right(self):
        kingpins, agents = 0, 0
        for p in self.pl:
            p: CopPlayer
            if not p.check_has_3_cards():
                return False
            if p.check_winner():
                return False
            if p.check_agent():
                agents += 1
            if p.check_kingpin():
                kingpins += 1
        if kingpins != 1 or agents != 1:
            return False
        return True

    # GAME PART
    def init_game(self, cards=None, shufle=True, starting_player=None) -> Result:
        super().init_game(player_class=CopPlayer)
        self.state = States.INIT
        self.max_guns = int(math.ceil(self.len/2))
        self.last_investigated_card = None
        self.wiretap_id = None

        if cards is None:
            cards = self.shuffle_roles()

        while not self._check_cards_dealt_right():
            # перемешаем роли
            if shufle:
                cards = self.shuffle_roles()
            # раздаем роли
            i = 0
            for p in self.pl:
                p: CopPlayer
                p.set_cards(cards[i], cards[i+1], cards[i+2])
                i += 3
        self.shuffle_equipment()
        if self.OPTIONS_USE_EQIPMENT:
            for p in self.pl:
                p: CopPlayer
                p.equipment = [self.pop_equipment()]
        return self.new_turn(starting_player)

    def check_victory(self):
        agent = self.find_agent();
        kingpin = self.find_kingpin();
        if agent.id == kingpin.id:
            self.status = True, agent.id, f"{agent.name} собрал обе лидерские карты! {agent.name} победил!!"
            self.state = States.END_GAME
            return True
        if agent.dead and kingpin.dead:
            self.status = True, None, "Ничья! Оба лидера мертвы!"
            self.state = States.END_GAME
            return True
        if agent.dead:
            self.status = True, False, "Плохие копы победили! Комиссар мертв!"
            self.state = States.END_GAME
            return True
        if kingpin.dead:
            self.status = True, True, "Хорошие копы победили! Вор в законе мертв!"
            self.state = States.END_GAME
            return True
        return False

    def get_victory_message(self):
        if not self.check_victory():
            return None
        done, winners, msg = self.status
        return Result.notify_all(msg)

    def pick_next_active_player(self, starting_player=None):
        if self.current_turn < 1:
            if starting_player is not None:
                return starting_player
            return random.randint(1, self.len)
        pl = self.current_turn_state()["active_player"] + 1
        if pl > self.len:
            pl = 1
        while self.n[pl].dead:
            pl += 1
            if pl > self.len:
                pl = 1
        return pl

    def find_enemy_leader(self, team: Roles) -> CopPlayer:
        if team == Roles.GOOD:
            return self.find_kingpin()
        if team == Roles.BAD:
            return self.find_agent()
        return None

    def find_team_leader(self, team: Roles) -> CopPlayer:
        if team == Roles.BAD:
            return self.find_kingpin()
        if team == Roles.GOOD:
            return self.find_agent()
        return None

    def find_agent(self):
        for p in self.pl:
            p: CopPlayer
            if p.check_agent():
                return p
        return None

    def find_kingpin(self):
        for p in self.pl:
            p: CopPlayer
            if p.check_kingpin():
                return p
        return None

    def new_turn(self, starting_player=None):
        active_player = self.pick_next_active_player(starting_player)
        if self.current_turn > 1:
            victory = self.check_victory()
            if victory:
                return False
        self.current_turn += 1
        turn_obj = {
            "active_player": active_player,
            "action": {},
            "logs": [],
            "action_done": False,
            "aim_done": False,
            "action_left": States.ACTION_SELECT,
        }
        if self.current_turn == 1:
            turn_obj["known_facts"] = {}
            for p in self.pl:
                p: CopPlayer
                turn_obj["known_facts"][p.num] = {}
                for key, p_of in self.n.items():
                    turn_obj["known_facts"][p.num][p_of.num] = {}
                for i, c in p.cards.items():
                    turn_obj["known_facts"][p.num][p.num][i] = c
        else:
            turn_obj["known_facts"] = copy.deepcopy(self.prev_turn_state()["known_facts"])
        self.game_state[self.current_turn] = turn_obj
        self.state = States.ACTION_SELECT
        return self._new_turn_result(self.n[active_player])

    def _new_turn_result(self, active_player: CopPlayer):
        # 1: Actions.INVESTIGATE,
        # 2: Actions.EQUIP,
        # 3: Actions.ARM,
        # 4: Actions.SHOOT,
        # 5: Actions.AIM,
        # 6: Actions.USE,
        options = self._main_action_options(active_player)
        status_messages = self.get_status_message(active_player)
        r = Result()
        for key, pl in self.n.items():
            if pl.id == active_player.id:
                r.msg_to_id(id=active_player.id, msg=status_messages[key], expected_action=States.ACTION_SELECT, commands=options)
            else:
                r.msg_to_id(id=pl.id, msg=status_messages[key])
        return r

    def _main_action_options(self, active_player: CopPlayer) -> list:
        options = [
            [("🔍 Проверить", 1)],
        ]
        equip = [("🛅 Экипироваться", 2)]
        arm = [("🔫 Вооружиться", 3)]
        shoot = [("🔥 Выстрелить", 4)]
        aim = [("🎯 Прицелиться", 5)]
        if self.OPTIONS_USE_EQIPMENT:
            options.append(equip)
        if active_player.gun:
            options.append(shoot)
            options.append(aim)
        else:
            options.append(arm)
        if active_player.has_equipment():
            use = [(active_player.get_equipment().value, 6)]
            options.append(use)
        return options

    def get_status_message(self, active_player: CopPlayer) -> {}:
        msg = f"Новый ход\nНа руках *{self.get_number_of_guns()}/{self.max_guns}* 🔫 пистолетов\n"
        ret = {}
        separator = "\n\t"
        for key, pl_viewer in self.n.items():
            pl_viewer: CopPlayer
            ret[key] = copy.copy(msg)
            if pl_viewer.id == active_player.id:
                ret[key] += "Ваш ход!\n\n"
            else:
                ret[key] += f"Ходит *{active_player.name}*!\n\n"
            ret[key] += "Список игроков:\n"
            dead = ""
            for i, ppl in self.n.items():
                ppl: CopPlayer
                public_cards = ppl.get_cards_dict(public=True)
                known_extra = self.get_extra_known_cards(pl_viewer, ppl)
                tmp = ""
                tmp += f"{i}:*{ppl.name}*"
                if ppl.wounded:
                    tmp+= " 🚑 ранен"
                tmp += f"\n"
                if len(public_cards) > 0:
                    tmp += f"\tОткрытые карты:\n {CopGame.decorate_cards_dict(public_cards, separator=separator)}\n"
                if ppl.num != key:
                    if len(public_cards) == 3:
                        tmp += f"\tЭто значит, что *{ppl.name}* - *{ppl.role().value}*\n"
                    else:
                        if self.OPTIONS_VIEW_KNOWN_FACTS:
                            if len(known_extra) > 0:
                                tmp += f"\tВы раньше подсматривали:\n {CopGame.decorate_cards_dict(known_extra, separator=separator)}\n"
                                #TODO - вставить подсказку?
                else:
                    closed_cards = ppl.get_cards_dict(public=False)
                    if len(closed_cards):
                        tmp += f"\tЗакрытые карты:\n {CopGame.decorate_cards_dict(closed_cards, separator=separator)}\n"
                    tmp += f"\tВы *{ppl.role().value}*\n"
                if ppl.dead:
                    dead += tmp
                else:
                    if ppl.has_equipment():
                        if ppl.num == key:
                            tmp += f"\tУ вас есть *{EQUIPMENT_DESCRIPTION[ppl.get_equipment()]}*\n"
                        else:
                            tmp += f"\tУ {ppl.name} есть какой-то предмет\n"
                    if ppl.gun:
                        if ppl.aim > 0:
                            tmp += f"\tВ руках у {ppl.name} *🔫 пистолет*, он нацелен на {self.n[ppl.aim].name}\n"
                        else:
                            tmp += f"\tВ руках у {ppl.name} *🔫 пистолет*, он не нацелен\n"
                    ret[key] += tmp
            if len(dead) > 0:
                ret[key] += "Умершие игроки:"
                ret[key] += dead
        return ret

    def get_list_of_investigatable_players(self, by: CopPlayer):
        ret_list = []
        players_list = []
        for p in self.pl:
            p: CopPlayer
            if p.id != by.id and not p.dead and p.has_unfliped_cards():
                tuple = (p.name, str(p.num))
                players_list.append(tuple)
        ret_list += chunks(players_list, 3)
        return ret_list

    def get_list_of_aimable_players(self, by: CopPlayer, exclude_ids = []):
        ret_list = []
        players_list = []
        for p in self.pl:
            p: CopPlayer
            if p.id != by.id and not p.dead and p.id not in exclude_ids:
                tuple = (p.name, str(p.num))
                players_list.append(tuple)
        ret_list += chunks(players_list, 3)
        return ret_list

    def get_list_of_players_with_items(self, by: CopPlayer):
        ret_list = []
        players_list = []
        for p in self.pl:
            p: CopPlayer
            if p.id != by.id and not p.dead and p.has_equipment():
                tuple = (p.name, str(p.num))
                players_list.append(tuple)
        ret_list += chunks(players_list, 3)
        return ret_list

    def get_list_of_players_with_guns(self, by: CopPlayer=None):
        ret_list = []
        players_list = []
        by_id = -1
        if by is not None:
            by_id = by.id
        for p in self.pl:
            p: CopPlayer
            if p.id != by_id and not p.dead and p.gun:
                tuple = (p.name, str(p.num))
                players_list.append(tuple)
        ret_list += chunks(players_list, 3)
        return ret_list

    def main_action(self, user, action):
        r = Game.check_input_values(action, 1, len(ACTION_DICT.keys()))
        if r is not None:
            return r
        active_player = self.n[self.current_turn_state()['active_player']]
        active_player: CopPlayer
        if user['id'] != active_player.id:
            return Result.error(f'{str(user)} сейчас не ходит!')
        action_type = ACTION_DICT[action]
        self.current_turn_state()["action"]["type"] = action_type
        if action_type == Actions.INVESTIGATE:
            investigatable_players = self.get_list_of_investigatable_players(active_player)
            if len(investigatable_players) == 0:
                return Result.error(f"Нет ни одной карты чтобы проверить")
            self.state = States.INVESTIGATE
            return Result.action("Выберите игрока для проверки", States.INVESTIGATE, investigatable_players)
        if action_type == Actions.EQUIP:
            new_item = self.pop_equipment()
            self.current_turn_state()["action"]["EQUIP"] = new_item
            self.current_turn_state()['action_done'] = True
            active_player.equipment.append(new_item)
            self.state = States.DISCARD
            r = Result.action(f"Вы нашли новый предмет:\n{EQUIPMENT_DESCRIPTION[new_item]}", States.AIM)
            r.notify_all_others(f"У {active_player.name} есть новый предмет")
            return r
        if action_type == Actions.ARM:
            if active_player.gun:
                return Result.error(f"У вас уже есть 🔫 пистолет")
            if self.get_number_of_guns() >= self.max_guns:
                return Result.error(f"Не осталось ни одного свободного пистолета - все 🔫 пистолеты на руках")
            active_player.gun = True
            unflipped_cards = active_player.get_cards_dict(public=False)
            if len(unflipped_cards) <= 1:
                r = Result.action("У вас теперь есть 🔫 пистолет!", States.AIM)
                r.notify_all_others(f"У {active_player.name} есть 🔫 пистолет!")
                if len(unflipped_cards) == 1:
                    # only one card to flip
                    unflipped_card_no = next(iter(unflipped_cards))
                    active_player.flip_all_up()
                    unflipped_card = active_player.cards[unflipped_card_no]
                    r.notify_all_others(f"У {active_player} есть 🔫 пистолет!\n{active_player} раскрыл карту *\"{unflipped_card.value}\"*\nтеперь известно, что {active_player} - {active_player.role().value}")
                # no cards to flip, gun is free
                self.current_turn_state()['action_done'] = True
                self.current_turn_state()['action_left'] = None
                self.state = States.AIM
                return r
            self.state = States.FLIP_ONE_CARD
            r = Result.action("У вас теперь есть 🔫 пистолет!\nВам нужно раскрыть одну из своих карт", States.FLIP_ONE_CARD, self.get_card_description_buttons(unflipped_cards))
            r.notify_all_others(f"У {active_player.name} есть пистолет!")
            return r
        if action_type == Actions.SHOOT:
            if not active_player.gun:
                return Result.error("У вас нет 🔫 пистолета!")
            if active_player.aim <= 0:
                return Result.error("Ваш 🔫 пистолет не заряжен!")
            if active_player.aim > self.len:
                return Result.error(f"Ваш 🔫 пистолет направлен в неправильного игрока ({active_player.aim})!")
            target = self.n[active_player.aim]
            self.current_turn_state()["action"]["target"] = active_player.aim
            target: CopPlayer
            if target.dead:
                return Result.error(f"{target.name} уже мертв!")
            target.flip_all_up()
            if target.check_leader():
                if not target.wounded:
                    target.wounded = True
                    r = Result.action(f"{target.role().value} {target.name} ранен!")
                    r.notify_all_others(f"{active_player.name} выстрелил в {target.name}!\n{target.role().value} {target.name} ранен!")
                    self.state = States.END_TURN
                    if 'COFFEE' in self.current_turn_state():
                        self.state = States.AIM
                else:
                    target.dead = True
                    target.gun = False
                    r = Result.action(f"{target.role().value} {target.name} убит!")
                    r.game_end = True
                    r.notify_all_others(f"{active_player.name} выстрелил в {target.name}!\n{target.role().value}  {target.name} убит!")
                    self.state = States.END_GAME
                    self.check_victory()
            else:
                target.dead = True
                target.gun = False
                r = Result.action(f"{target.role().value} {target.name} убит!")
                r.notify_all_others(f"{active_player.name} выстрелил в {target.name}!\n{target.role().value} {target.name} убит!")
                self.state = States.END_TURN
                if 'COFFEE' in self.current_turn_state():
                    self.state = States.AIM
            active_player.gun = False
            active_player.aim = -1
            self.current_turn_state()['action_done'] = True
            self.current_turn_state()['action_left'] = None
            return r
        if action_type == Actions.AIM:
            self.state = States.AIM
            return Result()
        if action_type == Actions.USE:
            if not active_player.has_equipment():
                return Result.error("У вас нет никакого предмета!")
            return self.use_item(active_player)
        return Result.error(f"Неверная команда {action}")

    def use_item(self, active_player: CopPlayer) -> Result:
        item = active_player.get_equipment()
        self.current_turn_state()['used_item'] = item
        r = Result.error(f"Предмет {item} не найден")
        if item == Equipment.TRUTH_SERUM:
            # "💉 сыворотка правды: выбранный игрок открывает всем одну свою карту",
            investigatable_players = self.get_list_of_investigatable_players(active_player)
            if len(flatten_buttons(investigatable_players)) < 1:
                return Result.error(f"Не получится использовать 💉 сыворотку правды - все карты у всех игроков известны")
            self.state = States.USE_PLAYER_SELECT
            r = Result.action("Выберите игрока чтобы вколоть ему 💉 сыворотку правды. Игрок откроет всем одну свою карту", States.USE_PLAYER_SELECT, investigatable_players)
        elif item == Equipment.FLASHBANG:
            # "💣 Светошумовая граната: закрыть и перемешать все свои открытые карты",
            active_player.public_cards[1] = False
            active_player.public_cards[2] = False
            active_player.public_cards[3] = False
            cards = copy.deepcopy(active_player.get_cards_list())
            random.shuffle(cards)
            active_player.cards[1] = cards.pop()
            active_player.cards[2] = cards.pop()
            active_player.cards[3] = cards.pop()
            r = Result.action("Вы перемешали все свои карты 💣 Светошумовой гранатой", States.AIM)
            self.state = States.AIM
            r.notify_all_others(f"{active_player.name} перемешал все свои карты 💣 Светошумовой гранатой")
            self.current_turn_state()['action_done'] = True
        elif item == Equipment.BLACKMAIL:
            # "👹 шантаж: поменять местами две карты у двух других игроков",
            aimable_players = self.get_list_of_aimable_players(active_player)
            if len(flatten_buttons(aimable_players)) < 2:
                return Result.error(f"Не получится использовать 👹 шантаж - нет двух доступных игроков")
            self.state = States.USE_PLAYER_SELECT
            r = Result.action("Выберите первого игрока чтобы использовать 👹 шантаж", States.USE_PLAYER_SELECT, aimable_players)
        elif item == Equipment.RESTRAINING_ORDER:
            # "📑 приказ начальства: выбранный игрок с пистолетом обязан выбрать другую цель",
            gunned_players = self.get_list_of_players_with_guns(active_player)
            if len(flatten_buttons(gunned_players)) < 1:
                return Result.error(f"Не получится использовать 📑 приказ начальства - нет игроков с пистолетами")
            self.state = States.USE_PLAYER_SELECT
            r = Result.action("Выберите игрока чтобы использовать 📑 приказ начальства - игрок выберет другую цель", States.USE_PLAYER_SELECT, gunned_players)
        elif item == Equipment.K_9_UNIT:
            # "🐶 служебная собака: выбранный игрок с пистолетом бросает пистолет",
            gunned_players = self.get_list_of_players_with_guns(active_player)
            if len(flatten_buttons(gunned_players)) < 1:
                return Result.error(f"Не получится использовать 🐶 служебную собаку - нет игроков с пистолетами")
            self.state = States.USE_PLAYER_SELECT
            r = Result.action("Выберите игрока чтобы использовать 🐶 служебную собаку - игрок бросит пистолет", States.USE_PLAYER_SELECT, gunned_players)
        elif item == Equipment.POLYGRAPTH:
            # "📈 полиграф: выбранный игрок показывает вам все свои карты. А вы показываете ему все свои",
            investigatable_players = self.get_buttons_list(active_player.id, exclude_dead=True)
            if len(flatten_buttons(investigatable_players)) < 1:
                return Result.error(f"Не получится использовать 📈 полиграф - нет доступных игроков")
            self.state = States.USE_PLAYER_SELECT
            r = Result.action("Выберите игрока чтобы использовать 📈 полиграф. Выбранный игрок покажет вам все свои карты. А вы покажете ему все свои", States.USE_PLAYER_SELECT, investigatable_players)
        elif item == Equipment.PLANTED_EVIDENCE:
            # "🔪 подброшенная улика: меняет у выбранного игрока все карты Хорошего Копа на карты Плохого Копа и наоборот",
            investigatable_players = self.get_buttons_list(active_player.id, exclude_dead=True)
            if len(flatten_buttons(investigatable_players)) < 1:
                return Result.error(f"Не получится использовать 🔪 подброшенную улику - нет доступных игроков")
            self.state = States.USE_PLAYER_SELECT
            r = Result.action("Выберите игрока чтобы использовать 🔪 подброшенную улику. Выбранный игрок поменяет у выбранного игрока все карты Хорошего Копа на карты Плохого Копа и наоборот", States.USE_PLAYER_SELECT, investigatable_players)
        elif item == Equipment.METAL_DETECTOR:
            # "🔧 металоискатель: проверить по одной карте у всех игроков с пистолетом",
            gunned_players = flatten_buttons(self.get_list_of_players_with_guns(active_player))
            if len(gunned_players) < 1:
                return Result.error(f"Не получится использовать 🔧 металоискатель - нет игроков с пистолетами")
            self.current_turn_state()['METAL_DETECTOR'] = gunned_players
            self.current_turn_state()['METAL_DETECTOR_LEFT'] = gunned_players
            r = self.use_metal_detector(active_player)
        elif item == Equipment.EVIDENCE_BAG:
            # "💼 пакет для улик: заберите предмет у выбранного игрока",
            itemed_players = self.get_list_of_players_with_items(active_player)
            if len(flatten_buttons(itemed_players)) < 1:
                return Result.error(f"Не получится использовать 💼 пакет для улик - нет игрока с предметом")
            self.state = States.USE_PLAYER_SELECT
            r = Result.action("Выберите первого игрока чтобы использовать 💼 пакет для улик - и забрать у него предмет", States.USE_PLAYER_SELECT, itemed_players)
        elif item == Equipment.REPORT_AUDIT:
            # "📝 прокурорская проверка: каждый игрок, у которого еще нет открытых карт, открывает одну карту",
            r = Result()
            self.current_turn_state()['REPORT_AUDIT'] = {}
            msg = ""
            for target in self.pl:
                target: CopPlayer
                unflipped_cards = target.get_cards_dict(public=False)
                self.current_turn_state()['REPORT_AUDIT_MSG'] = ""
                self.current_turn_state()['REPORT_AUDIT_MSG_ALL'] = {}
                if len(unflipped_cards) == 3:
                    self.current_turn_state()['REPORT_AUDIT'][target.num] = False
                    r.msg_to_id(target.id, f"{active_player.name} использовал предмет *📝 прокурорская проверка*\n Вам необходимо раскрыть одну из своих карт", States.USE_CARD_SELECT, self.get_card_description_buttons(unflipped_cards))
            if len(r.next_actions) == 0:
                return Result.error(f"Не получится использовать 📝 прокурорскую проверку - нет игроков без открытых карт")
            self.state = States.USE_CARD_SELECT
            return r
        elif item == Equipment.DEFIBRILLATOR:
            # "🩺 дефибриллятор: оживить мертвого игрока",  # TODO и поменять карты на одну из карт
            dead_players = self.get_dead_buttons_list()
            if len(flatten_buttons(dead_players)) < 1:
                return Result.error(f"Не получится использовать 🩺 дефибриллятор - нет мертвых игроков")
            self.state = States.USE_PLAYER_SELECT
            r = Result.action("Выберите игрока чтобы использовать 🩺 дефибриллятор. Это оживит его!", States.USE_PLAYER_SELECT, dead_players)
        elif item == Equipment.SURVEILLANCE_CAMERA:
            # "🎥 скрытое видеонаблюдение: посмотреть карту, которую последний раз смотрел другой игрок",
            if self.last_investigated_card is None:
                return Result.error(f"Не получится использовать 🎥 скрытое видеонаблюдение - в этой игре еще не было проверок")
            self.current_turn_state()['action_done'] = True
            self.state = States.AIM
            r = Result.action(f"Вы использовали 🎥 скрытое видеонаблюдение.\n{self.last_investigated_card}", States.AIM)
            r.notify_all_others(f"{active_player.name} использовал 🎥 скрытое видеонаблюдение. Он узнал результат предыдущей проверки")
        elif item == Equipment.TAZER:
            # "⚡ электрошокер: забрать пистолет у выбранного игрока",
            gunned_players = self.get_list_of_players_with_guns(active_player)
            if len(flatten_buttons(gunned_players)) < 1:
                return Result.error(f"Не получится использовать ⚡ электрошокер - нет игроков с пистолетами")
            self.state = States.USE_PLAYER_SELECT
            r = Result.action("Выберите игрока чтобы использовать ⚡ электрошокер - вы заберете пистолет у этого игрока", States.USE_PLAYER_SELECT, gunned_players)
        elif item == Equipment.COFFEE:
            # "☕️ кофе: прицелиться в друго игрка. После этого можно сделать еще одно действие (например - выстрелить)",
            self.state = States.USE_ACTION_SELECT
            self.current_turn_state()['COFFEE'] = False
            r = Result.action("С помощью ☕️ кофе вы сможете сделать два действия:", States.USE_ACTION_SELECT, self._main_action_options(active_player))
        elif item == Equipment.BRIBE:
            # "💵 взятка: Посмотреть карту дрого игрока. После этого можно поменять эту его карту на любую свою карту",
            investigatable_players = self.get_list_of_investigatable_players(active_player)
            if len(flatten_buttons(investigatable_players)) < 1:
                return Result.error(f"Не получится использовать 💵 взятку - все карты у всех игроков известны")
            self.state = States.USE_PLAYER_SELECT
            r = Result.action("Выберите игрока чтобы дать ему 💵 взятку. Вы сможете подсмотреть у него одну карту", States.USE_PLAYER_SELECT, investigatable_players)
        elif item == Equipment.WIRETAP:
            # "🎧 прослушка: вы узнаете результат следующей проверки карты другим игроком",
            self.wiretap_id = active_player.id
            self.current_turn_state()['action_done'] = True
            self.state = States.AIM
            r = Result.action(f"Вы использовали 🎧 прослушку. Вам сообщат результат следующей проверки", States.AIM)
            r.notify_all_others(f"{active_player.name} использовал 🎧 прослушку. Он узнает результат следующей проверки")
        self.equipment_deck.insert(0, item)
        active_player.equipment = []
        return r

    def use_action(self, user, action) -> Result:
        item = self.current_turn_state()['used_item']
        if item == Equipment.TRUTH_SERUM:
            # "💉 сыворотка правды: выбранный игрок открывает всем одну свою карту",
            if self.state == States.USE_PLAYER_SELECT:
                active_player = self.n[self.current_turn_state()['active_player']]
                active_player: CopPlayer
                if user['id'] != active_player.id:
                    return Result.error(f'{str(user)} сейчас не ходит!')
                r = Game.check_input_values(action, 1, self.len)
                if r is not None:
                    return r
                investigatable_players = flatten_buttons(self.get_list_of_investigatable_players(active_player))
                target = self.n[action]
                target: CopPlayer
                self.current_turn_state()['used_item_target'] = target
                self.current_turn_state()['used_item_user'] = active_player
                if action not in investigatable_players:
                    return Result.error(f"Не получится использовать 💉 сыворотку правды на {target.name} - все карты у {target.name} известны")
                closed_cards = target.get_cards_dict(public=False)
                if len(closed_cards) == 1:
                    unflipped_card_no = next(iter(closed_cards))
                    target.flip_all_up()
                    unflipped_card = active_player.cards[unflipped_card_no]
                    self.current_turn_state()['action_done'] = True
                    self.state = States.AIM
                    r = Result.action(f"Под 💉 сывороткой правды {target.name} раскрыл карту {unflipped_card_no}-{unflipped_card.value}")
                    r.notify_all_others(f"{active_player.name} использовал 💉 сыворотку правды на {target.name}.\n{target.name} раскрыл карту {unflipped_card_no}-{unflipped_card.value}")
                r = Result()
                self.state = States.USE_CARD_SELECT
                r.msg_to_id(target.id, "Вам вкололи 💉 сыворотку правды. Вам необходимо открыть одну карту", States.USE_CARD_SELECT, self.get_card_description_buttons(closed_cards))
                return r
            elif self.state == States.USE_CARD_SELECT:
                r = Game.check_input_values(action, 1, 3)
                if r is not None:
                    return r
                target = self.current_turn_state()['used_item_target']
                target: CopPlayer
                if user['id'] != target.id:
                    return Result.error(f'{str(user)} сейчас не ходит!')
                active_player = self.current_turn_state()['used_item_user']
                active_player: CopPlayer
                unflipped_card = target.cards[action]
                target.public_cards[action] = True
                self.current_turn_state()['action_done'] = True
                self.state = States.AIM
                r = Result()
                r.notify_all(f"{active_player.name} использовал 💉 сыворотку правды на {target.name}.\n{target.name} раскрыл карту {action}-{unflipped_card.value}")
                return r
        elif item == Equipment.FLASHBANG:
            # "💣 Светошумовая граната: закрыть и перемешать все свои открытые карты",
            return Result.error("Ошибка, 💣 Светошумовая граната уже использована")
        elif item == Equipment.BLACKMAIL:
            # "👹 шантаж: поменять местами две карты у двух других игроков",
            active_player = self.n[self.current_turn_state()['active_player']]
            active_player: CopPlayer
            if user['id'] != active_player.id:
                return Result.error(f'{str(user)} сейчас не ходит!')
            if self.state == States.USE_PLAYER_SELECT:
                r = Game.check_input_values(action, 1, self.len)
                if r is not None:
                    return r
                target = self.n[action]
                if target.id == active_player.id:
                    return Result.error("нелья выбрать себя")
                if 'used_item_target_1' not in self.current_turn_state():
                    self.current_turn_state()['used_item_target_1'] = target
                    cards = target.get_cards_dict()
                    self.state = States.USE_CARD_SELECT
                    return Result.action(f"Веберите карту у {target.name}", States.USE_CARD_SELECT, self.get_card_number_buttons(cards))
                else:
                    self.current_turn_state()['used_item_target_2'] = target
                    cards = target.get_cards_dict()
                    self.state = States.USE_CARD_SELECT
                    return Result.action(f"Веберите карту у {target.name}", States.USE_CARD_SELECT, self.get_card_number_buttons(cards))
            elif self.state == States.USE_CARD_SELECT:
                r = Game.check_input_values(action, 1, 3)
                if r is not None:
                    return r
                if 'used_item_target_2' not in self.current_turn_state():
                    target = self.current_turn_state()['used_item_target_1']
                    self.current_turn_state()['used_item_target_card_1'] = action
                    aimable_players = self.get_list_of_aimable_players(active_player, exclude_ids=[target.id])
                    self.state = States.USE_PLAYER_SELECT
                    return Result.action("Выберите второго игрока чтобы использовать 👹 шантаж", States.USE_PLAYER_SELECT, aimable_players)
                else:
                    target_1 = self.current_turn_state()['used_item_target_1']
                    target_1: CopPlayer
                    target_1_team = target_1.team()
                    target_2 = self.current_turn_state()['used_item_target_2']
                    target_2: CopPlayer
                    target_2_team = target_2.team()
                    card_1 = self.current_turn_state()['used_item_target_card_1']
                    card_2 = action
                    self.current_turn_state()['used_item_target_card_2'] = action
                    target_1.cards[card_1], target_2.cards[card_2] = target_2.cards[card_2], target_1.cards[card_1]
                    target_1.public_cards[card_1], target_2.public_cards[card_2] = target_2.public_cards[card_2], target_1.public_cards[card_1]
                    #todo поменять у всех известные карты
                    self.state = States.AIM
                    self.current_turn_state()['action_done'] = True
                    r = Result
                    if target_1.check_winner():
                        r = Result.notify_all(f"{active_player.name} использовал 👹 шантаж! {target_1.name} собрал обе карты {Roles.AGENT.value} и {Roles.KINGPIN.value}, {target_1.name} победил!\nОстальные проиграли!", States.END_GAME)
                        self.state = States.END_GAME
                        self.check_victory()
                        return r
                    if target_2.check_winner():
                        r = Result.notify_all(f"{active_player.name} использовал 👹 шантаж! {target_2.name} собрал обе карты {Roles.AGENT.value} и {Roles.KINGPIN.value}, {target_2.name} победил!\nОстальные проиграли!", States.END_GAME)
                        self.state = States.END_GAME
                        self.check_victory()
                        return r
                    for p in self.pl:
                        if p.id == active_player.id:
                            r.msg_to_id(p.id, f"Вы поменяли карту {card_1} у {target_1.name} на карту {card_2} у {target_2.name}", States.AIM)
                        if p.id == target_1.id:
                            msg = f"{active_player.id} применил к вам 👹 шантаж!\n" + \
                                  f"Вам поменяли карту {card_1}-{target_1.cards[card_1].value} на карту {card_2}-{target_2.cards[card_2].value} у {target_2.name}"
                            if target_1.team() != target_1_team:
                                msg += f"\nТеперь вы в команде {target_1.team().value}"
                            r.msg_to_id(p.id, msg)
                        if p.id == target_2.id:
                            msg = f"{active_player.id} применил к вам 👹 шантаж!\n" + \
                                  f"Вам поменяли карту {card_2}-{target_2.cards[card_2].value} на карту {card_1}-{target_1.cards[card_1].value} у {target_1.name}"
                            if target_2.team() != target_2_team:
                                msg += f"\nТеперь вы в команде {target_2.team().value}"
                            r.msg_to_id(p.id, msg)
                        else:
                            r.msg_to_id(p.id, f"{active_player.name} использовал 👹 шантаж! {active_player.name} поменял карту {card_1} у {target_1.name} на карту {card_2} у {target_2.name}", States.AIM)
                    return r
        elif item == Equipment.RESTRAINING_ORDER:
            # "📑 приказ начальства: выбранный игрок с пистолетом обязан выбрать другую цель",
            if self.state == States.USE_PLAYER_SELECT:
                r = Game.check_input_values(action, 1, self.len)
                if r is not None:
                    return r
                target = self.n[action]
                target: CopPlayer
                active_player = self.n[self.current_turn_state()['active_player']]
                active_player: CopPlayer
                current_target_id = None
                if target.aim in self.n:
                    current_target_id = self.n[target.aim].id
                self.current_turn_state()['used_item_exluded_target'] = target.aim
                self.current_turn_state()['used_item_target'] = target
                self.state = States.USE_ACTION_SELECT
                aimable_players = self.get_list_of_aimable_players(target, exclude_ids=[current_target_id])
                r = Result()
                r.msg_to_id(target.id, f"{active_player.name} использовал на Вас 📑 приказ начальства - вы обязаны выбрать другую цель", States.USE_ACTION_SELECT, aimable_players)
                return r
            if self.state == States.USE_ACTION_SELECT:
                r = Game.check_input_values(action, 1, self.len)
                if r is not None:
                    return r
                target = self.current_turn_state()['used_item_target']
                target: CopPlayer
                active_player = self.n[self.current_turn_state()['active_player']]
                active_player: CopPlayer
                if action == target.aim:
                    return Result.error("Нельзя выбрать ту же самую цель")
                target.aim = action
                self.state = States.AIM
                self.current_turn_state()['action_done'] = True
                r = Result()
                r.notify_all(target.id, f"{active_player.name} использовал 📑 приказ начальства на {target.name}. {target.name} выбрал другую цель")
                return r
        elif item == Equipment.K_9_UNIT:
            # "🐶 служебная собака: выбранный игрок с пистолетом бросает пистолет",
            if self.state == States.USE_PLAYER_SELECT:
                r = Game.check_input_values(action, 1, self.len)
                if r is not None:
                    return r
                target = self.n[action]
                target: CopPlayer
                active_player = self.n[self.current_turn_state()['active_player']]
                active_player: CopPlayer
                target.gun = False
                target.aim = -1
                r = Result()
                self.state = States.AIM
                self.current_turn_state()['action_done'] = True
                r.notify_all(target.id, f"{active_player.name} использовал 🐶 служебную собаку на {target.name}.\n{target.name} потерял свой пистолет")
                return r
        elif item == Equipment.POLYGRAPTH:
            # "📈 полиграф: выбранный игрок показывает вам все свои карты. А вы показываете ему все свои",
            if self.state == States.USE_PLAYER_SELECT:
                r = Game.check_input_values(action, 1, self.len)
                if r is not None:
                    return r
                target = self.n[action]
                target: CopPlayer
                active_player = self.n[self.current_turn_state()['active_player']]
                active_player: CopPlayer
                target_cards = target.get_cards_dict()
                active_player_cards = active_player.get_cards_dict()
                self.current_turn_state()["known_facts"][active_player.num][target.num] = target_cards
                self.current_turn_state()["known_facts"][target.num][active_player.num] = active_player_cards
                self.state = States.AIM
                self.current_turn_state()['action_done'] = True
                r = Result()
                s = '\n'
                for p in self.pl:
                    if p.id == target.id:
                        r.msg_to_id(p.id, f"{active_player.name} использовал 📈 полиграф на Вас. Теперь {active_player.name} знает все ваши карты.\nкарты у {active_player.name}:\n{self.decorate_cards_dict(active_player_cards,s)}")
                    if p.id == active_player.id:
                        r.msg_to_id(p.id, f"Вы использовали 📈 полиграф на {target.name}. Теперь {target.name} знает все ваши карты.\nкарты у {target.name}:\n{self.decorate_cards_dict(target_cards,s)}")
                    else:
                        r.msg_to_id(p.id, f"{active_player.name} использовал 📈 полиграф на {target.name}. Теперь они знают карты друг друга")
                return r
        elif item == Equipment.PLANTED_EVIDENCE:
            # "🔪 подброшенная улика: меняет у выбранного игрока все карты Хорошего Копа на карты Плохого Копа и наоборот",
            if self.state == States.USE_PLAYER_SELECT:
                r = Game.check_input_values(action, 1, self.len)
                if r is not None:
                    return r
                target = self.n[action]
                target: CopPlayer
                active_player = self.n[self.current_turn_state()['active_player']]
                active_player: CopPlayer
                target_cards = target.get_cards_dict()
                self.state = States.AIM
                self.current_turn_state()['action_done'] = True
                for key, value in target_cards.items():
                    if value == Roles.GOOD:
                        target.cards[key] = Roles.BAD
                    if value == Roles.BAD:
                        target.cards[key] = Roles.GOOD
                r = Result()
                s = '\n'
                for p in self.pl:
                    if p.id == target.id:
                        r.msg_to_id(p.id, f"{active_player.name} использовал 🔪 подброшенную улику на Вас. Вам поменяли все карты\nВаши карты:\n{self.decorate_cards_dict(target_cards,s)}\nТеперь вы {target.team()}")
                    if p.id == active_player.id:
                        r.msg_to_id(p.id, f"Вы использовали 🔪 подброшенную улику на {target.name}. Теперь у {target.name} все карты изменены на противоположные\n(карты лидера остались без изменения)")
                    else:
                        r.msg_to_id(p.id, f"{active_player.name} использовал 🔪 подброшенную улику на {target.name}. Теперь у {target.name} все карты изменены на противоположные\n(карты лидера остались без изменения)")
                return r
        elif item == Equipment.METAL_DETECTOR:
            # "🔧 металоискатель: проверить по одной карте у всех игроков с пистолетом",
            if self.state == States.USE_CARD_SELECT:
                r = Game.check_input_values(action, 1, 3)
                if r is not None:
                    return r
                target = self.current_turn_state()['METAL_DETECTOR_current_target']
                target: CopPlayer
                active_player = self.n[self.current_turn_state()['active_player']]
                active_player: CopPlayer
                return self.use_metal_detector(active_player, self._card_fliping(active_player, action, target))
        elif item == Equipment.EVIDENCE_BAG:
            # "💼 пакет для улик: заберите предмет у выбранного игрока",
            if self.state == States.USE_PLAYER_SELECT:
                r = Game.check_input_values(action, 1, self.len)
                if r is not None:
                    return r
                target = self.n[action]
                target: CopPlayer
                active_player = self.n[self.current_turn_state()['active_player']]
                active_player: CopPlayer
                if not target.has_equipment():
                    return Result.error(f"У {target.name} нет предмета")
                target_item = target.get_equipment()
                self.state = States.AIM
                self.current_turn_state()['action_done'] = True
                active_player.equipment = target.equipment
                target.equipment = []
                r = Result()
                s = '\n'
                for p in self.pl:
                    if p.id == target.id:
                        r.msg_to_id(p.id, f"{active_player.name} использовал 💼 пакет для улик на Вас. {active_player.name} забрал себе ваш {target_item.value}")
                    if p.id == active_player.id:
                        r.msg_to_id(p.id, f"Вы использовали 💼 пакет для улик на {target.name}. Теперь у вас есть:\n{EQUIPMENT_DESCRIPTION[target_item]}")
                    else:
                        r.msg_to_id(p.id, f"{active_player.name} использовал 💼 пакет для улик на {target.name} и забрал у {target.name} предмет")
                return r
        elif item == Equipment.REPORT_AUDIT:
            # "📝 прокурорская проверка: каждый игрок, у которого еще нет открытых карт, открывает одну карту",
            if self.state == States.USE_CARD_SELECT:
                r = Game.check_input_values(action, 1, 3)
                if r is not None:
                    return r
                target = self.get_player_by_id(user["id"])
                target: CopPlayer
                self.current_turn_state()['REPORT_AUDIT'][target.num] = True
                msg, msg_all = self._self_card_flip(target, action)
                self.current_turn_state()['REPORT_AUDIT_MSG'] += msg + "\n"
                self.current_turn_state()['REPORT_AUDIT_MSG_ALL'][target.num] = msg_all
                return Result.action(msg)
        elif item == Equipment.DEFIBRILLATOR:
            # "🩺 дефибриллятор: оживить мертвого игрока",  # TODO и поменять карты на одну из карт
            if self.state == States.USE_PLAYER_SELECT:
                r = Game.check_input_values(action, 1, self.len)
                if r is not None:
                    return r
                target = self.n[action]
                target: CopPlayer
                active_player = self.n[self.current_turn_state()['active_player']]
                target.dead = False
                self.current_turn_state()['action_done'] = True
                self.state = States.AIM
                r = Result()
                r.notify_all(f"{active_player.name} использовал 🩺 дефибриллятор на {target.name}. {target.name} больше не мертв!")
                return r
        elif item == Equipment.SURVEILLANCE_CAMERA:
            # "🎥 скрытое видеонаблюдение: посмотреть карту, которую последний раз смотрел другой игрок",
            return Result.error("Ошибка, 💣 Светошумовая граната уже использована")
        elif item == Equipment.TAZER:
            # "⚡ электрошокер: забрать пистолет у выбранного игрока",
            if self.state == States.USE_PLAYER_SELECT:
                r = Game.check_input_values(action, 1, self.len)
                if r is not None:
                    return r
                target = self.n[action]
                target: CopPlayer
                active_player = self.n[self.current_turn_state()['active_player']]
                active_player: CopPlayer
                target.gun = False
                target.aim = -1
                active_player.gun = True
                r = Result()
                self.state = States.AIM
                self.current_turn_state()['action_done'] = True
                r.notify_all(target.id, f"{active_player.name} использовал ⚡ электрошокер на {target.name}.\n{active_player.name} забрал у {target.name} пистолет")
                return r
        elif item == Equipment.COFFEE:
            # "☕️ кофе: прицелиться в друго игрка. После этого можно сделать еще одно действие (например - выстрелить)",
            r = self.main_action(user, action)
            if self.state == States.ACTION_SELECT:
                return r
            self.current_turn_state()['COFFEE'] = True
            return r
        elif item == Equipment.BRIBE:
            # "💵 взятка: Посмотреть карту дрого игрока. После этого можно поменять эту его карту на любую свою карту",
            active_player = self.n[self.current_turn_state()['active_player']]
            active_player: CopPlayer
            if user['id'] != active_player.id:
                return Result.error(f'{str(user)} сейчас не ходит!')
            if self.state == States.USE_PLAYER_SELECT:
                r = Game.check_input_values(action, 1, self.len)
                if r is not None:
                    return r
                target = self.n[action]
                if target.id == active_player.id:
                    return Result.error("нелья выбрать себя")
                self.current_turn_state()['used_item_target'] = target
                cards = target.get_cards_dict()
                self.state = States.USE_CARD_SELECT
                return Result.action(f"Веберите карту у {target.name}", States.USE_CARD_SELECT, self.get_card_number_buttons(cards))
            elif self.state == States.USE_CARD_SELECT:
                r = Game.check_input_values(action, 1, 3)
                if r is not None:
                    return r
                if 'used_item_target_card' not in self.current_turn_state():
                    self.current_turn_state()['used_item_target_card'] = action
                    cards = active_player.get_cards_dict()
                    return Result.action(f"Веберите карту у себя", States.USE_CARD_SELECT, self.get_card_description_buttons(cards))
                else:
                    target = self.current_turn_state()['used_item_target']
                    target: CopPlayer
                    target_team = target.team()
                    active_player_team = active_player.team()
                    card_t = self.current_turn_state()['used_item_target_card']
                    card_a = action
                    self.current_turn_state()['used_item_target_card_2'] = action
                    target.cards[card_t], active_player.cards[card_a] = active_player.cards[card_a], target.cards[card_t]
                    target.public_cards[card_t], active_player.public_cards[card_a] = active_player.public_cards[card_a], target.public_cards[card_t]
                    #todo поменять у всех известные карты
                    self.state = States.AIM
                    self.current_turn_state()['action_done'] = True
                    r = Result
                    if target.check_winner():
                        r = Result.notify_all(f"{active_player.name} использовал 👹 шантаж! {target.name} собрал обе карты {Roles.AGENT.value} и {Roles.KINGPIN.value}, {target.name} победил!\nОстальные проиграли!", States.END_GAME)
                        self.state = States.END_GAME
                        self.check_victory()
                        return r
                    if active_player.check_winner():
                        r = Result.notify_all(f"{active_player.name} использовал 👹 шантаж! {active_player.name} собрал обе карты {Roles.AGENT.value} и {Roles.KINGPIN.value}, {active_player.name} победил!\nОстальные проиграли!", States.END_GAME)
                        self.state = States.END_GAME
                        self.check_victory()
                        return r
                    for p in self.pl:
                        if p.id == target.id:
                            msg = f"{active_player.id} применил к вам 💵 взятку!\n" + \
                                  f"Вам поменяли карту {card_t}-{target.cards[card_t].value} на карту {card_a}-{active_player.cards[card_a].value} у {active_player.name}"
                            if target.team() != target_team:
                                msg += f"\nТеперь вы в команде {target.team().value}"
                            r.msg_to_id(p.id, msg)
                        if p.id == active_player.id:
                            msg = f"Вы применили 💵 взятку!\n" + \
                                  f"Вы поменяли карту {card_t}-{target.cards[card_t].value} на карту {card_a}-{active_player.cards[card_a].value} у {target.name}"
                            if active_player.team() != active_player_team:
                                msg += f"\nТеперь вы в команде {active_player.team().value}"
                            r.msg_to_id(p.id, msg)
                        else:
                            r.msg_to_id(p.id, f"{active_player.name} использовал 💵 взятку! {active_player.name} поменял карту {card_t} у {target.name} на карту {card_a} у {active_player.name}", States.AIM)
                    return r
        elif item == Equipment.WIRETAP:
            # "🎧 прослушка: вы узнаете результат следующей проверки карты другим игроком",
            return Result.error("Ошибка, 🎧 прослушк уже использована")
        return Result.error(f"Предмет {item} не найден")

    def check_use_is_done(self) -> bool:
        item = self.current_turn_state()['used_item']
        if item == Equipment.TRUTH_SERUM:
            # "💉 сыворотка правды: выбранный игрок открывает всем одну свою карту",
            return self.current_turn_state()['action_done']
        elif item == Equipment.FLASHBANG:
            # "💣 Светошумовая граната: закрыть и перемешать все свои открытые карты",
            return True
        elif item == Equipment.BLACKMAIL:
            # "👹 шантаж: поменять местами две карты у двух других игроков",
            return self.current_turn_state()['action_done']
        elif item == Equipment.RESTRAINING_ORDER:
            # "📑 приказ начальства: выбранный игрок с пистолетом обязан выбрать другую цель",
            return self.current_turn_state()['action_done']
        elif item == Equipment.K_9_UNIT:
            # "🐶 служебная собака: выбранный игрок с пистолетом бросает пистолет",
            return self.current_turn_state()['action_done']
        elif item == Equipment.POLYGRAPTH:
            # "📈 полиграф: выбранный игрок показывает вам все свои карты. А вы показываете ему все свои",
            return self.current_turn_state()['action_done']
        elif item == Equipment.PLANTED_EVIDENCE:
            # "🔪 подброшенная улика: меняет у выбранного игрока все карты Хорошего Копа на карты Плохого Копа и наоборот",
            return self.current_turn_state()['action_done']
        elif item == Equipment.METAL_DETECTOR:
            # "🔧 металоискатель: проверить по одной карте у всех игроков с пистолетом",
            if 'METAL_DETECTOR_LEFT' not in self.current_turn_state():
                return False
            return len(self.current_turn_state()['METAL_DETECTOR_LEFT']) <= 0
        elif item == Equipment.EVIDENCE_BAG:
            # "💼 пакет для улик: заберите предмет у выбранного игрока",
            return self.current_turn_state()['action_done']
        elif item == Equipment.REPORT_AUDIT:
            # "📝 прокурорская проверка: каждый игрок, у которого еще нет открытых карт, открывает одну карту",
            if 'REPORT_AUDIT' not in self.current_turn_state():
                return False
            for b in self.current_turn_state()['REPORT_AUDIT']:
                if not b:
                    return False
            return True
        elif item == Equipment.DEFIBRILLATOR:
            # "🩺 дефибриллятор: оживить мертвого игрока",  # TODO и поменять карты на одну из карт
            return self.current_turn_state()['action_done']
        elif item == Equipment.SURVEILLANCE_CAMERA:
            # "🎥 скрытое видеонаблюдение: посмотреть карту, которую последний раз смотрел другой игрок",
            return True
        elif item == Equipment.TAZER:
            # "⚡ электрошокер: забрать пистолет у выбранного игрока",
            return self.current_turn_state()['action_done']
        elif item == Equipment.COFFEE:
            # "☕️ кофе: прицелиться в друго игрка. После этого можно сделать еще одно действие (например - выстрелить)",
            return self.current_turn_state()['action_done']
        elif item == Equipment.BRIBE:
            # "💵 взятка: Посмотреть карту дрого игрока. После этого можно поменять эту его карту на любую свою карту",
            return self.current_turn_state()['action_done']
        elif item == Equipment.WIRETAP:
            # "🎧 прослушка: вы узнаете результат следующей проверки карты другим игроком",
            return True
        return True

    def _use_do_next_step(self) -> bool:
        item = self.current_turn_state()['used_item']
        if item == Equipment.TRUTH_SERUM:
            # "💉 сыворотка правды: выбранный игрок открывает всем одну свою карту",
            return None
        elif item == Equipment.FLASHBANG:
            # "💣 Светошумовая граната: закрыть и перемешать все свои открытые карты",
            return None
        elif item == Equipment.BLACKMAIL:
            # "👹 шантаж: поменять местами две карты у двух других игроков",
            return None
        elif item == Equipment.RESTRAINING_ORDER:
            # "📑 приказ начальства: выбранный игрок с пистолетом обязан выбрать другую цель",
            return None
        elif item == Equipment.K_9_UNIT:
            # "🐶 служебная собака: выбранный игрок с пистолетом бросает пистолет",
            return None
        elif item == Equipment.POLYGRAPTH:
            # "📈 полиграф: выбранный игрок показывает вам все свои карты. А вы показываете ему все свои",
            return None
        elif item == Equipment.PLANTED_EVIDENCE:
            # "🔪 подброшенная улика: меняет у выбранного игрока все карты Хорошего Копа на карты Плохого Копа и наоборот",
            return None
        elif item == Equipment.METAL_DETECTOR:
            # "🔧 металоискатель: проверить по одной карте у всех игроков с пистолетом",
            active_player = self.n[self.current_turn_state()['active_player']]
            return self.use_metal_detector(active_player)
        elif item == Equipment.EVIDENCE_BAG:
            # "💼 пакет для улик: заберите предмет у выбранного игрока",
            return None
        elif item == Equipment.REPORT_AUDIT:
            # "📝 прокурорская проверка: каждый игрок, у которого еще нет открытых карт, открывает одну карту",
            active_player = self.n[self.current_turn_state()['active_player']]
            msg = ""
            for n, msg in self.current_turn_state()['REPORT_AUDIT_MSG_ALL']:
                msg += f"{msg}\n"
            r = Result.notify_all(f"{active_player.name} использовал 📝 прокурорскую проверку:\n{msg}")
            return r
        elif item == Equipment.DEFIBRILLATOR:
            # "🩺 дефибриллятор: оживить мертвого игрока",  # TODO и поменять карты на одну из карт
            return None
        elif item == Equipment.SURVEILLANCE_CAMERA:
            # "🎥 скрытое видеонаблюдение: посмотреть карту, которую последний раз смотрел другой игрок",
            return None
        elif item == Equipment.TAZER:
            # "⚡ электрошокер: забрать пистолет у выбранного игрока",
            return None
        elif item == Equipment.COFFEE:
            # "☕️ кофе: прицелиться в друго игрка. После этого можно сделать еще одно действие (например - выстрелить)",
            return None
        elif item == Equipment.BRIBE:
            # "💵 взятка: Посмотреть карту дрого игрока. После этого можно поменять эту его карту на любую свою карту",
            return None
        elif item == Equipment.WIRETAP:
            # "🎧 прослушка: вы узнаете результат следующей проверки карты другим игроком",
            return True
        return True

    def use_metal_detector(self, active_player: CopPlayer, msg=""):
        investigatable_players = flatten_buttons(self.get_buttons_list(active_player.id, exclude_dead=True))
        r = Result.action("🔧 металоискатель использован")
        while len(self.current_turn_state()['METAL_DETECTOR_LEFT']) > 0:
            next_player_to_check = self.current_turn_state()['METAL_DETECTOR_LEFT'].pop()
            target = self.n[next_player_to_check]
            target: CopPlayer
            self.current_turn_state()['METAL_DETECTOR_current_target'] = target
            cards = target.get_card_numbers_list(public=False)
            if len(cards) == 1:
                unflipped_card_no = next(iter(cards))
                msg += self._card_fliping(active_player, unflipped_card_no, target)
            if len(cards) > 1:
                self.state = States.USE_CARD_SELECT
                return Result.action(f"{msg}\nВыберите карту у {target.name}", States.USE_CARD_SELECT, self.get_card_number_buttons(cards))
        self.state = States.AIM
        self.current_turn_state()['action_done'] = True
        return Result.action("🔧 металоискатель использован\n" + msg)

    def investigate(self, user, action):
        r = Game.check_input_values(action, 1, self.len)
        if r is not None:
            return r
        active_player = self.n[self.current_turn_state()['active_player']]
        active_player: CopPlayer
        if user['id'] != active_player.id:
            return Result.error(f'{str(user)} сейчас не ходит!')
        self.current_turn_state()["action"]["selected_player"] = action
        target = self.n[action]
        target: CopPlayer
        if target.dead:
            return Result.error(f"{target.name} уже мертв!")
        cards = target.get_card_numbers_list(public=False)
        if len(cards) == 0:
            return Result.error(f"Вы уже знаете все карты {target.name}!")
        if len(cards) == 1:
            # only one card to flip
            investigated_card_no = cards[0]
            return self._investigate_card_flip(active_player, investigated_card_no, target)
        self.state = States.INVESTIGATE_CARD_SELECT
        return Result.action("Выберите карту", States.INVESTIGATE_CARD_SELECT, self.get_card_number_buttons(cards))

    def aim(self, user, action):
        r = Game.check_input_values(action, 1, self.len)
        if r is not None:
            return r
        active_player = self.n[self.current_turn_state()['active_player']]
        active_player: CopPlayer
        if user['id'] != active_player.id:
            return Result.error(f'{str(user)} сейчас не ходит!')
        self.current_turn_state()["action"]["selected_aim_target"] = action
        target = self.n[action]
        target: CopPlayer
        if target.dead:
            return Result.error(f"{target.name} уже мертв!")
        self.state = States.END_TURN
        self.current_turn_state()['aim_done'] = True
        self.current_turn_state()['action_done'] = True
        active_player.aim = action
        r = Result.action(f"Вы целитесь в {target.name}")
        r.notify_all_others(f"{active_player.name} наставил пистолет на {target.name}")
        return r

    def discard(self, user, action):
        active_player = self.get_player_by_id(user['id'])
        active_player: CopPlayer
        if active_player is None:
            return Result.error(f'{str(user)} не найден!')
        r = Game.check_input_values(action, 1, len(active_player.equipment))
        if r is not None:
            return r
        self.current_turn_state()["discard"] = action
        item_left = active_player.equipment[action-1]
        discarded = copy.deepcopy(active_player.equipment)
        del discarded[action-1]
        active_player.equipment = [item_left]
        for ditem in discarded:
            self.equipment_deck.insert(0, ditem)
        return Result.action(f"У вас осталось {item_left.value}")

    def _investigate_card_flip(self, by: CopPlayer, card: int, of: CopPlayer) -> Result:
        msg = self._card_fliping(by, card, of)
        self.current_turn_state()['action_done'] = True
        self.state = States.END_TURN
        self.last_investigated_card = msg
        r = Result.action(msg)
        r: Result
        r.notify_all_others(f"{by.name} проверил карту №{str(card)} у {of.name}")
        if self.wiretap_id is not None:
            r.msg_to_id(self.wiretap_id, "🎧 прослушка принесла результаты:\n" + msg)
            self.wiretap_id = None
        return r

    def _card_fliping(self, by: CopPlayer, card: int, of: CopPlayer) -> str:
        known_facts = self.current_turn_state()["known_facts"][by.num][of.num]
        if known_facts is None:
            self.current_turn_state()["known_facts"][by.num][of.num] = {}
        result = of.cards[card]
        known_facts = self.current_turn_state()["known_facts"][by.num][of.num]
        public_cards = of.get_cards_dict(public=True)
        known_facts.update(public_cards)
        known_facts[card] = result
        self.current_turn_state()["known_facts"][by.num][of.num] = copy.deepcopy(known_facts)
        msg = f"Вы узнали, что у {of.name} карта №{str(card)} - {result.value}"
        if len(known_facts) > 1:
            msg += "\n" + CopGame.describe_known_cards(known_facts, of)
        return msg

    @staticmethod
    def describe_known_cards(known_cards: dict, of: CopPlayer):
        if len(known_cards) == 0:
            return ""
        ret = f"Вам известно, что у {of.name} карты: "
        for k, v in known_cards.items():
            ret += f"{str(k)}-{v.value} "
        if len(known_cards) == 3:
            ret += f"\nЭто означет, что {of.name} - {of.role().value}"
        return ret

    @staticmethod
    def decorate_cards_dict(cards: dict, separator=" "):
        if len(cards) == 0:
            return ""
        ret = ""
        for k, v in cards.items():
            ret += f"`{str(k)}-{v.value}`{separator}"
        return ret

    def investigate_card_pick(self, user, action):
        r = Game.check_input_values(action, 1, 3)
        if r is not None:
            return r
        active_player = self.n[self.current_turn_state()['active_player']]
        active_player: CopPlayer
        if user['id'] != active_player.id:
            return Result.error(f'{str(user)} сейчас не ходит!')
        self.current_turn_state()["action"]["selected_card"] = action
        target = self.n[self.current_turn_state()["action"]["selected_player"]]
        target: CopPlayer
        if target.dead:
            return Result.error(f"{target.name} уже мертв!")
        cards = target.get_card_numbers_list(public=False)
        if len(cards) == 0:
            return Result.error(f"Вы уже знаете все карты {target.name}!")
        #TODO what to do when I want to change player? 0 for selecting other player?
        if action not in cards:
            return Result.error(f"Вы уже знаете карту №{action} у {target.name}!")
        return self._investigate_card_flip(active_player, action, target)

    def self_card_flip(self, user, action):
        r = Game.check_input_values(action, 1, 3)
        if r is not None:
            return r
        active_player = self.n[self.current_turn_state()['active_player']]
        active_player: CopPlayer
        if user['id'] != active_player.id:
            return Result.error(f'{str(user)} сейчас не ходит!')
        cards = active_player.get_cards_dict(public=False)
        if len(cards) == 0:
            self.current_turn_state()['action_done'] = True
            self.state = States.AIM
            return Result.action(f"Вы уже открыли все свои карты!")
        if action not in cards:
            return Result.error(f"Вы уже открыли свою карту №{action}")
        msg, msg_all = self._self_card_flip(active_player, action)
        self.current_turn_state()['action_done'] = True
        self.state = States.AIM
        r = Result.action(msg)
        r: Result
        r.notify_all_others(msg_all)
        return r

    def _self_card_flip(self, active_player: CopPlayer, card):
        if "fliped_cards" not in self.current_turn_state()["action"]:
            self.current_turn_state()["action"]["fliped_cards"] = []
        self.current_turn_state()["action"]["fliped_cards"].append(card)
        active_player.public_cards[card] = True
        result = active_player.cards[card]
        msg = f"Вы открыли карту №{str(card)}"
        msg_all = f"{active_player.name} открыл карту №{str(card)} - {result.value}"
        return msg, msg_all

    def get_extra_known_cards(self, by, of):
        public_cards = of.get_cards_dict(public=True)
        known_cards = {}
        known_facts = self.current_turn_state()["known_facts"][by.num]
        if known_facts is not None:
            if of.num in known_facts:
                known_cards = known_facts[of.num]
                if known_cards is None:
                    known_cards = {}
        for i in public_cards.keys():
            while i in known_cards.keys():
                known_cards.pop(i, None)
        return known_cards

    def get_unknown_cards(self, by: CopPlayer, of: CopPlayer):
        non_public_cards = of.get_card_numbers_list(public=False)
        known_cards = []
        known_facts = self.current_turn_state()["known_facts"][by.num]
        if known_facts is not None:
            known_cards = known_facts[of.num]
            if known_cards is None:
                known_cards = []
        for i in known_cards:
            while i in non_public_cards:
                non_public_cards.remove(i)
        return non_public_cards

    def get_card_number_buttons(self, cards: list):
        r = []
        for i in cards:
            tuple = (str(i), i)
            l = [tuple]
            r.append(l)
        return r

    def get_card_description_buttons(self, cards: dict):
        r = []
        for i, v in cards.items():
            tuple = (f"{str(i)}: {v.value}", i)
            l = [tuple]
            r.append(l)
        return r

    def get_number_of_guns(self) -> int:
        n = 0
        for p in self.pl:
            p: CopPlayer
            if p.gun:
                n += 1
        return n

    def get_discard_actions(self, player):
        r = []
        i = 1
        for item in player.equipment:
            r.append([(item.value, i)])
            i += 1
        return r
