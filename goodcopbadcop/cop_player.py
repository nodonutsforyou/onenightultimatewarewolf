from player import Player
from goodcopbadcop.roles import Roles


class CopPlayer(Player):
    cards = {}
    public_cards = {}
    gun = False
    aim = -1
    wounded = False
    equipment = []

    def has_more_than_one_item(self):
        return len(self.equipment) > 1

    def get_equipment(self):
        return self.equipment[0]

    def has_equipment(self):
        return len(self.equipment) > 0

    def get_card_numbers_list(self, public=None):
        ret = []
        for key, value in self.cards.items():
            if public is None or self.public_cards[key] == public:
                ret.append(key)
        return ret

    def get_cards_list(self, public=None):
        ret = []
        for key, value in self.cards.items():
            if public is None or self.public_cards[key] == public:
                ret.append(value)
        return ret

    def get_cards_dict(self, public=None):
        ret = {}
        for key, value in self.cards.items():
            if public is None or self.public_cards[key] == public:
                ret[key] = value
        return ret

    def check_has_3_cards(self):
        if len(self.cards) != 3:
            return False
        if 1 not in self.cards:
            return False
        if 2 not in self.cards:
            return False
        if 3 not in self.cards:
            return False
        return isinstance(self.cards[1], Roles) and isinstance(self.cards[2], Roles) and isinstance(self.cards[3], Roles)

    def flip_all_up(self):
        self.public_cards[1] = True
        self.public_cards[2] = True
        self.public_cards[3] = True

    def has_unfliped_cards(self):
        if not self.public_cards[1] or not self.public_cards[2] or not self.public_cards[3]:
            return True
        return False

    def check_winner(self):
        cards = 0
        for key, value in self.cards.items():
            if value == Roles.AGENT:
                cards += 1
            if value == Roles.KINGPIN:
                cards += 1
        return cards > 1

    def check_leader(self):
        for key, value in self.cards.items():
            if value == Roles.AGENT:
                return True
            if value == Roles.KINGPIN:
                return True
        return False

    def check_agent(self):
        for key, value in self.cards.items():
            if value == Roles.AGENT:
                return True
        return False

    def check_kingpin(self):
        for key, value in self.cards.items():
            if value == Roles.KINGPIN:
                return True
        return False

    def team(self):
        good, bad = 0, 0
        for key, value in self.cards.items():
            if value == Roles.AGENT:
                return Roles.GOOD
            if value == Roles.KINGPIN:
                return Roles.BAD
            if value == Roles.GOOD:
                good += 1
            if value == Roles.BAD:
                bad += 1
        if good >= bad:
            return Roles.GOOD
        elif good <= bad:
            return Roles.BAD
        return None

    def get_role(self):
        good, bad = 0, 0
        for key, value in self.cards.items():
            if value == Roles.AGENT:
                return Roles.AGENT
            if value == Roles.KINGPIN:
                return Roles.KINGPIN
            if value == Roles.GOOD:
                good += 1
            if value == Roles.BAD:
                bad += 1
        if good > bad:
            return Roles.GOOD
        elif good < bad:
            return Roles.BAD
        return None

    def set_cards(self, c1: Roles, c2: Roles, c3: Roles):
        self.cards = {
            1: c1,
            2: c2,
            3: c3,
        }
        self.public_cards = {
            1: False,
            2: False,
            3: False,
        }