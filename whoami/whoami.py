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
    ASSIGN_ROLES = "ASSIGN_ROLES"
    PLAY = "PLAY"
    ADD = "ADD"


class WhoAmIGame(Game):
    roles_list = {}
    assigns = {}

    BUTTONS = [[("✅ я отгадал", 0)],
               [("❌ я сдаюсь", 3)],
               [("❔ перезагадать", 1)],
               [("➕ добавить нового человека", 2)],
               ]

    # Abstract methods redef
    def get_init_message(self, p):
        return "Игра 'Кто Я?' начинается!"

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

    def check_next_step(self) -> bool:
        if self.state == State.INIT:
            return False
        elif self.state == State.ASSIGN_ROLES:
            return self.unassigned_players() == 0
        elif self.state == State.PLAY:
            return True
        elif self.state == State.ADD:
            return self.unassigned_players() == 0
        if self.state is None:
            return None
        raise Exception(f"not yet implemented - {self.state}")

    def _do_action(self, user, action) -> Result:
        if self.state == State.INIT:
            return None
        elif self.state == State.ASSIGN_ROLES:
            return self.pick_role(user, action)
        elif self.state == State.PLAY:
            return self.command(user, action)
        elif self.state == State.ADD:
            return self.add_role(user, action)
        if self.state is None:
            return None
        raise Exception(f"not yet implemented - {self.state}")

    def _do_next_step(self) -> Result:
        if self.state == State.INIT:
            return None
        if self.state == State.ASSIGN_ROLES:
            return self.send_roles()
        elif self.state == State.PLAY:
            return None
        elif self.state == State.ENDTURN:
            return None
        if self.state is None:
            return None
        raise Exception(f"not yet implemented - {self.state}")

    def shuffle_assignes(self):
        assigns = {}
        roles_list = list(range(1, self.len+1))
        roles_list.append(roles_list.pop(0))
        for key, p in self.n.items():
            assigns[key] = roles_list.pop(0)
        return assigns

    # GAME PART
    def init_game(self, roles=None, laws=None, starting_player=None):
        super().init_game()
        self.state = State.INIT

        for p in self.pl:
            self.roles_list[p] = None
        self.assigns = self.shuffle_assignes()
        self.state = State.ASSIGN_ROLES
        r = Result()
        for key, pl in self.n.items():
            r.msg_to_id(id=pl.id, msg=f"Загадайте персонажа для {self.n[self.assigns[pl.num]].name}")
        return r

    def pick_role(self, user, action):
        player = self.get_player_by_id(user['id'])
        if player is None:
            return Result.error(f'Вы не участвуете в игре!')
        if str(action).isnumeric():
            return None
        active_player = self.n[self.assigns[player.num]]
        self.roles_list[active_player.num] = action
        return Result.action(f"Принято \"{action}\"")

    def command(self, user, action):
        r = Game.check_input_values(action, 0, 3)
        if r is not None:
            return r
        player = self.get_player_by_id(user['id'])
        if player is None:
            return Result.error(f'Вы не участвуете в игре!')
        # 0: ✅ я отгадал
        if action == 0:
            prev_role = self.roles_list[player.num]
            old_assigner = self.n[self.find_assigner(player.num)]
            self.roles_list[player.num] = None
            new_assigner = self.n[self.get_random_player(player.num)]
            self.assigns[new_assigner.num] = player.num
            self.state = State.ASSIGN_ROLES
            r = Result.notify_all(f"{player.name} отгадал, что они {prev_role} (загадывал {old_assigner.name})")
            r.msg_to_id(id=new_assigner.id, msg=f"Загадайте нового персонажа для {player.name}")
            return r
        # 3: ❌ я сдаюсь
        if action == 3:
            prev_role = self.roles_list[player.num]
            old_assigner = self.n[self.find_assigner(player.num)]
            self.roles_list[player.num] = None
            new_assigner = self.n[self.get_random_player(player.num)]
            self.assigns[new_assigner.num] = player.num
            self.state = State.ASSIGN_ROLES
            r = Result.notify_all(f"{player.name} сдался, они были {prev_role} (загадывал {old_assigner.name})")
            r.msg_to_id(id=new_assigner.id, msg=f"Загадайте нового персонажа для {player.name}")
            return r
        # 1: ❔ перезагадать
        if action == 1:
            assigned_pl = self.n[self.assigns[player.num]]
            prev_role = self.roles_list[assigned_pl.num]
            self.roles_list[assigned_pl.num] = None
            self.state = State.ASSIGN_ROLES
            r = Result.notify_all(f"{player.name} передумали загадывать {prev_role} для {assigned_pl.name})")
            r.msg_to_id(id=player.id, msg=f"Загадайте нового персонажа для {assigned_pl.name}")
            return r
        # 2: ➕ добавить нового человека
        if action == 2:
            new_players_obj = []
            for pl_obj in self.players_list:
                id = pl_obj['id']
                if self.get_player_by_id(id) is None:
                    new_players_obj.append(pl_obj)
            if len(new_players_obj) == 0:
                return Result.error("Не найдено новых игроков")
            new_players = self.update_players()
            msg_names = ""
            r = Result.notify_all(f"В игру добавились: {msg_names}")
            for new_player in new_players:
                msg_names += "\n" + new_player.name
                new_assigner = self.n[self.get_random_player(new_player.num)]
                self.roles_list[new_player.num] = None
                self.assigns[new_assigner.num] = new_player.num
                r.msg_to_id(id=new_assigner.id, msg=f"Загадайте нового персонажа для {new_player.name}")
            self.state = State.ASSIGN_ROLES
            return r
        return Result.action(f"Ошибка, команда не известна")

    def send_roles(self):
        self.state = State.PLAY
        return self.roles_message()

    def roles_message(self):
        r = Result()
        for key_to, pl_to in self.n.items():
            msg = "Список игроков:\n"
            for key_about, pl_about in self.n.items():
                if key_to == key_about:
                    msg += f"\n{key_about}: {pl_about.name} - Это Вы"
                else:
                    msg += f"\n{key_about}: {pl_about.name} - {self.roles_list[key_about]}"
            r.msg_to_id(id=pl_to.id, msg=msg, commands=self.BUTTONS)
        return r

    def find_assigner(self, who):
        for key, value in self.assigns.items():
            if who == value:
                return key
        return -1

    def get_random_player(self, excluding):
        if isinstance(excluding, int):
            excluding = [excluding]
        i = excluding[0]
        while i in excluding[0]:
            i = random.randint(1, self.len)
        return i

    def unassigned_players(self):
        i = 0
        for key, p in self.n.items():
            if self.roles_list[key] is None:
                i += 1
        return i
