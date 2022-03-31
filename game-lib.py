from typing import Union
import sqlite3
import logging


logging.basicConfig(
    filename='game-lib.log',
    format='%(asctime)s %(levelname)s | %(message)s',
    level=logging.DEBUG
)


def clamp(minimum: float, maximum: float, value: Union[int, float],
          only_min=False, only_max=False) -> Union[int, float]:
    if not only_max and value < minimum:
        value = minimum
    elif not only_min and value > maximum:
        value = maximum

    return value


con = sqlite3.connect("lib.db")
cur = con.cursor()


class Monster_Template:
    def __init__(self, uid: int, nickname='', lvl=1, exp=0, iv=(0, 0, 0, 0), shiny=False):
        """
        :param uid: id of monster in database
        :param lvl: level of monster
        :param exp: experience
        :param iv: individual values, gives addition stats
        :param shiny: shiny :)
        """

        self.uid = uid
        self.lvl = lvl
        self.exp = exp

        # name and types init
        data = cur.execute(f"""SELECT name, type_1, type_2 FROM Monsters
                            WHERE id = {self.uid}""").fetchone()
        self.name, self.type_1, self.type_2 = data

        if nickname == '':
            self.nickname = self.name
        else:
            self.nickname = nickname

        # stats init
        data = cur.execute(f"""SELECT base_hp, base_atk, base_satk, base_speed FROM Monsters
                            WHERE id = {self.uid}""").fetchone()
        self.base_hp, self.base_atk, self.base_satk, self.base_speed = data
        self.iv_hp, self.iv_atk, self.iv_satk, self.iv_speed = iv

        # additional info init
        data = cur.execute(f"""SELECT catch_rate FROM Monsters
                            WHERE id = {self.uid}""").fetchone()
        self.catch_rate = data

        self.shiny = shiny

    def get_name(self, nickname=False):
        """
        :param nickname: show name or nickname?
        :return: name or star&name if monster is shiny
        """

        if nickname:
            if self.shiny:
                return f"🌟{self.nickname}"
            else:
                return self.nickname
        else:
            if self.shiny:
                return f"🌟{self.name}"
            else:
                return self.name

    def battle_stats(self, nickname=False):
        """
        :param nickname: show name or nickname?
        :return: ready for output name, lvl, hp
        """

        if self.shiny:
            return f"{self.get_name(nickname=nickname)}" \
                   f"{' ' * (19 - len(f'{self.get_name(nickname=nickname)}lv.{self.lvl}'))}" \
                   f"lv.{self.lvl}\n" \
                   f"🟩🟩🟩🟩🟩🟩🟩🟫🟫🟫"
        else:
            return f"{self.get_name(nickname=nickname)}" \
                   f"{' ' * (20 - len(f'{self.get_name(nickname=nickname)}lv.{self.lvl}'))}" \
                   f"lv.{self.lvl}\n" \
                   f"🟩🟩🟩🟩🟩🟩🟩🟫🟫🟫"

    def get_types(self) -> list:
        """
        :return: types in form of list
        """

        return [self.type_1, self.type_2]

    def get_base_stats(self) -> dict:
        """
        :return: stats in form of dict
        """

        return {"hp": self.base_hp, "atk": self.base_atk, "satk": self.base_satk, "speed": self.base_speed}

    def evolve(self):
        """
        evolves this monster
        :return: next evolution of monster
        """

        pass

    def lvl_up(self):
        """
        function of leveling up
        :return: None
        """

        self.lvl += 1

        logging.info(f'{self.name} lvl {self.lvl - 1} -> {self.lvl}')

    def get_exp(self, amount: int):
        """
        :param amount: amount of exp get
        :return: None
        """

        self.exp += amount

        logging.info(f'{self.name} gets {amount} exp')

        self.exp = clamp(0, 1, self.exp, only_min=True)

        while self.exp >= 100 and self.lvl != 100:
            self.exp -= 100
            self.lvl_up()


test = Monster_Template(1, shiny=True)
print(test)
print(test.battle_stats())
test.get_exp(100)
print(test.battle_stats())
test.get_exp(1000)
print(test.battle_stats())
test.get_exp(-200)
print(test.battle_stats())