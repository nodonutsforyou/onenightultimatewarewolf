import pytest
from say_anything.say_anything import SayAnythingGame
from contextlib import contextmanager
import statebot
from util import dummy_players, dummy_players_large_list
from player import Player
from test.MockUpdateAndContext import MockUpdateAndContext

@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize("players,starting_player,actions,expected,expected_msg",
                         [
                             pytest.param(dummy_players, 1, [
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
def test_games(players, starting_player, actions, expected, expected_msg):
    raises = expected
    if isinstance(expected, bool):
        raises = does_not_raise()
    mock = MockUpdateAndContext()
    with raises as error:
        game = SayAnythingGame()
        mock.turn_callback = game.get_current_turn
        mock.set_game(game)
        mock.log = {}
        game.players_list = []
        for pl in players:
            game.add_player(pl)
        game.init_game(starting_player=starting_player)
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