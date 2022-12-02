import pytest
import json
from contextlib import contextmanager
from util import *
from test.MockUpdateAndContext import MockUpdateAndContext
from whoami.whoami import *
import statebot

def try_cast_an_action(g, p, a, a2):
    try:
        g.action(p, a)
    except:
        g.action(p, [a, a2])

counter_role = 0

def get_roles():
    global counter_role
    while True:
        counter_role += 1
        yield "role_" + str(counter_role)


mock = MockUpdateAndContext()


@contextmanager
def does_not_raise():
    yield

@pytest.mark.parametrize("player,actions,expected",
                         [
                             pytest.param(dummy_players, [
                                 (1, 2, True, 1, 1, None), #1
                                 (2, 3, True, 2, 1, None), #2
                                 (3, 4, True, 0, 0, None), #3
                                 (4, 5, True, 1, 0, None), #4
                                 (5, 1, True, 1, 0, None), #5
                                 (1, 2, True, 0, 0, None), #6
                                 (2, 3, True, 0, 0, None), #7
                                 (3, 4, True, 2, 1, 4   ), #8
                                 (5, 2, True, 0, 1, None), #9
                                 (1, 3, False, 1, 0, None), #10
                                 (2, 5, False, 1, 0, 5   ), #11
                                 (3, 1, True, 1, 0, None), #12
                             ], True),
                         ],
                         )
def test_games(players, actions, expected):
    global mock
    raises = expected
    if isinstance(expected, bool):
        raises = does_not_raise()
    turn = 1
    mock = MockUpdateAndContext()
    with raises as error:
        statebot.switch_game(statebot.Games.SECRET_HITLER)
        game = statebot.activeGame
        game.players_list = []
        for pl in players:
            game.add_player(pl)
        game.OPTION_SHUFFLE = False
        game.init_game(roles=roles, laws=laws, starting_player=starting_player)
        laws_count = len(game.laws_deck)
        while turn <= len(actions):
            p, c, v, cp, pp, a = actions[turn-1]
            mock.echo(players[p-1], c)
            state, msg, r = get_last_state_and_msg(game)
            if r is None:
                print(state)
            assert 'PRESIDENT->VOTE' in state, msg
            assert players[c-1]["first_name"] in msg
            votes = {}
            for i in range(1, len(players)+1):
                if isinstance(v, bool):
                    if v:
                        votes[i] = 1
                    else:
                        votes[i] = -1
                else:
                    votes[i] = v[i]
            for key, vote in votes.items():
                mock.echo(players[key-1], vote)
            state, msg, r = get_last_state_and_msg(game)
            if 'VOTE->LEGISLATURE_C' in state:
                assert str(c) in r.next_actions
                mock.echo(players[c - 1], cp)
                state, msg, r = get_last_state_and_msg(game)
                assert 'LEGISLATURE_C->LEGISLATURE_P' in state
                mock.echo(players[p - 1], pp)
                state, msg, r = get_last_state_and_msg(game)
            if a is not None:
                mock.echo(players[p-1], a)
                state, msg, r = get_last_state_and_msg(game)
            else:
                pass
            if not ("NEW_TURN" in state or "END_GAME" in state):
                print(state)
            assert "NEW_TURN" in state or "END_GAME" in state
            laws_count_deck = len(game.laws_deck)
            laws_count_in_action = len(game.laws_in_action)
            laws_count_discarded = len(game.laws_discard)
            lib, fas = game.count_laws()
            assert lib + fas == laws_count_in_action, f"{lib} lib + {fas} fas != {laws_count_in_action} in action, turn {turn}"
            assert laws_count_deck + laws_count_in_action + laws_count_discarded == laws_count, f"{laws_count_deck} deck + {laws_count_in_action} in action + {laws_count_discarded} discarded != {laws_count} total, turn {turn}"
            turn += 1
        game_end, side_won, msg = game.status
        assert expected == side_won
        assert msg == expected_msg
    userlog = mock.log
    log = game.game_state
    print(userlog)
    print(log)

    # working with possible exception from here\
    print(str(error))
    if not isinstance(expected, bool):
        assert expected_msg in str(error)


def get_pl_by_name(game, name):
    for p in game.pl:
        if name in p["name"]:
            return p


def flatten_button_list(msg):
    if msg is None:
        return []
    joined_list = []
    for l in msg:
        joined_list += [b for a, b in l]
    return joined_list


def get_last_message_to_id(mock, id=None) -> str:
    i = 0
    while i < len(mock.log):
        logs = mock.log[mock.turn_callback() - i]
        j = 1
        while j <= len(logs):
            line = logs[-j]
            if id is None or line.startswith(f"to {id}"):
                return line
            j += 1
        i += 1
    raise Exception("Not found")

def flatten_messages(result):
    s = ""
    if result is None:
        print(result)
    for key, msg in result.next_actions.items():
        s += str(msg.msg) + "\n"
    return s


def get_last_state_and_msg(game):
    log = game.current_turn_state()["logs"]
    if len(log) == 0:
        log = game.prev_turn_state()["logs"]
    state, r = log[-1]
    return state, flatten_messages(r), r