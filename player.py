class Player:
    #to init
    c1, c2, c3 = None, None, None
    name = None
    id = None
    num = None
    telegram_obj = None

    #default values
    dead = False

    def __init__(self, num, player_obj):
        self.num = num
        self.id = player_obj['id']
        self.name = str(player_obj['first_name']) + ' ' + str(player_obj['last_name'])
        self.telegram_obj = player_obj
