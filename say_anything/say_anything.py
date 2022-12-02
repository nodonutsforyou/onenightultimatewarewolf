import logging
import random
import json
import copy
from enum import Enum
from datetime import datetime
from player import Player
from game import Game
from util import *

random.seed(datetime.now())


class State(Enum):
    INIT = "INIT"
    QUESTION_SELECT = "QUESTION_SELECT"
    SUGGEST_ANSWERS = "SUGGEST_ANSWERS"
    REMOVE_DUBLICATES = "REMOVE_DUBLICATES"
    VOTE = "VOTE"
    ENDTURN = "VETO"


QUESTIONS = {
    "funny": [
        "Самое плохое в жизни мужчины?",
        "Самое плохое в жизни женшины?",
        "Самой лучший свадебный падарок?",
        "На землю прилетели инопланетяне. Что нам делать?",
        "Самая глупая вещь, которую можно сказать на интервью?",
        "Самая глупая вещь, которую можно сказать на первом свидании?",
        "Самая глупая вещь, которую можно сказать когда тебя остановила полиция?",
        "Самая глупая вещь, которую можно сделать на Красной Площади?",
        "Что сделать первым делом при перезде?",
        "Самый лучший рингтон на телефон?",
        "Самая забавная надпись на стене в туалете?",
    ],
    "serious": [
        "Что бы я хотел бы в падарок на следующий день рождения?",
        "Что нужна написать на моей магиле?",
        "Какая технологию еще не изобрели, но тебе хотелось бы чтобы она появилась?",
        "В каое время бы я отправился на день в машине времени?",
        "Из какого знаменитости получится самый лучший президент (настоящий)?",
        "Из какой знаменитости получится наихудший президент?",
        "Что я буду делать на пенсии?",
        "Что больше всего бесит меня в людях?",
        "Самая бесполезная в хозяйстве вещь?",
    ],
    "personal": [
        "Какой самый лучший способ убить время в субботу вечером?",
        "Лучший ден в моей жизни?",
        "Каким киноперсонажем я хотел бы стать?",
        "Если бы я выиграл подарочный сертификат на 1000$ в один магазин, куда бы я его потратил бы?",
        "Самое крутое экзотическое домашнее животное?",
    ],
    "trivia": [
        "Какая музыкальная группа сильно переоцененна?",
        "Лучшая музыкальная группа за все времена?",
        "Самая переоциненная комедия?",
        "Самый лучшей фильм-сиквел?",
        "Лучшая песня за последние 10 лет?",
        "Лучшая песня из прошлого века?",
        "Какая знаменитость была бы лучшим напарником на необитаемом острове?",
    ],
}

DUBLICATE_CHECK_BUTTONS = [[("✅ нет повторов", 0), ("❌ указать повторы", -1)]]


class SayAnythingGame(Game):
    questions_list = {}
    dublicate_one = None

    # Abstract methods redef
    def get_init_message(self, p):
        return "Игра 'По моему мнению...' начинается!"

    def do_next_step(self, unstack=False) -> Result:
        if self.check_next_step():
            s_state = self.state
            r = self._do_next_step()
            e_state = self.state
            if e_state is None:
                e_state = "None"
            else:
                e_state = e_state.value
            self.current_turn_state()["logs"].append((f"next_action state {s_state.value}->{e_state}", r))
            return r
        return Result()

    def check_next_step(self) -> bool:
        if self.state == State.INIT:
            return False
        elif self.state == State.QUESTION_SELECT:
            return self.current_turn_state()['question'] is not None
        elif self.state == State.SUGGEST_ANSWERS:
            if 'answers' not in self.current_turn_state():
                return False
            for key, answer in self.current_turn_state()['answers'].items():
                if len(answer) == 0:
                    return False
            return True
        elif self.state == State.REMOVE_DUBLICATES:
            return False
        elif self.state == State.VOTE:
            if self.current_turn_state()['correct_answer'] <= 0:
                return False
            for key, answer in self.current_turn_state()['votes'].items():
                if len(answer) < 2:
                    return False
            return True
        elif self.state == State.ENDTURN:
            return True
        if self.state is None:
            return None
        raise Exception(f"not yet implemented - {self.state}")

    def _do_action(self, user, action) -> Result:
        if self.state == State.INIT:
            return None
        elif self.state == State.QUESTION_SELECT:
            return self.pick_question(user, action)
        elif self.state == State.SUGGEST_ANSWERS:
            return self.accept_answer(user, action)
        elif self.state == State.REMOVE_DUBLICATES:
            return self.remove_dublicates(user, action)
        elif self.state == State.VOTE:
            return self.vote(user, action)
        elif self.state == State.ENDTURN:
            return None
        if self.state is None:
            return None
        raise Exception(f"not yet implemented - {self.state}")

    def _do_next_step(self) -> Result:
        #if self.state == State.INIT:
        #elif self.state == State.QUESTION_SELECT:
        if self.state == State.SUGGEST_ANSWERS:
            return self.send_answers_for_check()
        elif self.state == State.VOTE:
            return self.results()
        elif self.state == State.ENDTURN:
            return self.new_turn()
        if self.state is None:
            return None
        raise Exception(f"not yet implemented - {self.state}")

    def shuffle_questions(self):
        questions_list = copy.deepcopy(QUESTIONS)
        for key, list in questions_list.items():
            random.shuffle(list)
        logging.info("Roles are " + str(questions_list))
        return questions_list

    # GAME PART
    def init_game(self, roles=None, laws=None, starting_player=None):
        super().init_game()
        self.state = State.INIT
        self.dublicate_one = None

        for p in self.pl:
            p.score = 0

        self.questions_list = self.shuffle_questions()

        return self.new_turn(starting_player)

    def pick_next_active_player(self, starting_player=None):
        if self.current_turn == 0:
            if starting_player is None:
                return random.randint(1, len(self.pl))
            return starting_player
        active_player = self.current_turn_state()["active_player"]
        active_player += 1
        if active_player > len(self.n):
            active_player = 1
        return active_player

    def new_turn(self, starting_player=None):
        active_player_n = self.pick_next_active_player(starting_player)
        self.current_turn += 1
        turn_obj = {
            "active_player": active_player_n,
            "votes": self.prefilled_dict([]),
            "correct_answer": 0,
            "questions": {},
            "question": None,
            "dublicates": False,
            "answers": self.prefilled_dict(""),
            "answers_authors": {},
            "logs": [],
        }
        self.game_state[self.current_turn] = turn_obj
        active_player = self.get_current_active_player()
        i = 1
        for key, list in self.questions_list.items():
            q = list.pop()
            self.current_turn_state()['questions'][i] = q
            list.insert(0, q)
            i += 1
        r = Result()
        msg, commands = self.get_questions_message_and_buttons(self.current_turn_state()['questions'])
        r.msg_to_id(active_player.id, msg, commands)
        del self.current_turn_state()['answers'][active_player_n]
        del self.current_turn_state()['votes'][active_player_n]
        self.state = State.QUESTION_SELECT
        return r

    def get_questions_message_and_buttons(self, questions: dict) -> (str, list):
        msg = "Вы ведущий в этом ходу!\nВыберите вопрос на этот раунд:\n"
        buttons = []
        for key, value in questions.items():
            text = f"{key}: {value}"
            msg += text + "\n"
            button = [(msg, key)]
            buttons.append(button)
        return msg, buttons

    def get_answers_message_and_buttons(self) -> (str, list):
        answers = self.current_turn_state()['answers']
        msg = ""
        buttons = []
        for key, value in answers.items():
            text = f"{key}: {value}"
            msg += text + "\n"
            button = [(msg, key)]
            buttons.append(button)
        return msg, buttons

    def pick_question(self, user, action):
        questions = self.current_turn_state()['questions']
        r = Game.check_input_values(action, 1, len(questions))
        if r is not None:
            return r
        active_player = self.get_current_active_player()
        if user['id'] != active_player.id:
            return Result.error(f'{str(user)} сейчас не ходит!')
        question = questions[action]
        self.current_turn_state()['question'] = question
        msg = f"Ходит {active_player.name}\nПредложите ответ на вопрос, как по мнению {active_player.name}:"
        r = Result.action(f"Принято {question}")
        r.notify_all_others(msg, State.SUGGEST_ANSWERS)
        self.state = State.SUGGEST_ANSWERS
        return r

    def vote(self, user, action):
        answers = self.current_turn_state()['answers']
        r = Game.check_input_values(action, 1, len(answers))
        if r is not None:
            return r
        active_player = self.get_current_active_player()
        if action not in answers:
            return Result.error(f"Нет ответа {action}")
        if user['id'] == active_player.id:
            self.current_turn_state()['correct_answer'] = action
            return Result.action(f"принято {self.current_turn_state()['correct_answer']}")
        player = self.get_player_by_id(user['id'])
        if player is None:
            return Result.error(f'Вы не участвуете в игре!')
        self.current_turn_state()['votes'][player.num].append(action)
        while len(self.current_turn_state()['votes'][player.num]) > 2:
            del self.current_turn_state()['votes'][player.num][0]
        msg = f"{self.current_turn_state()['votes'][player.num][0]}"
        if len(self.current_turn_state()['votes'][player.num]) == 2:
            if self.current_turn_state()['votes'][player.num][0] == self.current_turn_state()['votes'][player.num][1]:
                msg = f"двойная ставка на {self.current_turn_state()['votes'][player.num][0]}"
            else:
                msg = f"{self.current_turn_state()['votes'][player.num][0]} и {self.current_turn_state()['votes'][player.num][1]}"
        return Result.action(f"Принято {msg}")

    def remove_dublicates(self, user, action):
        answers = self.current_turn_state()['answers']
        r = Game.check_input_values(action, -1, len(answers))
        if r is not None:
            return r
        active_player = self.get_current_active_player()
        if user['id'] != active_player.id:
            return Result.error(f'{str(user)} сейчас не ходит!')
        if action == 0:
            return self.vote_options()
        if action < 0:
            msg, buttons = self.get_answers_message_and_buttons()
            return Result.action(f"Выберите один из повторов:\n{msg}", State.REMOVE_DUBLICATES, buttons.extend(DUBLICATE_CHECK_BUTTONS))
        if self.dublicate_one is None:
            self.dublicate_one = action
        dublicate_two = action
        # join answers
        del answers[dublicate_two]
        self.current_turn_state()['answers_authors'][self.dublicate_one].extend(self.current_turn_state()['answers_authors'][dublicate_two])
        del self.current_turn_state()['answers_authors'][dublicate_two]
        msg, buttons = self.get_answers_message_and_buttons()
        return Result.action(f"Выберите следующий из повтор:\n{msg}", State.REMOVE_DUBLICATES, buttons.extend(DUBLICATE_CHECK_BUTTONS))

    def accept_answer(self, user, action):
        player = self.get_player_by_id(user['id'])
        if player is None:
            return Result.error(f'Вы не участвуете в игре!')
        active_player = self.get_current_active_player()
        if user['id'] == active_player.id:
            return Result.error(f'Подождите, пока остальный игроки ответят на ваш вопрос!')
        self.current_turn_state()['answers'][player.num] = action
        self.current_turn_state()['answers_authors'][player.num] = [player.num]
        return Result.action(f"Принято \"{action}\"")

    def send_answers_for_check(self) -> Result:
        msg, buttons = self.get_answers_message_and_buttons()
        r = Result()
        r.msg_to_id(self.get_current_active_player().id, f"Пришли все ответы!\nВам необходимо проверить ответы на повторый:\n{msg}\nОтветы разные?", State.REMOVE_DUBLICATES, DUBLICATE_CHECK_BUTTONS)
        self.current_turn_state()['answers_first_draft'] = self.current_turn_state()['answers']
        self.state = State.REMOVE_DUBLICATES
        return r

    def vote_options(self) -> Result:
        msg, buttons = self.get_answers_message_and_buttons()
        active_player = self.get_current_active_player()
        question = self.current_turn_state()['question']
        reply_msg = f"Пришло время голосования!\nКакой по мнению {active_player.name} будет ответ на вопрос:\n*{question}*\nУ игроков два голоса. Выбор одного правильного ответа дважды даст 3 очка"
        self.state = State.VOTE
        return Result.notify_all(reply_msg, State.VOTE, buttons)

    def results(self):
        msg_correct = ""
        msg_twice_correct = ""
        active_player = self.get_current_active_player()
        votes = self.current_turn_state()['votes']
        correct_answer = self.current_turn_state()['correct_answer']
        answers = self.current_turn_state()['answers']
        for key, p in self.n.items():
            p: Player
            if p.num != active_player.num:
                r = votes[p.num].count(correct_answer)
                if r == 2:
                    msg_twice_correct += f"{p.name} "
                    p.score += 3
                if r == 1:
                    msg_correct += f"{p.name} "
                    p.score += 1
        msg = f"Правильный ответ:{answers[correct_answer]}\n"
        if len(msg_correct) == 0 and len(msg_twice_correct) == 0:
            msg += "Никто не отгадал!"
        else:
            if len(msg_correct) != 0:
                msg += f"*{msg_correct}* отгадали и получили по 1 очку!\n"
            if len(msg_twice_correct) != 0:
                msg += f"*{msg_twice_correct}* отгадали дважды и получили по 3 очка!\n"
        msg += f"\nCумма очков за игру:\n{self.total_scores()}"
        self.state = State.ENDTURN
        return Result.notify_all(msg)

    def total_scores(self) -> str:
        msg = ""
        for key, p in self.n.items():
            msg += f"{key}: {p.name} - {p.score} очка\n"
        return msg

    def get_current_active_player(self) -> Player:
        return self.n[self.current_turn_state()['active_player']]
