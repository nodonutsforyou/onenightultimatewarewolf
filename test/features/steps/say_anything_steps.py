from behave import *
import pytest
import json
import copy
from collections import namedtuple
from say_anything.say_anything import SayAnythingGame
from contextlib import contextmanager
import statebot
from util import dummy_players, dummy_players_large_list, Result, ReplyTo, flatten_buttons
from test.MockUpdateAndContext import MockUpdateAndContext
from player import Player

game = SayAnythingGame()
mock = MockUpdateAndContext()
players = []
spetial_players = {}
answers_by_player = {}

def reset_all():
    global game, players, mock, spetial_players, answers_by_player
    game = SayAnythingGame()
    game.players_list = []
    mock.turn_callback = game.get_current_turn
    mock.set_game(game)
    mock.log = {}
    spetial_players = {}
    answers_by_player = {}
    statebot.logger.propagate = False


@given('we start a simple opinion game')
def step_impl(context):
    reset_all()
    global game, players
    players = copy.deepcopy(dummy_players)
    for pl in players:
        game.add_player(pl)
    game.init_game(starting_player=1)


@when('user {active_user} picks {question} question')
def step_impl(context, active_user, question):
    global game, players, mock
    active_user_n, active_user = get_user(active_user)
    if question == "any":
        question = 1
    else:
        question = int(question)
    mock.echo(players[active_user_n-1], question)
    state_msg, r = get_last_log()
    assert "QUESTION_SELECT->SUGGEST_ANSWERS" in state_msg, state_msg


@when('everybody sends some answers')
def step_impl(context):
    global game, players, mock, answers_by_player
    active_user_n, active_user = get_user("active_player")
    for p in players:
        if p["id"] != active_user.id:
            answer = f"answer by {p['first_name']} {p['last_name']}"
            answers_by_player[p["id"]] = answer
            mock.echo(p, answer)
            state_msg, r = get_last_log()
            print(state_msg)
            #assert "QUESTION_SELECT->SUGGEST_ANSWERS" in state_msg, state_msg
    mock.echo(players[active_user_n-1], 0)


@when(u'user {user} votes for answer {answer}')
def step_impl(context, user, answer):
    global players, mock
    user_n, user = get_user(user)
    mock.echo(players[user_n-1], answer)


@when(u'all other users except {users} vote for answer {answer}')
def step_impl(context, users, answer):
    global players, mock
    for p in players:
        if str(p["id"]) not in users:
            mock.echo(p, answer)


@then(u'user {user} gets score {score}')
def step_impl(context, user, score):
    global game, players, mock, answers_by_player
    user_n, user = get_user(user)
    line = get_last_message_to_id(user.id)
    assert f"{user.name} - {score} очка" in line


@then(u'user {active_user} can see answers list')
def step_impl(context, active_user):
    global game, players, mock, answers_by_player
    active_user_n, active_user = get_user(active_user)
    line = get_last_message_to_id(active_user.id)
    for id, answer in answers_by_player.items():
        assert answer in line


def get_last_log() -> (str, Result):
    global game
    return game.current_turn_state()["logs"][-1]


def check_turn_ends() -> Result:
    state_msg, r = get_last_log()
    assert "END_TURN->ACTION_SELECT" in state_msg or "AIM->ACTION_SELECT" in state_msg


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

def get_user(user: str) -> (int, Player):
    global game
    if user.isdigit():
        return int(user), game.n[int(user)]
    user = user.replace(" ", "_")
    if user in spetial_players:
        return spetial_players[user], game.n[spetial_players[user]]
    if user == "active_player":
        return game.current_turn_state()['active_player'], game.n[game.current_turn_state()['active_player']]

def get_last_message_to_id(id) -> str:
    i = 0
    while i < len(mock.log):
        logs = mock.log[mock.turn_callback() - i]
        j = 1
        while j <= len(logs):
            line = logs[-j]
            if line.startswith(f"to {id}"):
                return line
            j += 1
        i += 1
    raise Exception("Not found")
