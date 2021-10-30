import pytest
import json
from onuwgame import Game, Roles
from contextlib import contextmanager

dummy_players = [
    {'first_name': 'Peotr', 'last_name': 'I', 'id': "1", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Vaysa', 'last_name': 'II', 'id': "2", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Goasha', 'last_name': 'III', 'id': "3", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'IVAN', 'last_name': 'IV', 'id': "4", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Sputnik', 'last_name': 'V', 'id': "5", 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Ruslan', 'last_name': 'VI', 'id': "6", 'language_code': 'en', 'is_bot': False},
]

def try_cast_an_action(g, p, a, a2):
    try:
        g.action(p, a)
    except:
        g.action(p, [a, a2])

ROLES_LIST_1 = [
    Roles.WEREWOLF,
    Roles.WEREWOLF,
    Roles.VILLAGER,
    Roles.TROUBLEMAKER,
    Roles.ROBBER,
    Roles.SEER,
]

ROLES_LIST_2 = [
    Roles.VILLAGER,         # 1
    Roles.VILLAGER,         # 2
    Roles.VILLAGER,         # 3
    Roles.WEREWOLF,         # 4
    Roles.WEREWOLF,         # 5
    Roles.VILLAGER,         # 6
    Roles.TROUBLEMAKER,     # 7
    Roles.ROBBER,           # 8
    Roles.SEER,             # 9
]

ROLES_LIST_3 = [
    Roles.VILLAGER,         # 1
    Roles.VILLAGER,         # 2
    Roles.WEREWOLF,         # 3
    Roles.VILLAGER,         # 4
    Roles.WEREWOLF,         # 5
    Roles.VILLAGER,         # 6
    Roles.TROUBLEMAKER,     # 7
    Roles.ROBBER,           # 8
    Roles.SEER,             # 9
]

ROLES_LIST_4 = [
    Roles.VILLAGER,         # 1
    Roles.WEREWOLF,         # 2
    Roles.WEREWOLF,         # 3
    Roles.VILLAGER,         # 4
    Roles.VILLAGER,         # 5
    Roles.VILLAGER,         # 6
    Roles.TROUBLEMAKER,     # 7
    Roles.ROBBER,           # 8
    Roles.SEER,             # 9
]

ROLES_LIST_5_WITH_INSOMNIAC = [
    Roles.VILLAGER,         # 1
    Roles.WEREWOLF,         # 2
    Roles.WEREWOLF,         # 3
    Roles.INSOMNIAC,        # 4
    Roles.VILLAGER,         # 5
    Roles.VILLAGER,         # 6
    Roles.TROUBLEMAKER,     # 7
    Roles.ROBBER,           # 8
    Roles.SEER,             # 9
]

@contextmanager
def does_not_raise():
    yield

@pytest.mark.parametrize("roles,players,actions,votes,expected,expected_msg",
                         [
                             pytest.param(ROLES_LIST_1, dummy_players[:3], [[5, 6], [4], [1, 2]], [0, 0, 0], True, "Вы все победили"),
                             pytest.param(ROLES_LIST_1, dummy_players[:3], [[5, 6], [4], [1, 2]], [5, 6, 4], True, "Вы все победили"),
                             pytest.param(ROLES_LIST_1, dummy_players[:3], [[5, 6], [4], [1, 2]], [5, 4, 4], False, "Убитый Peotr I оказался невиновным"),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [5, 6, 5, 5, 5, 5], False, "Убитый Vaysa II оказался невинным человеком"),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [5, 6, 7, 8, 9, 4], False, "Peotr I и Goasha III оказались оборотнями"),
                             pytest.param(ROLES_LIST_3, dummy_players, [[], [], [], [6, 8], [5], [4]], [5, 6, 7, 8, 9, 4], False, "Goasha III оказался оборотнем"),
                             pytest.param(ROLES_LIST_4, dummy_players, [[], [], [], [6, 8], [5], [4]], [5, 6, 5, 6, 5, 6], False, "Убитые Vaysa II, Goasha III оказались"),
                             pytest.param(ROLES_LIST_4, dummy_players, [[], [], [], [6, 8], [5], [4]], [5, 6, 7, 5, 6, 7], False, "Убитые Vaysa II, Goasha III, IVAN IV оказались"),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [6, 6, 6, 6, 6, 6], True, "Убитый Goasha III оказался"),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [6, 6, 7, 4, 4, 8], True, "Убитые Peotr I и Goasha III оказались оборотнями"),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [8, 8, 8, 8, 8, 6], False, "Убитый Sputnik V оказался невинным человеком"),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [8, 8, 9, 9, 5, 5], False, "Убитые Vaysa II, Sputnik V, Ruslan VI"),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 6, 6, 6, 8], [5], [4]], [6, 6, 7, 4, 4, 8], True, "Убитые Peotr I и Goasha III оказались оборотнями"),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 6, 6, 8], [5], [4]], [8, 8, 8, 8, 8, 6], False, "Убитый Sputnik V оказался невинным человеком"),
                             pytest.param(ROLES_LIST_5_WITH_INSOMNIAC, dummy_players, [[], [], [], [6, 8], [5], [4]], [5, 6, 7, 5, 6, 7], False, "Убитые Vaysa II, Goasha III, IVAN IV оказались"),
                             # one less vote here
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [6, 6, 6, 6, 6], pytest.raises(Exception), "not all votes are cast"),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 6], [5], [4]], [6, 6, 6, 6, 6, 6], pytest.raises(Exception), "not all actions are cast"),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8, 4], [5], []], [6, 6, 6, 6, 6, 6], pytest.raises(Exception), "not all actions are cast"),
                         ],
                         )
def test_games(roles, players, actions, votes, expected, expected_msg):
    raises = expected
    if isinstance(expected, bool):
        raises = does_not_raise()
    with raises as error:
        game = Game()
        for pl in players:
            game.add_player(pl)
        game.init_game(roles)
        for pl, acs in zip(players, actions):
            pl_obj = get_pl_by_name(game, pl["first_name"])
            msg, options = game.get_init_message(pl_obj)
            options_num = flatten_button_list(options)
            for a in acs:
                assert str(a) in options_num
                game.action(pl, a)
        assert game.check_actions_cast(), "not all actions are cast"
        game.implement_actions()

        for pl, v in zip(players, votes):
            assert not game.check_votes_cast()
            game.vote(pl, v)
        assert game.check_votes_cast(), "not all votes are cast"

        res, msg = game.implement_votes()
        print(res, msg)
        if isinstance(expected, bool):
            assert expected == res, msg
        assert expected_msg in msg
    # working with possible exception from here\
    print(str(error))
    if not isinstance(expected, bool):
        assert expected_msg in str(error)


def get_pl_by_name(game, name):
    for p in game.pl:
        if name in p["name"]:
            return p


@pytest.mark.parametrize("roles,players,actions,votes,expected_role",
                         [
                             pytest.param(ROLES_LIST_5_WITH_INSOMNIAC, dummy_players, [[], [], [], [4, 5], [5], [4]], [5, 6, 5, 5, 5, 5], Roles.ROBBER),
                             pytest.param(ROLES_LIST_5_WITH_INSOMNIAC, dummy_players, [[], [], [], [4, 8], [4], [4]], [5, 6, 5, 5, 5, 5], Roles.INSOMNIAC),
                             pytest.param(ROLES_LIST_5_WITH_INSOMNIAC, dummy_players, [[], [], [], [5, 8], [4], [4]], [5, 6, 5, 5, 5, 5], Roles.ROBBER),
                             pytest.param(ROLES_LIST_5_WITH_INSOMNIAC, dummy_players, [[], [], [], [4, 2], [4], [4]], [5, 6, 5, 5, 5, 5], Roles.WEREWOLF),
                         ],
                         )
def test_insomniac(roles, players, actions, votes, expected_role):
    game = Game()
    for pl in players:
        game.add_player(pl)
    game.init_game(roles)
    for pl, acs in zip(players, actions):
        for a in acs:
            game.action(pl, a)
    game.implement_actions()
    for p in game.pl:
        if p["starts_as"] == Roles.INSOMNIAC:
            assert p["new_role"] == expected_role
            print(p["msg"])


@pytest.mark.parametrize("run", range(10))
def test_shufle_roles(run):
    game = Game()
    for pl in dummy_players:
        game.add_player(pl)
    game.init_game()
    assigned_roles = [p["starts_as"] for p in game.pl]
    role_count = {}
    for r in Roles:
        role_count[r] = 0
    for r in assigned_roles:
        role_count[r] += 1
    assert len(dummy_players) == 6
    assert len(assigned_roles) == 9
    assert role_count[Roles.VILLAGER] == 4
    assert role_count[Roles.WEREWOLF] == 2
    assert role_count[Roles.TROUBLEMAKER] == 1
    assert role_count[Roles.ROBBER] == 1
    assert role_count[Roles.SEER] == 1

@pytest.mark.parametrize("table, exclude_id, vote_all, assert_included, assert_excluded",
                         [
                             (True, "1", None, ['1', '2', '3', '5', '6', '7', '8', '9'], ['4', '0']),
                             (False, "2", None, ['4', '6', '7', '8', '9'], ['1', '2', '3', '5', '0']),
                             (False, None, None, ['4', '5', '6', '7', '8', '9'], ['1', '2', '3', '0']),
                             (False, None, True, ['4', '5', '6', '7', '8', '9', '0'], ['1', '2', '3']),
                             (False, "3", True, ['4', '5', '7', '8', '9', '0'], ['1', '2', '3', '6']),
                         ])
def test_exclude_id(table, exclude_id, vote_all, assert_included, assert_excluded):
    game = Game()
    for pl in dummy_players:
        game.add_player(pl)
    game.init_game()
    vote_all_msg = "vote all" if vote_all is not None else None
    msg = game.get_buttons_list(tables=table, exclude_id=exclude_id, vote_all_str=vote_all_msg)
    for row in msg:
        assert len(row) < 4, str(row) + "len greater than 3"
    joined_list = flatten_button_list(msg)
    for ai in assert_included:
        assert ai in joined_list
    for ae in assert_excluded:
        assert ae not in joined_list
    print(joined_list)


def flatten_button_list(msg):
    if msg is None:
        return []
    joined_list = []
    for l in msg:
        joined_list += [b for a, b in l]
    return joined_list

