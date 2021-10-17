import pytest
import json
from onuwgame import Game

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
    "оборотень",
    "оборотень",
    "мирный",
    "баламут",
    "вор",
    "ясновидящий",
]

ROLES_LIST_2 = [
    "мирный",       # 1
    "мирный",       # 2
    "мирный",       # 3
    "оборотень",    # 4
    "оборотень",    # 5
    "мирный",       # 6
    "баламут",      # 7
    "вор",          # 8
    "ясновидящий",  # 9
]

ROLES_LIST_3 = [
    "мирный",       # 1
    "мирный",       # 2
    "оборотень",    # 3
    "мирный",       # 4
    "оборотень",    # 5
    "мирный",       # 6
    "баламут",      # 7
    "вор",          # 8
    "ясновидящий",  # 9
]

ROLES_LIST_4 = [
    "мирный",       # 1
    "оборотень",    # 2
    "оборотень",    # 3
    "мирный",       # 4
    "мирный",       # 5
    "мирный",       # 6
    "баламут",      # 7
    "вор",          # 8
    "ясновидящий",  # 9
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