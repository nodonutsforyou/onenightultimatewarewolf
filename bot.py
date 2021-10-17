#!/usr/bin/env python
import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from enum import Enum
import time
import re
import random

from onuwgame import Game

gameObj = Game()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


class State(Enum):
    STOPPED = "STOPPED"
    INIT = "INIT"
    VOTE = "VOTE"


stateFlag = State.STOPPED

timer_countdown = 0
# timeout = 5 * 60
timeout = 10
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
    gameObj.init_game()
    for p in gameObj.human_pl:
        update.message.bot.send_message(p["id"], "Игра начинается")
        update.message.bot.send_message(p["id"], f'Список игроков:\n {gameObj.list_of_players_by_number()}')
        update.message.bot.send_message(p["id"], gameObj.get_init_message(p))
    stateFlag = State.INIT
    if gameObj.check_actions_cast():
        #пауза на случай если все игроки мирные или оборотни
        logger.info("All players have no actions pause")
        time.sleep(random.randint(3, 15))
    action_phase(update, context)


def stop(update: Update, context: CallbackContext) -> None:
    logger.info("Game Interupted")
    global stateFlag
    initiator = update.effective_user
    initiator_name = str(initiator['first_name']) + ' ' + str(initiator['last_name'])
    if stateFlag != State.STOPPED:
        for p in gameObj.human_pl:
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
    context.bot.send_message(context.job.context,  "Список на голосование:\n" + voting_list)


def kill_alarms(context: CallbackContext) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(ALARM_JOB_ID)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def action_phase(update: Update, context: CallbackContext):
    global stateFlag
    if gameObj.check_actions_cast():
        gameObj.implement_actions()
        stateFlag = State.VOTE
        voting_list = gameObj.list_of_human_players_by_number_for_voting(True)
        for p in gameObj.human_pl:
            if len(p["msg"]) > 0:
                update.message.bot.send_message(p["id"], p["msg"])
            update.message.bot.send_message(p["id"], "Все действия совершены. Можно начинать обсуждение!")
            update.message.bot.send_message(p["id"], "Список на голосование:\n" + voting_list)
            context.job_queue.run_once(alarm5, timeout, context=p["id"], name=ALARM_JOB_ID)
            context.job_queue.run_once(alarm10, 2*timeout, context=p["id"], name=ALARM_JOB_ID)
            context.job_queue.run_once(alarm15, 3*timeout, context=p["id"], name=ALARM_JOB_ID)
        logger.info("Vote Phase")


def vote_phase(update: Update, context: CallbackContext):
    global stateFlag
    if gameObj.check_votes_cast():
        stateFlag = State.STOPPED
        kill_alarms(context)
        result, msg = gameObj.implement_votes()
        for p in gameObj.human_pl:
            update.message.bot.send_message(p["id"], msg)
            personal_result, msg_per = gameObj.get_personal_result(result, p["id"])
            update.message.bot.send_message(p["id"], msg_per)
        logger.info("Game Ended")
        logger.info(gameObj.get_history())


def echo(update: Update, context: CallbackContext) -> None:
    logger.info(f"{str(update.effective_user)}, {update.message.text}")
    global stateFlag
    num = int(re.search(r"/?([0-9]+)", update.message.text).group(1))
    if stateFlag == State.STOPPED:
        return
    if stateFlag == State.INIT:
        res, msg = gameObj.action(update.effective_user, num)
        update.message.reply_text(msg)
        action_phase(update, context)
        return
    if stateFlag == State.VOTE:
        gameObj.vote(update.effective_user, num)
        vote_phase(update, context)
        return
    #update.message.reply_text(update.message.text)


def main() -> None:
    with open('secret.token', 'r') as file:
        token = file.read()
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
    for i in range(0, 20):
        dispatcher.add_handler(CommandHandler(str(i), echo))

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