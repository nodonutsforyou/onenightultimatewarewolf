import statebot


class MockUpdateAndContext:
    callback_query = None
    effective_user = None
    bot = None
    data = ""
    id = None

    turn_callback = None

    log = {}

    def __setitem__(self, key, value):
        self.id = value

    def __getitem__(self, key):
        return self.id

    def __str__(self):
        return f"u{str(self.id)}a{self.data}"

    def __init__(self):
        pass

    def answer(self):
        pass

    def set_game(self, game):
        statebot.activeGame = game

    def send_message(self, id, msg, reply_markup=None, **kwargs):
        turn = 0
        if self.turn_callback is not None:
            turn = self.turn_callback()
        if turn not in self.log:
            self.log[turn] = []
        msg = f"to {id}: {msg}"
        if reply_markup is not None:
            msg += f"\n{str(reply_markup)}"
        self.log[turn].append(msg)

    def log_call(*args, **kwargs):
        print(str(args) + " " + str(kwargs))

    def echo(self, user, action):
        self.effective_user = self
        self.id = user["id"]
        self.callback_query = self
        self.data = str(action)
        self.bot = self
        statebot.echo(self, self)

    def current_turn_log(self) -> []:
        return self.log[self.turn_callback()]