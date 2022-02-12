import pytest
import json
from collections import namedtuple
from goodcopbadcop.goodcopbadcop import CopGame, CopPlayer, Actions, Roles
from contextlib import contextmanager
import statebot
from util import dummy_players, dummy_players_large_list

CARDS_LIST_1 = [
    Roles.AGENT, # 1
    Roles.GOOD,
    Roles.GOOD,
    Roles.KINGPIN, # 2
    Roles.GOOD,
    Roles.GOOD,
    Roles.BAD, # 3
    Roles.BAD,
    Roles.GOOD,
    Roles.BAD, # 4
    Roles.BAD,
    Roles.BAD,
    Roles.GOOD, # 5
    Roles.GOOD,
    Roles.BAD,
    Roles.BAD, # 6
    Roles.BAD,
    Roles.BAD,
]

@contextmanager
def does_not_raise():
    yield

class MockUpdateAndContext:
    callback_query = None
    effective_user = None
    bot = None
    data = ""
    id = None

    def __setitem__(self, key, value):
        self.id = value

    def __getitem__(self, key):
        return self.id

    def __str__(self):
        return f"u{str(self.id)}a{self.data}"

    def __init__(self):
        pass

    def answer(self):
        pass

    def send_message(self, id, msg, reply_markup, **kwargs):
        print(f"to {id}: {msg} with options:\n{str(reply_markup)}")

    def log_call(*args, **kwargs):
        print(str(args) + " " + str(kwargs))

    def echo(self, user, action):
        self.effective_user = self
        self.id = user["id"]
        self.callback_query = self
        self.data = str(action)
        self.bot = self
        statebot.echo(self, self)

    # def __getattribute__(self, name):
    #     attr = object.__getattribute__(self, name)
    #     if hasattr(attr, '__call__'):
    #         def newfunc(*args, **kwargs):
    #             result = attr(*args, **kwargs)
    #             return result
    #         return newfunc
    #     else:
    #         return attr

@pytest.mark.parametrize("roles,players,starting_player,actions,expected,expected_msg",
                         [
                             pytest.param(CARDS_LIST_1, dummy_players, 1, [
                                 (1, 1, True, None, None), #1
                                 (1, 2, True, None, None), #2
                                 (1, 1, True, None, None), #3
                                 (2, 1, True, None, None), #4
                                 (2, 3, True, None, None), #5
                                 (2, 3, True, None, None), #6
                                 (3, 3, True, None, None), #7
                                 (3, 3, True, None, None), #8
                                 (3, 1, True, None, None), #9
                                 (4, 3, True, None, None), #10
                                 (4, 1, True, None, None), #11
                                 (4, 1, True, None, None), #12
                                 (5, 3, True, None, None), #10
                                 (5, 3, True, None, None), #11
                                 (5, 3, True, None, None), #12
                                 (6, 1, True, None, None), #13
                                 (6, 5, True, None, None), #14
                                 (6, 2, True, None, None), #15
                                 (1, 1, True, None, None), #16
                                 (1, 5, True, None, None), #17
                                 (1, 1, True, None, None), #18
                                 (2, 1, True, None, None), #19
                                 (2, 3, True, None, None), #20
                                 (2, 2, True, None, None), #21
                                 (3, 4, True, None, None), #22
                                 (4, 4, True, None, None), #25
                             ], False, "Плохие копы победили! Комиссар мертв!"),
                         ],
                         )
def test_games(roles, players, starting_player, actions, expected, expected_msg):
    raises = expected
    if isinstance(expected, bool):
        raises = does_not_raise()
    mock = MockUpdateAndContext()
    with raises as error:
        game = CopGame()
        game.players_list = []
        for pl in players:
            game.add_player(pl)
        game.init_game(cards=roles, shufle=False, starting_player=starting_player)
        statebot.activeGame = game
        i = 0
        while i < len(actions):
            id, action, result, test, params = actions[i]
            mock.echo(players[id-1], action)
            i += 1
        done, winner, msg = game.status
        assert done, "game was not ended"
        assert winner == expected, "End result is wrong"
        assert expected_msg in msg
    # userlog = statebot.game_state_logger(game.n)
    log = statebot.game_state_logger(game.game_state)
    # print(userlog)
    print(log)

    # working with possible exception from here\
    print(str(error))
    if not isinstance(expected, bool):
        assert expected_msg in str(error)