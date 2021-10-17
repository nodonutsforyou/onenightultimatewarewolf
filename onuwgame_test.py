import pytest
import json
from onuwgame import Game, Roles

dummy_players = [
    {'first_name': 'Peotr', 'last_name': 'I', 'id': 1, 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Vaysa', 'last_name': 'II', 'id': 2, 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Goasha', 'last_name': 'III', 'id': 3, 'language_code': 'en', 'is_bot': False},
    {'first_name': 'IVAN', 'last_name': 'IV', 'id': 4, 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Sputnik', 'last_name': 'V', 'id': 5, 'language_code': 'en', 'is_bot': False},
    {'first_name': 'Ruslan', 'last_name': 'VI', 'id': 6, 'language_code': 'en', 'is_bot': False},
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

@pytest.mark.parametrize("roles,players,actions,votes,expected",
                         [
                             pytest.param(ROLES_LIST_1, dummy_players[:3], [[5, 6], [4], [1, 2]], [0, 0, 0], True),
                             pytest.param(ROLES_LIST_1, dummy_players[:3], [[5, 6], [4], [1, 2]], [5, 6, 4], True),
                             pytest.param(ROLES_LIST_1, dummy_players[:3], [[5, 6], [4], [1, 2]], [5, 4, 4], False),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [5, 6, 5, 5, 5, 5], False),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [5, 6, 7, 8, 9, 4], False),
                             pytest.param(ROLES_LIST_3, dummy_players, [[], [], [], [6, 8], [5], [4]], [5, 6, 7, 8, 9, 4], False),
                             pytest.param(ROLES_LIST_4, dummy_players, [[], [], [], [6, 8], [5], [4]], [5, 6, 5, 6, 5, 6], False),
                             pytest.param(ROLES_LIST_4, dummy_players, [[], [], [], [6, 8], [5], [4]], [5, 6, 7, 5, 6, 7], False),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [6, 6, 6, 6, 6, 6], True),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [6, 6, 7, 4, 4, 8], True),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [8, 8, 8, 8, 8, 6], False),
                             pytest.param(ROLES_LIST_2, dummy_players, [[], [], [], [6, 8], [5], [4]], [8, 8, 9, 9, 5, 5], False),
                             pytest.param(ROLES_LIST_5_WITH_INSOMNIAC, dummy_players, [[], [], [], [6, 8], [5], [4]], [5, 6, 7, 5, 6, 7], False),
                         ],
                         )
def test_games(roles, players, actions, votes, expected):
    game = Game()
    for pl in players:
        game.add_player(pl)
    game.init_game(roles)
    for pl, acs in zip(players, actions):
        for a in acs:
            game.action(pl, a)
            # print("game.check_actions_cast()" + str(game.check_actions_cast()))
    # print("game.check_actions_cast()" + str(game.check_actions_cast()))

    game.implement_actions()

    for pl, v in zip(players, votes):
        game.vote(pl, v)
        # print("game.check_votes_cast()" + str(game.check_votes_cast()))

    res, msg = game.implement_votes()
    print(res, msg)
    assert expected == res, msg

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
            # print("game.check_actions_cast()" + str(game.check_actions_cast()))
    # print("game.check_actions_cast()" + str(game.check_actions_cast()))

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
