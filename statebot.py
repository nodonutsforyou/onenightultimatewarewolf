#!/usr/bin/env python
import logging

from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from enum import Enum
import time
import re
import random
import os
import copy
import json
from goodcopbadcop.goodcopbadcop import CopGame
from util import *

from secrethitler import Game, Actions, Roles

class Games(Enum):
    ONE_NIGHT_ULTIMATE_WEREWOLF = "ONE_NIGHT_ULTIMATE_WEREWOLF"
    SECRET_HITLER = "SECRET_HITLER"
    GOOD_COP_BAD_COP = "GOOD_COP_BAD_COP"

games = {
    Games.GOOD_COP_BAD_COP: CopGame(),
    Games.SECRET_HITLER: CopGame(),
    Games.ONE_NIGHT_ULTIMATE_WEREWOLF: CopGame(),
}
activeGame = games[Games.GOOD_COP_BAD_COP]

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

ALARM_JOB_ID = "countdown_for_voting"

ADMIN_LIST = [131733634]

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    logger.info(str(user))
    for k, game in games.items():
        game.add_player(user)
    logger.info(str(activeGame.get_list_of_players()))
    commands_user = [("start", "start")]
    commands_admin = [("start", "start"), ("game", "game")]
    if user['id'] in ADMIN_LIST:
        context.bot.set_my_commands(commands_admin)
    else:
        context.bot.set_my_commands(commands_user)
    update.message.reply_markdown_v2(
        f"Hi {user.mention_markdown_v2()}\\!\nWe have those players joined:\n{activeGame.get_list_of_players()}"
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
    if activeGame.get_num_of_players() == 0:
        update.message.reply_text("Ни одного игрока не присоединилось /join чтобы присоединиться")
        update.message.reply_text("/help чтобы посмотреть подсказку")
        return
    action = activeGame.init_game()
    #TODO if result false? or game end?
    for p in activeGame.pl:
        update.message.bot.send_message(p.id, activeGame.get_init_message(p))
    kill_alarms(context)
    do_action(action, update=update, context=context)


def stop(update: Update, context: CallbackContext) -> None:
    logger.info("Game Interupted")
    global stateFlag
    initiator = update.effective_user
    initiator_name = str(initiator['first_name']) + ' ' + str(initiator['last_name'])
    if activeGame.state != None:
        for p in activeGame.pl:
            update.message.bot.send_message(p.id, "Игра прервана " + initiator_name)
    else:
        update.message.reply_text("Игра не найдена")
    activeGame.state = None
    kill_alarms(context)


def remove(update: Update, context: CallbackContext) -> None:
    #TODO remove player
    pass


def kill_alarms(context: CallbackContext) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(ALARM_JOB_ID)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def do_action(action: Result, update: Update, context: CallbackContext, caller_id=None):
    for key, message in action.next_actions.items():
        message: Message
        logger.info(str(message.expected_action) + message.msg)
        if key == ReplyTo.ALL:
            for p in activeGame.pl:
                context.bot.send_message(p.id, message.msg, reply_markup=reply_keyboard_markup(message.commands), parse_mode=ParseMode.MARKDOWN)
        elif key == ReplyTo.ALL_OTHERS:
            for p in activeGame.pl:
                if caller_id is None or p.id != caller_id:
                    context.bot.send_message(p.id, message.msg, reply_markup=reply_keyboard_markup(message.commands), parse_mode=ParseMode.MARKDOWN)
        elif key == ReplyTo.CALLER:
            for p in activeGame.pl:
                if caller_id is not None and p.id == caller_id:
                    context.bot.send_message(p.id, message.msg, reply_markup=reply_keyboard_markup(message.commands), parse_mode=ParseMode.MARKDOWN)
        else:
            if not isinstance(key, list):
                key = [key]
            for id in key:
                context.bot.send_message(id, message.msg, reply_markup=reply_keyboard_markup(message.commands), parse_mode=ParseMode.MARKDOWN)


def next_step(update: Update, context: CallbackContext):
    if activeGame.check_next_step():
        r = activeGame.do_next_step()
        if r.game_end:
            return endgame(r, update, context)
        do_action(r, update, context)


def endgame(action: Result, update: Update, context: CallbackContext):
    do_action(action)
    activeGame.state = None
    # logging.info(game_state_logger(activeGame.n))
    logging.info(game_state_logger(activeGame.game_state))


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
                s += f"\t{key}:\n"
                for i in value:
                    s += f"\t\t{str(i)},\n"
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
            # text, command = t
            try:
                text, command = t
            except Exception as e:
                print(str(e))
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
    r = activeGame.do_action(update.effective_user, num)
    if r is not None:
        do_action(r, update, context, caller_id=update.effective_user.id)
        next_step(update, context)


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

    updater.bot.set_my_commands([("start", "start")])
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
