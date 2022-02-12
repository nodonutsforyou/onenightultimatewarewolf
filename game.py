import logging
import random
import json
import copy
from datetime import datetime
from player import Player
from util import *

random.seed(datetime.now())


class Game:
    # Game Lobby status
    players_list = []

    # This session
    pl = []
    n = {}
    start_ts = datetime.now()
    game_state = {}
    current_turn = 0
    status = None
    state = None
    len = 0

    # SESSION PART
    def get_player(self, user):
        for p in self.players_list:
            if p["id"] == user["id"]:
                return p
        return None

    def get_current_turn(self) -> int:
        return self.current_turn

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
            p: Player
            if p.id not in exclude_id:
                if not (exclude_dead and p.dead):
                    tuple = (p.name, str(p.num))
                    players_list.append(tuple)
        ret_list += chunks(players_list, 3)
        if vote_all_str is not None:
            ret_list.append([(vote_all_str, "0")])
        return ret_list

    def get_dead_buttons_list(self, exclude_id=None, vote_all_str=None):
        ret_list = []
        players_list = []
        if not isinstance(exclude_id, list):
            exclude_id = [exclude_id]
        for p in self.pl:
            p: Player
            if p.id not in exclude_id:
                if p.dead:
                    tuple = p.name, str(p.num)
                    players_list.append(tuple)
        ret_list += chunks(players_list, 3)
        if vote_all_str is not None:
            ret_list.append([(vote_all_str, "0")])
        return ret_list

    # GAME PART
    def init_game(self, player_class=Player) -> Result:
        # зафиксируем список игроков
        self.pl = []
        self.n = {}
        self.game_state = {}
        num = 1
        status = False, None, None
        for pl_obj in self.players_list:
            self.pl.append(player_class(num, pl_obj))
            num += 1
        self.len = len(self.pl)

        # делаем номерной список
        for p in self.pl:
            p: Player
            self.n[p.num] = p

        # Заводим игровой лог
        self.current_turn = 0
        self.game_state = {0: {"logs": []}}

        # фиксируем время начала
        self.start_ts = datetime.now()
        logging.info("Starting timestamp " + str(self.start_ts))
        return Result.error("super method")

    def list_of_players_by_number(self):
        msg = ""
        for key, p in self.n.items():
            p: Player
            msg += f'{key}: {p.name}\n'
        return msg

    def list_of_alive_players_by_number(self):
        msg = ""
        for key, p in self.n.items():
            p: Player
            if not p.dead:
                msg += f'{key}: {p.name}\n'
        return msg

    def current_turn_state(self):
        return self.game_state[self.current_turn]

    def prev_turn_state(self):
        return self.game_state[self.current_turn - 1]

    def get_player_by_id(self, id):
        for p in self.pl:
            if p.id == id:
                return p
        return None

    @staticmethod
    def check_input_values(value, min_value, max_value, ok_alowed=False):
        if not isinstance(value, int):
            if ok_alowed and str(value) == "OK":
                return Result()
            return Result.error(f"Неверная команда '{value}'")
        if value < min_value:
            return Result.error(f"Неверная команда '{value}'")
        if value > max_value:
            return Result.error(f"Неверная команда '{value}'")
        return None

    # Abstract Methods
    def get_init_message(self, p: Player):
        raise Exception("Abstract method")

    def do_next_step(self, unstack=False) -> Result:
        raise Exception("Abstract method")

    def check_next_step(self) -> bool:
        raise Exception("Abstract method")

    def do_action(self, user, action) -> Result:
        raise Exception("Abstract method")
