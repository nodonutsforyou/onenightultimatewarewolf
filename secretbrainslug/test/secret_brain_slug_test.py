import pytest
import json
from contextlib import contextmanager
from util import *
from test.MockUpdateAndContext import MockUpdateAndContext
from secretbrainslug.secret_slug import *
import statebot

def try_cast_an_action(g, p, a, a2):
    try:
        g.action(p, a)
    except:
        g.action(p, [a, a2])

ROLES_LIST_1 = [
    Roles.HITLER,
    Roles.FASCIST,
    Roles.LIBERAL,
    Roles.LIBERAL,
    Roles.LIBERAL,
]

ROLES_LIST_2 = [
    Roles.HITLER,
    Roles.FASCIST,
    Roles.LIBERAL,
    Roles.LIBERAL,
    Roles.LIBERAL,
    Roles.LIBERAL,
]

ROLES_LIST_3 = [
    Roles.HITLER,
    Roles.FASCIST,
    Roles.LIBERAL,
    Roles.LIBERAL,
    Roles.LIBERAL,
    Roles.LIBERAL,
    Roles.FASCIST,
    Roles.LIBERAL,
    Roles.FASCIST,
    Roles.LIBERAL,
    Roles.FASCIST,
]

LAWS_LIST_1 = [
    {"type": Law.LIBERAL, "name": "lib law no 1", "description": "lib law no 1"},
    {"type": Law.LIBERAL, "name": "lib law no 2", "description": "lib law no 2"},
    {"type": Law.LIBERAL, "name": "lib law no 3", "description": "lib law no 3"},
    {"type": Law.LIBERAL, "name": "lib law no 4", "description": "lib law no 4"},
    {"type": Law.LIBERAL, "name": "lib law no 5", "description": "lib law no 5"},
    {"type": Law.LIBERAL, "name": "lib law no 6", "description": "lib law no 6"},
    {"type": Law.FASCIST, "name": "fas law no 1", "description": "fas law no 1"},
    {"type": Law.FASCIST, "name": "fas law no 2", "description": "fas law no 2"},
    {"type": Law.FASCIST, "name": "fas law no 3", "description": "fas law no 3"},
    {"type": Law.FASCIST, "name": "fas law no 4", "description": "fas law no 4"},
    {"type": Law.FASCIST, "name": "fas law no 5", "description": "fas law no 5"},
    {"type": Law.FASCIST, "name": "fas law no 6", "description": "fas law no 6"},
    {"type": Law.FASCIST, "name": "fas law no 7", "description": "fas law no 7"},
    {"type": Law.FASCIST, "name": "fas law no 8", "description": "fas law no 8"},
    {"type": Law.FASCIST, "name": "fas law no 9", "description": "fas law no 9"},
    {"type": Law.FASCIST, "name": "fas law no 10", "description": "fas law no 10"},
    {"type": Law.FASCIST, "name": "fas law no 11", "description": "fas law no 11"},
]

LAWS_LIST_2 = [
    {"type": Law.LIBERAL, "name": "lib law no 1", "description": "lib law no 1"},
    {"type": Law.LIBERAL, "name": "lib law no 3", "description": "lib law no 3"},
    {"type": Law.LIBERAL, "name": "lib law no 5", "description": "lib law no 5"},
    {"type": Law.LIBERAL, "name": "lib law no 6", "description": "lib law no 6"},
    {"type": Law.FASCIST, "name": "fas law no 1", "description": "fas law no 1"},
    {"type": Law.LIBERAL, "name": "lib law no 2", "description": "lib law no 2"},
    {"type": Law.FASCIST, "name": "fas law no 2", "description": "fas law no 2"},
    {"type": Law.LIBERAL, "name": "lib law no 3", "description": "lib law no 3"},
    {"type": Law.FASCIST, "name": "fas law no 3", "description": "fas law no 3"},
    {"type": Law.FASCIST, "name": "fas law no 4", "description": "fas law no 4"},
    {"type": Law.LIBERAL, "name": "lib law no 4", "description": "lib law no 4"},
    {"type": Law.FASCIST, "name": "fas law no 5", "description": "fas law no 5"},
    {"type": Law.LIBERAL, "name": "lib law no 5", "description": "lib law no 5"},
    {"type": Law.FASCIST, "name": "fas law no 6", "description": "fas law no 6"},
    {"type": Law.FASCIST, "name": "fas law no 7", "description": "fas law no 7"},
    {"type": Law.LIBERAL, "name": "lib law no 5", "description": "lib law no 5"},
    {"type": Law.FASCIST, "name": "fas law no 8", "description": "fas law no 8"},
    {"type": Law.LIBERAL, "name": "lib law no 5", "description": "lib law no 5"},
    {"type": Law.FASCIST, "name": "fas law no 9", "description": "fas law no 9"},
    {"type": Law.LIBERAL, "name": "lib law no 5", "description": "lib law no 5"},
    {"type": Law.FASCIST, "name": "fas law no 10", "description": "some laws desc"},
    {"type": Law.LIBERAL, "name": "lib law no 5", "description": "some laws desc"},
    {"type": Law.FASCIST, "name": "fas law no 11", "description": "some laws desc"},
]

LAWS_LIST_3 = [
    {"type": Law.FASCIST, "name": "fas law no 1", "description": "some laws desc"},
    {"type": Law.FASCIST, "name": "fas law no 2", "description": "some laws desc"},
    {"type": Law.FASCIST, "name": "fas law no 3", "description": "some laws desc"},
    {"type": Law.FASCIST, "name": "fas law no 4", "description": "some laws desc"},
    {"type": Law.FASCIST, "name": "fas law no 5", "description": "some laws desc"},
    {"type": Law.FASCIST, "name": "fas law no 6", "description": "some laws desc"},
    {"type": Law.FASCIST, "name": "fas law no 7", "description": "some laws desc"},
    {"type": Law.FASCIST, "name": "fas law no 8", "description": "some laws desc"},
    {"type": Law.FASCIST, "name": "fas law no 9", "description": "some laws desc"},
    {"type": Law.FASCIST, "name": "fas law no 10", "description": "some laws desc"},
    {"type": Law.FASCIST, "name": "fas law no 11", "description": "some laws desc"},
    {"type": Law.LIBERAL, "name": "lib law no 1", "description": "some laws desc"},
    {"type": Law.LIBERAL, "name": "lib law no 2", "description": "some laws desc"},
    {"type": Law.LIBERAL, "name": "lib law no 3", "description": "some laws desc"},
    {"type": Law.LIBERAL, "name": "lib law no 4", "description": "some laws desc"},
    {"type": Law.LIBERAL, "name": "lib law no 5", "description": "some laws desc"},
    {"type": Law.LIBERAL, "name": "lib law no 6", "description": "some laws desc"},
]

mock = MockUpdateAndContext()

@contextmanager
def does_not_raise():
    yield

@pytest.mark.parametrize("roles,laws,players,starting_player,actions,expected,expected_msg",
                         [
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_1, dummy_players[:5], 1, [
                             #     (1, 2, True, 1, 1, None), #1
                             #     (2, 3, True, 1, 1, None), #2
                             #     (3, 4, True, 1, 1, None), #3
                             #     (4, 5, True, 1, 1, None), #4
                             #     (5, 3, True, 1, 1, None), #5
                             #     (1, 2, True, 1, 1, None), #6
                             #     (2, 3, True, 1, 1, None), #7
                             #     (3, 4, True, 1, 1, 4   ), #8
                             #     (5, 2, True, 1, 1, 2   ), #9
                             #     (1, 3, True, 1, 1, None), #10
                             #     (3, 5, True, 1, 1, 5   ), #11
                             # ], False, "Фашисты избрали 6 законов! Фашисты победили!"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_2, dummy_players[:5], 1, [
                             #     (1, 2, True, 1, 1, None), #1
                             #     (2, 3, True, 1, 1, None), #2
                             #     (3, 1, True, 0, 0, None), #3
                             #     (4, 2, True, 0, 0, None), #4
                             #     (5, 1, True, 2, 0, None), #5
                             #     (1, 2, True, 0, 1, None), #6
                             # ], True, "Либералы избрали 6 законов! Либералы победили!"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_2, dummy_players[:5], 1, [
                             #     (1, 2, True, 1, 1, None), #1
                             #     (2, 3, True, 2, 1, None), #2
                             #     (3, 4, True, 0, 1, None), #3
                             #     (4, 5, True, 1, 0, None), #4
                             #     (5, 2, True, 0, 1, 2   ), #5
                             #     (1, 3, True, 0, 0, 3   ), #6
                             #     (4, 5, True, 1, 0, 5   ), #7
                             # ], False, "Фашисты избрали 6 законов! Фашисты победили!"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_2, dummy_players[:5], 1, [
                             #     (1, 2, True, 1, 1, None), #1
                             #     (2, 3, True, 2, 1, None), #2
                             #     (3, 4, True, 0, 0, None), #3
                             #     (4, 5, True, 1, 0, None), #4
                             #     (5, 1, True, 1, 0, None), #5
                             #     (1, 2, True, 0, 0, None), #6
                             #     (2, 3, True, 0, 0, None), #7
                             #     (3, 4, True, 2, 1, 4   ), #8
                             #     (5, 2, True, 0, 1, None), #9
                             #     (1, 3, True, 1, 0, 2   ), #10
                             #     (3, 5, True, 0, 1, 3   ), #11
                             # ], False, "Фашисты избрали 6 законов! Фашисты победили!"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_2, dummy_players[:5], 1, [
                             #     (1, 1, True, 1, 1, None), #1
                             # ], pytest.raises(Exception), "Нельзя выбрать себя"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_2, dummy_players[:5], 1, [
                             #     (1, 3, True, 1, 1, None), #1
                             #     (2, 3, True, 1, 1, None), #2
                             # ], pytest.raises(Exception), "Нельзя выбрать Goasha III - он был канцлером в прошлом ходу"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_2, dummy_players[:5], 1, [
                             #     (1, 3, True, 1, 1, None), #1
                             #     (2, 1, True, 1, 1, None), #2
                             # ], pytest.raises(Exception), "Нельзя выбрать Peotr I - он был президентом в прошлом ходу"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_2, dummy_players[:5], 1, [
                             #     (1, 2, True, 1, 1, None), #1
                             #     (2, 3, True, 2, 1, None), #2
                             #     (3, 4, True, 0, 1, None), #3
                             #     (4, 5, True, 1, 0, None), #4
                             #     (5, 1, True, 0, 1, None), #5
                             # ], False, "Фашисты избрали Гитлера канцлером! Фашисты победили!"),
                             pytest.param(ROLES_LIST_1, LAWS_LIST_2, dummy_players[:5], 1, [
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
                             ], False, "Фашисты избрали Гитлера канцлером! Фашисты победили!"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_2, dummy_players[:5], 1, [
                             #     (1, 2, True, 1, 1, None), #1
                             #     (2, 3, True, 2, 1, None), #2
                             #     (3, 4, True, 0, 1, None), #3
                             #     (4, 5, True, 1, 0, None), #4
                             #     (5, 2, True, 0, 1, None), #5
                             # ], pytest.raises(Exception), "action was needed"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_2, dummy_players[:5], 1, [
                             #     (1, 2, True, 1, 1, None), #1
                             #     (2, 3, True, 2, 1, None), #2
                             #     (3, 4, True, 0, 1, None), #3
                             #     (4, 5, True, 1, 0, None), #4
                             #     (5, 2, True, 0, 1, 1   ), #5
                             # ], True, "Гитлер убит! Либералы победили!"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_2, dummy_players[:5], 1, [
                             #     (1, 2, True, 1, 1, None), #1
                             #     (2, 3, True, 2, 1, None), #2
                             #     (3, 4, True, 0, 0, None), #3
                             #     (4, 5, True, 1, 0, None), #4
                             #     (5, 1, True, 1, 0, None), #5
                             #     (1, 2, True, 0, 0, None), #6
                             #     (2, 3, True, 0, 0, None), #7
                             #     (3, 4, True, 2, 1, 4   ), #8
                             #     (5, 2, True, 0, 1, None), #9
                             #     (1, 3, True, 1, 0, 2), #10
                             #     (3, 5, True, 0, 1, 1), #11
                             # ], True, "Гитлер убит! Либералы победили!"),
                             # pytest.param(ROLES_LIST_3, LAWS_LIST_2, dummy_players_large_list[:11], 1, [
                             #     (1, 2, True, 1, 1, None), #1
                             #     (2, 3, True, 2, 1, 1   ), #2
                             #     (3, 4, True, 0, 0, None), #3
                             #     (4, 5, True, 1, 0, 2   ), #4
                             #     (5, 1, True, 1, 0, None), #5
                             #     (6, 2, True, 0, 0, 3   ), #6
                             #     (3, 11, True, 0, 0, None), #7
                             #     (7, 4, True, 2, 1, 4   ), #8
                             #     (8, 5, True, 0, 1, None), #9
                             #     (9, 2, True, 1, 0, 2   ), #10
                             #     (10, 3, True, 0, 1, 3  ), #11
                             # ], False, "Фашисты избрали 6 законов! Фашисты победили!"),
                             # pytest.param(ROLES_LIST_3, LAWS_LIST_2, dummy_players_large_list[:11], 1, [
                             #     (1, 2, True, 1, 1, None), #1
                             #     (2, 3, True, 2, 1, 1   ), #2
                             #     (3, 4, True, 0, 0, None), #3
                             #     (4, 5, True, 1, 0, 2   ), #4
                             #     (5, 1, True, 1, 0, None), #5
                             #     (6, 2, True, 0, 0, 6   ), #6
                             #     (6, 11, True, 0, 0, None), #7
                             # ], pytest.raises(Exception), "Нельзя назначить себя экстренным президентом"),
                             # pytest.param(ROLES_LIST_3, LAWS_LIST_2, dummy_players_large_list[:11], 1, [
                             #     (1, 2, True, 1, 1, None), #1
                             #     (2, 3, True, 2, 1, 1   ), #2
                             #     (3, 4, True, 0, 0, None), #3
                             #     (4, 5, True, 1, 0, 2   ), #4
                             #     (5, 1, True, 1, 0, None), #5
                             #     (6, 2, True, 0, 0, 7   ), #6
                             #     (7, 11, True, 0, 0, None), #7
                             #     (7, 4, True, 2, 1, 8   ), #8
                             #     (9, 5, True, 0, 1, None), #9
                             #     (10, 2, True, 1, 0, 11 ), #10
                             #     (1, 3, True, 0, 1, 3  ), #11
                             # ], False, "Фашисты избрали 6 законов! Фашисты победили!"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_1, dummy_players[:5], 1, [
                             #     (1, 2, False, 1, 1, None), #1
                             #     (2, 3, False, 1, 1, None), #2
                             #     (3, 4, False, 1, 1, None), #3
                             #     (4, 5, False, 1, 1, None), #4
                             #     (5, 3, False, 1, 1, None), #5
                             #     (1, 2, False, 1, 1, None), #6
                             #     (2, 3, False, 1, 1, None), #7
                             #     (3, 4, False, 1, 1, None), #8
                             #     (4, 5, False, 1, 1, None), #9
                             #     (5, 2, False, 1, 1, None), #10
                             #     (1, 3, False, 1, 1, None), #11
                             #     (2, 5, False, 1, 1, None), #12
                             #     (3, 4, False, 1, 1, None), #13
                             #     (4, 5, False, 1, 1, None), #14
                             #     (5, 3, False, 1, 1, None), #15
                             #     (1, 3, False, 1, 1, None), #16
                             #     (2, 5, False, 1, 1, None), #17
                             #     (3, 4, False, 1, 1, None), #18
                             # ], True, "Либералы избрали 6 законов! Либералы победили!"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_3, dummy_players[:5], 1, [
                             #     (1, 2, False, 1, 1, None), #1
                             #     (2, 3, False, 1, 1, None), #2
                             #     (3, 4, False, 1, 1, None), #3
                             #     (4, 5, False, 1, 1, None), #4
                             #     (5, 3, False, 1, 1, None), #5
                             #     (1, 2, False, 1, 1, None), #6
                             #     (2, 3, False, 1, 1, None), #7
                             #     (3, 4, False, 1, 1, None), #8
                             #     (4, 5, False, 1, 1, None), #9
                             #     (5, 2, False, 1, 1, None), #10
                             #     (1, 3, False, 1, 1, None), #11
                             #     (2, 5, False, 1, 1, 5   ), #12
                             #     (3, 4, False, 1, 1, None), #13
                             #     (4, 2, False, 1, 1, None), #14
                             #     (1, 3, False, 1, 1, 2   ), #15
                             #     (3, 4, False, 1, 1, None), #16
                             #     (4, 1, False, 1, 1, None), #17
                             #     (1, 3, False, 1, 1, 4), #18
                             # ], False, "Фашисты избрали 6 законов! Фашисты победили!"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_1, dummy_players[:5], 1, [
                             #     (1, 2, True, 1, 1, None), #1
                             #     (2, 3, True, 1, 1, None), #2
                             #     (3, 4, True, 1, 1, None), #3
                             #     (4, 5, True, 1, 1, None), #4
                             #     (5, 3, True, 1, 1, None), #5
                             #     (1, 2, True, 1, 1, None), #6
                             #     (2, 3, True, 1, 1, None), #7
                             #     (3, 4, True, 1, 1, 4   ), #8
                             #     (5, 2, True, 1, 1, 5   ), #9
                             # ], False, "Фашисты убили либералов и теперь в большинстве"),
                             # pytest.param(ROLES_LIST_1, LAWS_LIST_3, dummy_players[:5], 1, [
                             #     (1, 2, False, 1, 1, None), #1
                             #     (2, 3, False, 1, 1, None), #2
                             #     (3, 4, False, 1, 1, None), #3
                             #     (4, 5, False, 1, 1, None), #4
                             #     (5, 3, False, 1, 1, None), #5
                             #     (1, 2, False, 1, 1, None), #6
                             #     (2, 3, False, 1, 1, None), #7
                             #     (3, 4, False, 1, 1, None), #8
                             #     (4, 5, False, 1, 1, None), #9
                             #     (5, 2, False, 1, 1, None), #10
                             #     (1, 3, False, 1, 1, None), #11
                             #     (2, 5, False, 1, 1, 5   ), #12
                             #     (3, 4, False, 1, 1, None), #13
                             #     (4, 2, False, 1, 1, None), #14
                             #     (1, 3, False, 1, 1, 2   ), #15
                             #     (3, 4, False, 1, 1, None), #16
                             #     (4, 1, False, 1, 1, None), #17
                             #     (1, 2, False, 1, 1, 4), #18
                             # ], pytest.raises(Exception), "Нельзя выбрать Vaysa II - он мертв"),
                         ],
                         )
def test_games(roles, laws, players, starting_player, actions, expected, expected_msg):
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

# @pytest.mark.parametrize("roles,laws,players,starting_player,actions,expected,expected_msg",
#                          [
#                              pytest.param(ROLES_LIST_3, LAWS_LIST_1, dummy_players_large_list[:11], 1, [
#                                  (2, True, 1, 1, None), #1
#                                  (3, True, 1, 1, None), #2
#                                  (4, True, 1, 1, 1), #3
#                              ], True, "Peotr I - фашист"),
#                              pytest.param(ROLES_LIST_3, LAWS_LIST_1, dummy_players_large_list[:11], 1, [
#                                  (2, True, 1, 1, None), #1
#                                  (3, True, 1, 1, None), #2
#                                  (4, True, 1, 1, 11), #3
#                              ], True, "Sputnik XI - фашист"),
#                              pytest.param(ROLES_LIST_3, LAWS_LIST_1, dummy_players_large_list[:11], 1, [
#                                  (2, True, 1, 1, None), #1
#                                  (3, True, 1, 1, None), #2
#                                  (4, True, 1, 1, 3), #3
#                              ], True, "Goasha III - либерал"),
#                          ]
#                          )
# def test_investigate(roles, laws, players, starting_player, actions, expected, expected_msg):
#     raises = expected
#     if isinstance(expected, bool):
#         raises = does_not_raise()
#     turn = 1
#     with raises as error:
#         game = Game()
#         for pl in players:
#             game.add_player(pl)
#         game.init_game(roles=roles, laws=laws, starting_player=starting_player)
#         check, result = None, None
#         while turn <= len(actions):
#             c, v, cp, pp, a = actions[turn-1]
#             r, msg = game.pick_chancellor(players[starting_player-1], c)
#             if not r:
#                 print(msg)
#             assert r, msg
#             votes = {}
#             for i in range(1, len(players)+1):
#                 if isinstance(v, bool):
#                     votes[i] = v
#                 else:
#                     votes[i] = v[i]
#             for key, vote in votes.items():
#                 game.vote(players[key-1], vote)
#             assert game.check_votes_cast()
#             r, msg = game.implement_votes(shuffle=False)
#             if r is None:
#                 turn += 1
#                 continue
#             game.legislation(players[c-1], cp)
#             game.legislation(players[starting_player-1], pp)
#             r, msg = game.implement_action()
#             if not r:
#                 if a is None:
#                     print("turn " + str(turn))
#                     assert not (a is None), "action was needed"
#                 check, result, msg_all = game.action(players[starting_player-1], a)
#                 assert check, msg
#                 r = game.implement_action()
#             else:
#                 assert a is None, "action was planned for this turn " + str(turn)
#             if not r:
#                 print(r)
#             assert r
#             r = game.new_turn(shuffle=False)
#             if not (r or turn == len(actions)):
#                 print(r)
#             assert r or turn == len(actions)
#             starting_player += 1
#             if starting_player >= len(players):
#                 starting_player = 0
#             turn += 1
#         game_end, side_won, msg = game.status
#         assert game_end
#         assert expected_msg in result
#         assert check == expected
#
#     # working with possible exception from here\
#     print(str(error))
#     if not isinstance(expected, bool):
#         assert expected_msg in str(error)
#
#
# @pytest.mark.parametrize("roles,laws,players,starting_player,actions,expected_turn,expected_msg",
#                          [
#                              pytest.param(ROLES_LIST_1, LAWS_LIST_2, dummy_players[:5], 1, [
#                                  (1, 2, True, 1, 1, None), #1
#                                  (2, 3, True, 2, 1, None), #2
#                                  (3, 4, True, 0, 1, None), #3
#                                  (4, 5, True, 1, 0, None), #4
#                                  (5, 1, True, 0, 1, None), #5
#                              ], 5,  "Peotr I оказался Гитлером!"),
#                          ],
#                          )
# def test_hitler_on_law_3(roles, laws, players, starting_player, actions, expected_turn, expected_msg):
#     turn = 1
#     game = Game()
#     game.players_list = []
#     for pl in players:
#         game.add_player(pl)
#     game.init_game(roles=roles, laws=laws, starting_player=starting_player)
#     while turn <= len(actions):
#         p, c, v, cp, pp, a = actions[turn-1]
#         r, msg = game.pick_chancellor(players[p-1], c)
#         if not r:
#             print(msg)
#         assert r, str(msg) + " turn " + str(turn)
#         votes = {}
#         for i in range(1, len(players)+1):
#             if isinstance(v, bool):
#                 if v:
#                     votes[i] = 1
#                 else:
#                     votes[i] = 0
#             else:
#                 votes[i] = v[i]
#         for key, vote in votes.items():
#             game.vote(players[key-1], vote)
#         assert game.check_votes_cast()
#         r, msg = game.implement_votes(shuffle=False)
#         if r is None:
#             if turn == expected_turn:
#                 assert expected_msg in msg
#             turn += 1
#             continue
#         if isinstance(v, bool) and v:
#             game.legislation(players[c-1], cp)
#             assert game.check_president_legislation_is_ready()
#             game.legislation(players[p-1], pp)
#         r, msg = game.implement_action()
#         if not r:
#             if a is None:
#                 lib, fas = game.count_laws()
#                 action = game.select_action(fas)
#                 if action == Actions.PEEK:
#                     r = True
#                 else:
#                     print("turn " + str(turn))
#                     assert not (a is None), "action was needed turn " + str(turn)
#             else:
#                 ra, msg = game.action(players[p-1], a)
#                 assert ra, str(msg)
#                 r = game.implement_action()
#         else:
#             assert a is None, "No action was planned for this turn " + str(turn)
#         if not r:
#             print(r)
#         assert r
#         r = game.new_turn(shuffle=False)
#         if not (r or turn == len(actions)):
#             print(r)
#         assert r or turn == len(actions)
#         turn += 1
#
#
# @pytest.mark.parametrize("roles,players,player_to_check,expected_msg",
#                          [
#                              pytest.param(ROLES_LIST_1, dummy_players[:5], 5,  "Вы либерал"),
#                              pytest.param(ROLES_LIST_3, dummy_players_large_list[:10], 1,  "Вы Гитлер! Остальные фашисты: Vaysa II, Peotr2 VII, Goasha2 IX"),
#                              pytest.param(ROLES_LIST_3, dummy_players_large_list[:10], 2,  "Вы фашист! Peotr I Гитлер Остальные фашисты: Vaysa II, Peotr2 VII, Goasha2 IX"),
#                              pytest.param(ROLES_LIST_3, dummy_players_large_list[:10], 7,  "Вы фашист! Peotr I Гитлер Остальные фашисты: Vaysa II, Peotr2 VII, Goasha2 IX"),
#                          ],
#                          )
# def test_init_messages(roles, players, player_to_check, expected_msg):
#     game = Game()
#     game.players_list = []
#     for pl in players:
#         game.add_player(pl)
#     game.init_game(roles=roles)
#     msg = game.get_init_message(game.n[player_to_check])
#     assert expected_msg in msg


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