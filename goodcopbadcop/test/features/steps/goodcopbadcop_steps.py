from behave import *
import pytest
import json
import copy
from collections import namedtuple
from goodcopbadcop.goodcopbadcop import CopGame, CopPlayer, Actions, Roles, Equipment
from contextlib import contextmanager
import statebot
from util import dummy_players, dummy_players_large_list, Result, ReplyTo, flatten_buttons
from test.MockUpdateAndContext import MockUpdateAndContext

game = CopGame()
mock = MockUpdateAndContext()
players = []
spetial_players = {}

INVESTIGATE = 1
EQUIP = 2
ARM = 3
SHOOT = 4
AIM = 5
USE = 6


def reset_all():
    global game, players, mock, spetial_players
    game = CopGame()
    game.players_list = []
    mock.turn_callback = game.get_current_turn
    mock.set_game(game)
    mock.log = {}
    spetial_players = {}
    statebot.logger.propagate = False


@given('we start a simple game')
def step_impl(context):
    reset_all()
    global game, players
    players = copy.deepcopy(dummy_players)
    for pl in players:
        game.add_player(pl)
    game.init_game(starting_player=1)


@given('we start a game with user {user} having {item}')
def step_impl(context, user, item):
    reset_all()
    global game, players
    game.OPTIONS_USE_EQIPMENT = True
    players = copy.deepcopy(dummy_players)
    for pl in players:
        game.add_player(pl)
    game.init_game(starting_player=1)
    user_n, user = get_user(user)
    user.equipment = [Equipment[item]]


@when('user {active_user} investigates card {card} of user {target}')
def step_impl(context, active_user, card, target):
    global game, players, mock
    active_user_n, active_user = get_user(active_user)
    target_n, target = get_user(target)
    card = int(card)
    mock.echo(players[active_user_n-1], INVESTIGATE)
    state_msg, msg, cmds = get_last_log_result_commands()
    assert "ACTION_SELECT->INVESTIGATE" in state_msg, state_msg
    assert 'Выберите игрока для проверки' in msg, msg
    assert target_n in cmds, cmds
    mock.echo(players[active_user_n-1], target_n)
    state_msg, msg, cmds = get_last_log_result_commands()
    assert "INVESTIGATE->INVESTIGATE_CARD_SELECT" in state_msg
    assert 'Выберите карту' in msg
    assert card in cmds
    mock.echo(players[active_user_n-1], card)
    check_turn_ends()


@when('user {active_user} uses card item on user {target}. Target opens card {card}')
def step_impl(context, active_user, card, target):
    global game, players, mock
    active_user_n, active_user = get_user(active_user)
    spetial_players["item_user"] = active_user_n
    target_n, target = get_user(target)
    card = int(card)
    mock.echo(players[active_user_n-1], USE)
    state_msg, msg, cmds = get_last_log_result_commands()
    assert 'ACTION_SELECT->USE_PLAYER_SELECT' in state_msg, state_msg
    assert 'Выберите игрока' in msg, msg
    assert target_n in cmds, cmds
    mock.echo(players[active_user_n-1], target_n)
    state_msg, msg, cmds = get_last_log_result_id_commands(target)
    assert 'USE_PLAYER_SELECT->USE_CARD_SELECT' in state_msg, state_msg
    assert card in cmds, cmds
    mock.echo(players[target_n-1], card)
    check_turn_ends()


@when('user {active_user} uses item on user {target}')
def step_impl(context, active_user, target):
    global game, players, mock
    active_user_n, active_user = get_user(active_user)
    spetial_players["item_user"] = active_user_n
    target_n, target = get_user(target)
    mock.echo(players[active_user_n-1], USE)
    state_msg, msg, cmds = get_last_log_result_commands()
    assert 'ACTION_SELECT->USE_PLAYER_SELECT' in state_msg, state_msg
    assert 'Выберите игрока' in msg, msg
    assert target_n in cmds, cmds
    mock.echo(players[active_user_n-1], target_n)
    check_turn_ends()


@when('user {active_user} uses BLACKMAIL to gie victory to enemy leader')
def step_impl(context, active_user):
    global game, players, mock
    active_user_n, active_user = get_user(active_user)
    enemy_leader = game.find_enemy_leader(active_user.team())
    spetial_players["enemy_leader"] = enemy_leader.num
    team_leader = game.find_team_leader(active_user.team())
    spetial_players["team_leader"] = team_leader.num
    team_leader_card = -1
    enemy_leader_card = -1
    for key, value in team_leader.cards.items():
        if value == Roles.KINGPIN or value == Roles.AGENT:
            team_leader_card = key
    for key, value in enemy_leader.cards.items():
        if not (value == Roles.KINGPIN or value == Roles.AGENT):
            enemy_leader_card = key
    # Use item
    mock.echo(players[active_user_n-1], USE)
    state_msg, msg, cmds = get_last_log_result_commands()
    assert 'ACTION_SELECT->USE_PLAYER_SELECT' in state_msg, state_msg
    assert 'Выберите первого игрока чтобы использовать 👹 шантаж' in msg, msg
    assert team_leader.num in cmds, cmds
    # pick team leader
    mock.echo(players[active_user_n-1], team_leader.num)
    state_msg, msg, cmds = get_last_log_result_commands()
    assert 'USE_PLAYER_SELECT->USE_CARD_SELECT' in state_msg, state_msg
    assert team_leader_card in cmds, cmds
    # pick leader card
    mock.echo(players[active_user_n-1], team_leader_card)
    state_msg, msg, cmds = get_last_log_result_commands()
    assert 'USE_CARD_SELECT->USE_PLAYER_SELECT' in state_msg, state_msg
    assert enemy_leader.num in cmds, cmds
    # pick enemy leader
    mock.echo(players[active_user_n-1], enemy_leader.num)
    state_msg, msg, cmds = get_last_log_result_commands()
    assert 'USE_PLAYER_SELECT->USE_CARD_SELECT' in state_msg, state_msg
    assert enemy_leader_card in cmds, cmds
    # pick leader card
    mock.echo(players[active_user_n-1], enemy_leader_card)
    check_end_game()


@when('user {active_user} uses RESTRAINING_ORDER on user {target}')
def step_impl(context, active_user, target):
    global game, players, mock
    active_user_n, active_user = get_user(active_user)
    target_n, target = get_user(target)
    # Use item
    mock.echo(players[active_user_n-1], USE)
    state_msg, msg, cmds = get_last_log_result_commands()
    assert 'ACTION_SELECT->USE_PLAYER_SELECT' in state_msg, state_msg
    assert 'Выберите игрока' in msg, msg
    assert target_n in cmds, cmds
    # pick target
    mock.echo(players[active_user_n-1], target_n)
    state_msg, msg, cmds = get_last_log_result_id_commands(target)
    assert "USE_ACTION_SELECT" in state_msg
    assert 'вы обязаны выбрать другую цель' in msg


@when('user {active_user} uses item')
def step_impl(context, active_user):
    global game, players, mock, spetial_players
    active_user_n, active_user = get_user(active_user)
    mock.echo(players[active_user_n-1], USE)
    spetial_players["item_user"] = active_user_n


@when('user {active_user} arms himself and aims at {target_desc}')
def step_impl(context, active_user, target_desc):
    global game, players, mock, spetial_players
    active_user_n, active_user = get_user(active_user)
    target_n, target = None, None
    if target_desc == "enemy leader":
        enemy_leader = game.find_enemy_leader(active_user.team())
        spetial_players["enemy_leader"] = enemy_leader.num
        target = enemy_leader
        target_n = enemy_leader.num
    elif target_desc == "enemy non-leader":
        enemy_leader = game.find_enemy_leader(active_user.team())
        for key, p in game.n.items():
            if p.id != enemy_leader.id and p.team() != active_user.team():
                target_n, target = key, p
        spetial_players["enemy_non-leader"] = target.num
    else:
        target_n, target = get_user(target_desc)
    mock.echo(players[active_user_n-1], ARM)
    state_msg, msg, cmds = get_last_log_result_commands()
    #TODO возможно карты уже раскрыты
    assert "ACTION_SELECT->FLIP_ONE_CARD" in state_msg, state_msg
    assert 'Вам нужно раскрыть одну из своих карт' in msg, msg
    assert len(cmds) > 0
    mock.echo(players[active_user_n-1], cmds[0])
    state_msg, msg, cmds = get_last_log_result_id_commands(active_user)
    assert "AIM" in state_msg
    assert 'В кого направить пистолет?' in msg
    assert target_n in cmds
    mock.echo(players[active_user_n-1], target_n)
    check_turn_ends()


@when('user {active_user} aims at enemy leader')
def step_impl(context, active_user):
    global game, players, mock, spetial_players
    active_user_n, active_user = get_user(active_user)
    enemy_leader = game.find_enemy_leader(active_user.team())
    enemy_leader: CopPlayer
    spetial_players["enemy_leader"] = enemy_leader.num
    mock.echo(players[active_user_n-1], enemy_leader.num)
    check_turn_ends()


@when('user {active_user} shoots')
def step_impl(context, active_user):
    global game, players, mock, spetial_players
    active_user_n, active_user = get_user(active_user)
    target = game.n[active_user.aim]
    target: CopPlayer
    mock.echo(players[active_user_n-1], SHOOT)
    if target.check_leader() and target.dead:
        check_end_game()
    else:
        check_turn_ends()
    assert not active_user.gun, "active_user still has gun"


@when('we play the game until it is turn of user {user}')
def step_impl(context, user):
    global game, players, mock
    target_n, target = get_user(user)
    active_player_n, active_player = get_user('active_player')
    while active_player_n != target_n:
        mock.echo(players[active_player_n-1], INVESTIGATE)
        state_msg, msg, cmds = get_last_log_result_commands()
        assert "ACTION_SELECT->INVESTIGATE" in state_msg, state_msg
        assert 'Выберите игрока для проверки' in msg, msg
        assert len(cmds) > 0
        mock.echo(players[active_player_n-1], cmds[0])
        end_turn, result = either_action_or_end_turn()
        if not end_turn:
            state_msg, msg, cmds = result
            assert "INVESTIGATE->INVESTIGATE_CARD_SELECT" in state_msg
            assert 'Выберите карту' in msg
            assert len(cmds) > 0
            mock.echo(players[active_player_n-1], cmds[0])
            if active_player.gun:
                assert False #TODO if player has gun, there sould be aim
            check_turn_ends()
        active_player_n, active_player = get_user('active_player')
    assert active_player.num == target_n


@then('user {user} saw card {card} of user {target} last turn')
def step_impl(context, user, card, target):
    global game
    user_n, user = get_user(user)
    target_n, target = get_user(target)
    log = mock.log
    prev_turn = mock.turn_callback() - 1
    msg_to_look = f'to {user_n}: Вы узнали, что у {target.name} карта №{card} - {target.cards[int(card)].value}'
    found = False
    for line in log[prev_turn]:
        if msg_to_look in line:
            found = True
    assert found, f"not found {msg_to_look} in {str(log[prev_turn])}"


@then('everybody {can_or_can_not} see public card {card} of user {user}')
def step_impl(context, can_or_can_not, user, card):
    global game
    user_n, user = get_user(user)
    log = mock.current_turn_log()
    card_desc = f"{card}-{user.cards[int(card)].value}"
    if can_or_can_not == "can":
        can_or_can_not = True
    elif can_or_can_not == "can not":
        can_or_can_not = False
    for p in game.pl:
        p: CopPlayer
        for msg in log:
            msg: str
            if msg.startswith(f"to {p.id}: Новый ход"):
                cut_details = parse_end_turn_message_get_player_info(msg, user_n)
                if can_or_can_not:
                    assert "Открытые карты" in cut_details, cut_details
                    assert card_desc in cut_details, cut_details
                else:
                    if p.num != user_n:
                        assert card_desc not in cut_details, cut_details


@then('enemy leader is wounded')
def step_impl(context):
    global game, spetial_players
    enemy_leader_n, enemy_leader = get_user("enemy_leader")
    assert enemy_leader.wounded


@then('user {user} is{is_or_is_not}dead')
def step_impl(context, user, is_or_is_not):
    global game, spetial_players
    user_n, user = get_user(user)
    expexded = not ("not" in is_or_is_not)
    assert expexded == user.dead


@then('user {active_user} arms himself but there is no guns left')
def step_impl(context, active_user):
    global game, players, mock, spetial_players
    active_user_n, active_user = get_user(active_user)
    mock.echo(players[active_user_n-1], ARM)
    state_msg, msg = get_last_error()
    #TODO возможно карты уже раскрыты
    assert 'ACTION_SELECT->ACTION_SELECT' in state_msg, state_msg
    assert 'Не осталось ни одного свободного пистолета' in msg, msg
    assert not active_user.gun


@then('user {user} team has won!')
def step_impl(context, user):
    global game, spetial_players
    active_user_n, active_user = get_user(user)
    team = active_user.team()
    team: Roles
    msg = get_last_all_msg()
    if team == Roles.BAD:
        assert 'Плохие копы победили! Комиссар мертв!' in msg
    elif team == Roles.GOOD:
        assert 'Хорошие копы победили! Вор в законе мертв!' in msg
    else:
        assert False, f"team {team} is wrong"


@then('user {user} can not target enemy leader')
def step_impl(context, user):
    global game, spetial_players
    active_user_n, active_user = get_user(user)
    enemy_leader_n, enemy_leader = get_user("enemy_leader")
    state_msg, msg, cmds = get_last_log_result_id_commands(active_user)
    assert len(cmds) > 0
    assert enemy_leader_n not in cmds, f"{active_user.name} can still aim at {enemy_leader.name}"
    mock.echo(players[active_user_n-1], enemy_leader_n)
    state_msg, msg = get_last_error()
    assert 'Нельзя выбрать ту же самую цель' in msg


@then('{user} is a winner')
def step_impl(context, user):
    global game, spetial_players
    user_n, user = get_user(user)
    msg = get_last_all_msg()
    assert f'{user.name} победил!!' in msg


def get_last_log() -> (str, Result):
    global game
    return game.current_turn_state()["logs"][-1]


def check_turn_ends() -> Result:
    state_msg, r = get_last_log()
    assert "END_TURN->ACTION_SELECT" in state_msg or "AIM->ACTION_SELECT" in state_msg


def check_end_game() -> Result:
    state_msg, r = get_last_log()
    assert 'END_GAME' in state_msg


def get_last_error() -> (str, str):
    state_msg, r = get_last_log()
    if r.result:
        assert r.result, "error in result not found:" + str(r)
    if ReplyTo.CALLER not in r.next_actions:
        assert ReplyTo.CALLER in r.next_actions
    msg = r.next_actions[ReplyTo.CALLER].msg
    return state_msg, msg


def get_last_log_result_commands() -> (str, str, list):
    state_msg, r = get_last_log()
    if not r.result:
        assert r.result, "error in result :" + str(r)
    if ReplyTo.CALLER not in r.next_actions:
        assert ReplyTo.CALLER in r.next_actions
    cmd = r.next_actions[ReplyTo.CALLER].commands
    msg = r.next_actions[ReplyTo.CALLER].msg
    return state_msg, msg, flatten_buttons(cmd)


def get_last_log_result_id_commands(user) -> (str, str, list):
    state_msg, r = get_last_log()
    if not r.result:
        assert r.result, "error in result :" + str(r)
    if user.id not in r.next_actions:
        assert user.id in r.next_actions
    cmd = r.next_actions[user.id].commands
    msg = r.next_actions[user.id].msg
    return state_msg, msg, flatten_buttons(cmd)


def get_last_all_msg() -> str:
    state_msg, r = get_last_log()
    if not r.result:
        assert r.result, "error in result :" + str(r)
    if ReplyTo.ALL not in r.next_actions:
        assert ReplyTo.ALL in r.next_actions
    msg = r.next_actions[ReplyTo.ALL].msg
    return msg


def either_action_or_end_turn() -> (bool, tuple):
    state_msg, r = get_last_log()
    if "END_TURN->ACTION_SELECT" in state_msg:
        return True, r
    if not r.result:
        assert r.result, "error in result :" + str(r)
    if ReplyTo.CALLER not in r.next_actions:
        assert ReplyTo.CALLER in r.next_actions
    cmd = r.next_actions[ReplyTo.CALLER].commands
    msg = r.next_actions[ReplyTo.CALLER].msg
    return False, (state_msg, msg, flatten_buttons(cmd))


def parse_end_turn_message_get_player_info(msg: str, player_num) -> str:
    ret = ""
    found = False
    lines = msg.split("\n")
    for line in lines:
        if line.startswith(f"{player_num}:"):
            found = True
        if line.startswith(f"{player_num + 1}:"):
            found = False
        if found:
            ret += line + "\n"
    return ret

def get_user(user: str) -> (int, CopPlayer):
    global game
    if user.isdigit():
        return int(user), game.n[int(user)]
    user = user.replace(" ", "_")
    if user in spetial_players:
        return spetial_players[user], game.n[spetial_players[user]]
    if user == "non-leader":
        for key, p in game.n.items():
            p: CopPlayer
            if not p.check_leader():
                spetial_players["non-leader"] = key
                return key, p
    if user == "active_player":
        return game.current_turn_state()['active_player'], game.n[game.current_turn_state()['active_player']]

