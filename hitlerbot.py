#!/usr/bin/env python
import logging

from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from enum import Enum
import time
import re
import random
import os
import copy
import json

from secrethitler import Game, Actions, Roles

gameObj = Game()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


class State(Enum):
    STOPPED = "STOPPED"
    INIT = "INIT"
    PRESIDENT = "PRESIDENT"
    VOTE = "VOTE"
    LEGISLATURE_C = "LEGISLATURE_C"
    LEGISLATURE_P = "LEGISLATURE_P"
    VETO = "VETO"
    IMPLEMENTATION = "IMPLEMENTATION"
    NEW_TURN = "NEW_TURN"


stateFlag = State.STOPPED

timer_countdown = 0
timeout = 5 * 60
# timeout = 10
timer_msg = {
    0: "Прошло 5 минут",
    1: "Прошло 10 минут",
    2: "Прошло 15 минут. Пора голосовать!",
}
ALARM_JOB_ID = "countdown_for_voting"


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    logger.info(str(user))
    gameObj.add_player(user)
    logger.info(str(gameObj.get_list_of_players()))
    context.bot.set_my_commands([("start", "start")])
    update.message.reply_markdown_v2(
        f"Hi {user.mention_markdown_v2()}\\!\nWe have those players joined:\n{gameObj.get_list_of_players()}"
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(" /start или /join чтобы добавиться и посмотреть список людей")
    update.message.reply_text(" /help посмотреть эту подсказку")
    update.message.reply_text(" /game чтобы начать игру")
    update.message.reply_text(" /stop чтобы остановить игру")
    # update.message.reply_text(" /remove чтобы убрать другого игрока из игры")


def game(update: Update, context: CallbackContext) -> None:
    logger.info("Game Start")
    global stateFlag
    if gameObj.get_num_of_players() == 0:
        update.message.reply_text("Ни одного игрока не присоединилось /join чтобы присоединиться")
        update.message.reply_text("/help чтобы посмотреть подсказку")
        return
    stateFlag = State.INIT
    gameObj.init_game()
    for p in gameObj.pl:
        update.message.bot.send_message(p["id"], "Игра начинается")
        update.message.bot.send_message(p["id"], f'Список игроков:\n{gameObj.list_of_players_by_number()}')
        update.message.bot.send_message(p["id"], gameObj.get_init_message(p))
    kill_alarms(context)
    stateFlag = State.PRESIDENT
    president_phase(update, context)


def stop(update: Update, context: CallbackContext) -> None:
    logger.info("Game Interupted")
    global stateFlag
    initiator = update.effective_user
    initiator_name = str(initiator['first_name']) + ' ' + str(initiator['last_name'])
    if stateFlag != State.STOPPED:
        for p in gameObj.pl:
            update.message.bot.send_message(p["id"], "Игра прервана " + initiator_name)
    else:
        update.message.reply_text("Игра не найдена")
    stateFlag = State.STOPPED
    kill_alarms(context)


def remove(update: Update, context: CallbackContext) -> None:
    pass


def alarm5(context: CallbackContext) -> None:
    context.bot.send_message(context.job.context, timer_msg[0])


def alarm10(context: CallbackContext) -> None:
    context.bot.send_message(context.job.context, timer_msg[1])


def alarm15(context: CallbackContext) -> None:
    context.bot.send_message(context.job.context, timer_msg[2])
    voting_list = gameObj.list_of_human_players_by_number_for_voting(True)
    voting_reply_markup = reply_keyboard_markup(gameObj.get_buttons_list(tables=False, vote_all_str="Никого не убивать"))
    context.bot.send_message(context.job.context,  "Список на голосование:\n" + voting_list, reply_markup=voting_reply_markup)


def kill_alarms(context: CallbackContext) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(ALARM_JOB_ID)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def president_phase(update: Update, context: CallbackContext):
    global stateFlag
    president_n = gameObj.curent_turn_state()["president"]
    president = gameObj.n[president_n]
    list = gameObj.get_chancellor_candidates_list()
    if len(list) == 0:
        for p in gameObj.pl:
            context.bot.send_message(p["id"], "Нет ни одной подходящей кандидатуры на роль канцлера!")
            gameObj.curent_turn_state()["chaos_score"] += 1
            if gameObj.curent_turn_state()["chaos_score"] > 2:
                gameObj.chaos_popup_law()
            stateFlag = State.IMPLEMENTATION
            action_phase(update, context)
            return
    for p in gameObj.pl:
        if p["num"] == president_n:
            chancellor_candidates_markup = reply_keyboard_markup(list)
            context.bot.send_message(p["id"], "Вы назначены президентом в этом ходу!\nВыберите себе канцлера:", reply_markup=chancellor_candidates_markup)
        else:
            context.bot.send_message(p["id"], f"{president['name']} назначен президентом в этом ходу!\n{president['name']} Выбирает себе канцлера")
    logger.info("president Phase")

def pick_chancellor(update: Update, context: CallbackContext):
    global stateFlag
    stateFlag = State.VOTE
    president_n = gameObj.curent_turn_state()["president"]
    president = gameObj.n[president_n]
    chancellor_n = gameObj.curent_turn_state()["chancellor_candidate"]
    chancellor = gameObj.n[chancellor_n]
    vote_markup = reply_keyboard_markup([[("Ja", 1),("Nein", 0)]])
    warnings = ""
    if gameObj.check_hitler_chancellorship_wins_the_game():
        warnings += "* Если кандидат окажется *Гитлером*, то либералы проиграют игру\n"
    if gameObj.check_next_fas_law_wins_the_game():
        warnings += "* Если президент вместе с канслером примут фашистский закон, то либералы проиграют игру\n"
    if gameObj.check_chaos_score():
        warnings += f"* Если парлмент откажет {chancellor['name']}, то {president['name']} примет следующий закон автоматически\n"
    if gameObj.check_chaos_score():
        warnings += f"* Если парлмент откажет {chancellor['name']}, то {president['name']} примет следующий закон автоматически\n"
    next_action = gameObj.desribe_next_action()
    if next_action is not None:
        warnings += next_action + "\n"
    for p in gameObj.pl:
        if p["num"] == president_n:
            context.bot.send_message(p["id"], f"Вы выбрали {chancellor['name']} кандидатом в канцлеры в этом ходу\n{warnings}Утвердить?", reply_markup=vote_markup)
        elif p["num"] == chancellor_n:
            context.bot.send_message(p["id"], f"Президент {president['name']} выбрал Вас, {chancellor['name']}, кандидатом в канцлеры в этом ходу\n{warnings}Утвердить?", reply_markup=vote_markup)
        else:
            if not p["dead"]:
                context.bot.send_message(p["id"], f"Президент {president['name']} выбрал {chancellor['name']} кандидатом в канцлеры в этом ходу\n{warnings}Утвердить?", reply_markup=vote_markup)
            else:
                context.bot.send_message(p["id"], f"Президент {president['name']} выбрал {chancellor['name']} кандидатом в канцлеры в этом ходу")
            #TODO предупреждения о правилах
    logger.info("president Phase")

def action_phase(update: Update, context: CallbackContext):
    global stateFlag
    if gameObj.curent_turn_state()["veto"]:
        stateFlag = State.VETO
        president_n = gameObj.curent_turn_state()["president"]
        president = gameObj.n[president_n]
        chancellor_n = gameObj.curent_turn_state()["chancellor_candidate"]
        chancellor = gameObj.n[chancellor_n]
        vote_markup = reply_keyboard_markup([("Ja", 1),("Nein", 0)])
        for p in gameObj.pl:
            if p["num"] == chancellor_n:
                context.bot.send_message(p["id"], f"Президент {president['name']} предложил наложить вето на все законы\nПоддержать?", reply_markup=vote_markup)
    if gameObj.check_legislation_done():
        stateFlag = State.IMPLEMENTATION
        res, msg = gameObj.implement_action()
        for p in gameObj.pl:
            if not msg is None and len(msg) > 0:
                context.bot.send_message(p["id"], msg)
        if res:
            new_turn(update, context)
            return
        logger.info("Action Phase")
        president_n = gameObj.curent_turn_state()["president"]
        president = gameObj.n[president_n]
        action = gameObj.select_action()
        actions_markup = reply_keyboard_markup(gameObj.get_buttons_list(exclude_id=president["id"]))
        actions_markup_dead_exluded = reply_keyboard_markup(gameObj.get_buttons_list(exclude_id=president["id"], exclude_dead=True))
        for p in gameObj.pl:
            if p["num"] == president_n:
                if action == Actions.INVESTIGATE:
                    context.bot.send_message(p["id"], "Выберите игрока на проверку", reply_markup=actions_markup)
                    return
                if action == Actions.ELECTION:
                    context.bot.send_message(p["id"], "Выберите следующего президента", reply_markup=actions_markup_dead_exluded)
                    return
                if action == Actions.EXECUTION:
                    context.bot.send_message(p["id"], "Выберите игрока на растрел", reply_markup=actions_markup_dead_exluded)
                    return
                if action == Actions.PEEK:
                    laws = gameObj.view_laws(3)
                    s = ""
                    for l in laws:
                        s += l["description"] + "\n"
                    context.bot.send_message(p["id"], f"Следующие 3 закона в колоде: \n{s}")
                    new_turn(update, context)
                    return


def action_implementation_phase(update: Update, context: CallbackContext):
    global stateFlag
    if gameObj.check_legislation_done():
        stateFlag = State.IMPLEMENTATION
        res, msg = gameObj.implement_action()
        for p in gameObj.pl:
            if not msg is None and len(msg) > 0:
                context.bot.send_message(p["id"], msg)
        if res:
            new_turn(update, context)
            return


def decorate_laws_list(laws, veto=False):
    list = []
    i = 0
    for l in laws:
        item = [(str(l["description"]), i)]
        i += 1
        list.append(item)
    if veto:
        item = [("Предолжить наложить вето", -1)]
        list.append(item)
    return reply_keyboard_markup(list)


def vote_phase(update: Update, context: CallbackContext):
    global stateFlag
    if gameObj.check_votes_cast():
        r, msg = gameObj.implement_votes()
        for p in gameObj.pl:
            context.bot.send_message(p["id"], msg)
        if r is None:
            endgame_phase(update, context, msg)
            return
        if r:
            stateFlag = State.LEGISLATURE_C
            president_n = gameObj.curent_turn_state()["president"]
            president = gameObj.n[president_n]
            chancellor_n = gameObj.curent_turn_state()["chancellor"]
            chancellor = gameObj.n[chancellor_n]
            decoration = decorate_laws_list(gameObj.curent_turn_state()["laws_big_list"])
            for p in gameObj.pl:
                if p["num"] == chancellor_n:
                    context.bot.send_message(p["id"], "Вас выбрали Канцлером!\nСписок законов на увержедние (вы можете отклонить один из них):", reply_markup=decoration)
        else:
            stateFlag = State.IMPLEMENTATION
            action_phase(update, context)


def legislature_president_phase(update: Update, context: CallbackContext):
    global stateFlag
    if gameObj.check_president_legislation_is_ready():
        stateFlag = State.LEGISLATURE_P
        president_n = gameObj.curent_turn_state()["president"]
        president = gameObj.n[president_n]
        laws = copy.deepcopy(gameObj.curent_turn_state()["laws_short_list"])
        decoration = decorate_laws_list(laws, gameObj.check_veto_option())
        for p in gameObj.pl:
            if p["num"] == president_n:
                context.bot.send_message(p["id"], "Выберите закон для принятия:", reply_markup=decoration)


def implement_veto(update: Update, context: CallbackContext):
    global stateFlag
    done, impl, msg = gameObj.implement_veto()
    if done:
        stateFlag = State.LEGISLATURE_P
        president_n = gameObj.curent_turn_state()["president"]
        president = gameObj.n[president_n]
        chancellor_n = gameObj.curent_turn_state()["chancellor"]
        chancellor = gameObj.n[chancellor_n]
        if impl:
            stateFlag = State.IMPLEMENTATION
            for p in gameObj.pl:
                if p["num"] == president_n or p["num"] == chancellor_n:
                    context.bot.send_message(p["id"], msg)
            action_phase(update, context)
            return True
        else:
            stateFlag = State.LEGISLATURE_P
            legislature_president_phase(update, context)


def new_turn(update: Update, context: CallbackContext):
    global stateFlag
    status = gameObj.check_victory()
    if status:
        endgame_phase(update, context)
        return
    if not gameObj.status is None:
        cont, win, msg = gameObj.status
        for p in gameObj.pl:
            context.bot.send_message(p["id"], f"Ход завершен\n{msg}\nЖивые игроки:\n{gameObj.list_of_alive_players_by_number()}")
    stateFlag = State.NEW_TURN
    gameObj.new_turn()
    stateFlag = State.PRESIDENT
    president_phase(update, context)


def endgame_phase(update: Update, context: CallbackContext, msg=None):
    global stateFlag
    stateFlag = State.STOPPED
    cont, win, msg = gameObj.status
    if not gameObj.status is None:
        for p in gameObj.pl:
            context.bot.send_message(p["id"], f"Игра завершена\n{msg}\n{gameObj.get_fashists_list()}")
    logging.info(game_state_logger(gameObj.n))
    logging.info(game_state_logger(gameObj.game_state))

def game_state_logger(game_state):
    s = ""
    for turn, state in game_state.items():
        s += f"turn {turn}:\n"
        for key, value in state.items():
            if isinstance(value, dict):
                s += f"\t{key}:\n"
                for kk, vv in value.items():
                    s += f"\t\t{kk}:{str(vv)}\n"
            if isinstance(value, list):
                s += f"\t{key}:\n\t\t"
                for i in value:
                    s += f"{str(i)},"
                s += f"\n"
            else:
                s += f"\t{key}:{str(value)}\n"
    return s


def reply_keyboard_markup(buttons_list):
    if buttons_list is None:
        return None
    keyboard_list = []
    for row in buttons_list:
        krow = []
        for t in row:
            text, command = t
            krow.append(InlineKeyboardButton(text, callback_data=command))
        if len(krow) > 0:
            keyboard_list.append(krow)
    return InlineKeyboardMarkup(keyboard_list)


def echo(update: Update, context: CallbackContext) -> None:
    value = str(update.callback_query)
    if hasattr(update.callback_query, "data"):
        value = update.callback_query.data
    logger.info(f"{str(update.effective_user)}, {value}")
    query = update.callback_query
    global stateFlag
    num = None
    if str(update.callback_query.data) == "OK":
        num = "OK"
    else:
        num = int(re.search(r"/?([0-9]+)", update.callback_query.data).group(1))
    query.answer()
    if stateFlag == State.STOPPED:
        return
    if stateFlag == State.INIT:
        return
    if stateFlag == State.PRESIDENT:
        res, msg = gameObj.pick_chancellor(update.effective_user, num)
        if res:
            pick_chancellor(update, context)
        else:
            query.message.reply_text(msg)
        return
    if stateFlag == State.VOTE:
        result, msg = gameObj.vote(update.effective_user, num)
        if result:
            if msg is not None:
                query.message.reply_text(msg)
        elif not result:
            query.message.reply_text("ошибка: " + msg)
        vote_phase(update, context)
        return
    if stateFlag == State.LEGISLATURE_C:
        result, msg = gameObj.legislation(update.effective_user, num)
        if result:
            if msg is not None:
                query.message.reply_text(msg)
        elif not result:
            query.message.reply_text("ошибка: " + msg)
        legislature_president_phase(update, context)
        return
    if stateFlag == State.LEGISLATURE_P:
        result, msg = gameObj.legislation(update.effective_user, num)
        if result:
            if msg is not None:
                query.message.reply_text(msg)
        elif not result:
            query.message.reply_text("ошибка: " + msg)
        action_phase(update, context)
        return
    if stateFlag == State.IMPLEMENTATION:
        result, msg, msg_all = gameObj.action(update.effective_user, num)
        if result:
            if msg is not None:
                query.message.reply_text(msg)
        elif not result:
            query.message.reply_text("ошибка: " + msg)
        if msg_all is not None:
            for p in gameObj.pl:
                if update.effective_user.id !=p["id"]:
                    context.bot.send_message(p["id"], msg_all)
        action_implementation_phase(update, context)
        return
    if stateFlag == State.VETO:
        result, msg = gameObj.veto(update.effective_user, num)
        if result:
            if msg is not None:
                query.message.reply_text(msg)
        elif not result:
            query.message.reply_text("ошибка: " + msg)
        implement_veto(update, context)
        return
    #update.message.reply_text(update.message.text)


def main() -> None:
    token = os.environ["SECRET_TOKEN"]
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("join", start))
    dispatcher.add_handler(CommandHandler("stop", stop))
    # dispatcher.add_handler(CommandHandler("remove", remove))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("game", game))

    dispatcher.add_handler(CallbackQueryHandler(echo))
    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()