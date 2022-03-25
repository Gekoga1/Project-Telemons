import random
from typing import Union
import sqlite3
import logging
from math import floor, ceil
from random import choices


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
    def __init__(self, uid: int, nickname='', lvl=1, exp=0, iv=(0, 0, 0, 0), shiny=False,
                 skills=None, owner=None):
        """
        :param uid: id of monster in database
        :param lvl: level of monster
        :param exp: experience
        :param iv: individual values, gives addition stats
        :param shiny: shiny :)
        """
        self.owner = owner

        if skills is None:
            skills = [None, None, None, None]

        self.uid = uid
        self.lvl = lvl
        self.exp = exp

        self.skills = skills

        # dict of skills with levels when they're learnable
        # {lvl: skill inst}
        self.skills_rule = {}

        # dict of evolutions
        # {lvl: evolution type}
        self.evolution_rule = {}

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

        # true stats
        self.hp, self.atk, self.satk, self.speed = list(map(
            lambda x: int(x / 100 * self.lvl),
            [self.base_hp + self.iv_hp, self.base_atk + self.iv_atk,
             self.base_satk + self.iv_satk, self.base_speed + self.iv_speed]))

        # current stats in battle
        self.c_hp, self.c_atk, self.c_satk, self.c_speed = self.hp, self.atk, self.satk, self.speed
        self.shield = 0
        self.alive = True

    def on_change(self):
        pass

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

    def generate_bar(self):
        if self.alive:
            shield = floor(self.shield / (self.hp + self.shield) * 10)
            hp = ceil(self.c_hp / self.hp * 10)

            if hp + shield > 10:
                hp -= hp + shield - 10
                return f"{'🟩' * hp}{'🟫' * shield}"
            else:
                return f"{'🟩' * hp}{' ' * (2 * (10 - hp - shield))}{'🟫' * shield}"
        else:
            return "☠"

    def battle_stats(self, nickname=False):
        """
        :param nickname: show name or nickname?
        :return: ready for output name, lvl, hp
        """
        if self.shiny:
            return f"{self.get_name(nickname=nickname)}" \
                   f"{' ' * (19 - len(f'{self.get_name(nickname=nickname)}lv.{self.lvl}'))}" \
                   f"lv.{self.lvl}\n" \
                   f"{self.generate_bar()}"
        else:
            return f"{self.get_name(nickname=nickname)}" \
                   f"{' ' * (20 - len(f'{self.get_name(nickname=nickname)}lv.{self.lvl}'))}" \
                   f"lv.{self.lvl}\n" \
                   f"{self.generate_bar()}"

    def get_types(self) -> list:
        """
        :return: types in form of list
        """

        return [self.type_1, self.type_2]

    def get_base_stats(self) -> dict:
        """
        :return: base stats in form of dict
        """
        return {"hp": self.base_hp, "atk": self.base_atk, "satk": self.base_satk, "speed": self.base_speed}

    def get_stats(self) -> dict:
        """
        :return: true stats in form of dict
        """
        return {"hp": self.hp, "atk": self.atk, "satk": self.satk, "speed": self.speed}

    def get_current_stats(self) -> dict:
        """
        :return: current stats in form of dict
        """
        return {"hp": self.c_hp, "atk": self.c_atk, "satk": self.c_satk, "speed": self.c_speed}

    def rebuild_stats(self):
        # true stats
        self.hp, self.atk, self.satk, self.speed = list(map(
            lambda x: int(x / 100 * self.lvl),
            [self.base_hp + self.iv_hp, self.base_atk + self.iv_atk,
             self.base_satk + self.iv_satk, self.base_speed + self.iv_speed]))

        # current stats in battle
        self.c_hp, self.c_atk, self.c_satk, self.c_speed = self.hp, self.atk, self.satk, self.speed

        logging.debug(f"{self.name} stats rebuilded"
                      f"{self.get_stats()} - {self.get_current_stats()}")

    def show_skills(self):
        out = []

        for index, skill in enumerate(self.skills):
            if skill is None:
                out.append(f"{index + 1}. None")
            else:
                out.append(f"{index + 1}. {skill.name}")

        return '\n'.join(out)

    def lvl_up(self):
        """
        function of leveling up
        :return: None
        """
        self.lvl += 1
        if self.lvl in self.skills_rule.keys():
            skill = self.skills_rule[self.lvl]

            print(f"{self.get_name(nickname=True)} can learn {skill.name}")
            if input('Learn it? (Y/N)').lower() == 'y':
                if None not in self.skills:
                    print(self.show_skills())
                    self.skills[int(input(
                        f'What skill {self.get_name(nickname=True)} should forget? (1-4)')) - 1] = skill
                else:
                    self.skills[self.skills.index(None)] = skill

        logging.info(f'{self.name} lvl {self.lvl - 1} -> {self.lvl}')

        if self.lvl in self.evolution_rule.keys():
            return True

    def get_exp(self, amount: int):
        """
        :param amount: amount of exp get
        :return: None
        """
        lvl_up = False

        self.exp += amount
        logging.info(f'{self.name} gets {amount} exp')

        self.exp = clamp(0, 1, self.exp, only_min=True)

        while self.exp >= 100 and self.lvl != 100:
            self.exp -= 100
            lvl_up = True
            if self.lvl_up():
                next_form = self.evolution_rule[self.lvl](self.nickname, self.lvl, self.exp,
                                                          (self.iv_hp, self.iv_atk, self.iv_satk, self.iv_speed),
                                                          self.shiny, self.skills, self.owner)

                logging.info(f'{self.name} evolved into {next_form.name}')

                next_form.get_exp(0)
                return next_form

        if lvl_up:
            self.rebuild_stats()

        return self

    def get_damage(self, amount: float, true=False):
        logging.info(f"{self.name} got damaged for {amount} (true={true})")

        if true:
            self.c_hp -= floor(amount)
        else:
            if self.shield > 0:
                self.shield -= floor(amount)
                if self.shield < 0:
                    amount = -self.shield
                    self.shield = 0
                    self.c_hp -= amount

        self.death_check()

    def death_check(self):
        if self.c_hp <= 0:
            self.alive = False
            self.c_hp = 0

            logging.info(f'{self.name} died')

    def generate_skills(self):
        for step in self.skills_rule.keys():
            if step <= self.lvl:
                for index in range(4):
                    if self.skills_rule[step] not in self.skills and self.skills[index] is None:
                        self.skills[index] = self.skills_rule[step]
                if self.skills_rule[step] not in self.skills:
                    self.skills[choices([0, 1, 2, 3], k=1)[0]] = self.skills_rule[step]
            else:
                return


class Spylit(Monster_Template):
    def __init__(self, nickname='', lvl=1, exp=0, iv=(0, 0, 0, 0), shiny=False,
                 skills=None, owner=None):
        uid = 1
        super().__init__(uid, nickname, lvl, exp, iv, shiny, skills, owner)

        # dict of skills with levels when they're learnable
        # {lvl: skill id}
        self.skills_rule = {
            1: Screech(),
            2: Slash()
        }

        # dict of evolutions
        # {lvl: evolution type}
        self.evolution_rule = {
            16: Spylish
        }

    def on_change(self):
        self.shield = floor(self.hp * 0.67)


class Spylish(Monster_Template):
    def __init__(self, nickname='', lvl=1, exp=0, iv=(0, 0, 0, 0), shiny=False,
                 skills=None, owner=None):
        uid = 2
        super().__init__(uid, nickname, lvl, exp, iv, shiny, skills, owner)

        # dict of skills with levels when they're learnable
        # {lvl: skill id}
        self.skills_rule = {
            1: Screech(),
            2: Slash()
        }

        # dict of evolutions
        # {lvl: evolution type}
        self.evolution_rule = {
            36: Spyland
        }


class Spyland(Monster_Template):
    def __init__(self, nickname='', lvl=1, exp=0, iv=(0, 0, 0, 0), shiny=False,
                 skills=None, owner=None):
        uid = 3
        super().__init__(uid, nickname, lvl, exp, iv, shiny, skills, owner)

        # dict of skills with levels when they're learnable
        # {lvl: skill id}
        self.skills_rule = {
            1: Screech(),
            2: Slash()
        }

        # dict of evolutions
        # {lvl: evolution type}
        self.evolution_rule = {}


class Skill_Template:
    def __init__(self, uid):
        """
        :param uid: id of skill in database
        """
        self.uid = uid

        # init of basic data
        data = cur.execute(f"""SELECT name, info, type, stat, power, accuracy FROM Skills
                            WHERE id = {self.uid}""").fetchone()
        self.name, self.info, self.type, self.stat, self.power, self.accuracy = data
        self.c_accuracy = 100

    def __str__(self):
        return self.name

    def get_info(self):
        return self.info

    def use(self, owner: Monster_Template, target: Monster_Template):
        if choices([True, False], weights=[self.c_accuracy, 100 - self.c_accuracy], k=1)[0]:
            logging.info(f"{owner.name} uses {self.name}")

            if self.stat == "atk":
                atk = owner.c_atk
            else:
                atk = owner.c_satk

            self.c_accuracy -= self.accuracy
            target.get_damage(self.power / 100 * atk)
        else:
            logging.info(f"{owner.name} tried to use {self.name}, but failed")


class Slash(Skill_Template):
    def __init__(self):
        uid = 1
        super().__init__(uid)


class Screech(Skill_Template):
    def __init__(self):
        uid = 2
        super().__init__(uid)

    def use(self, owner: Monster_Template, target: Monster_Template):
        if choices([True, False], weights=[self.c_accuracy, 100 - self.c_accuracy], k=1)[0]:
            logging.info(f"{owner.name} uses {self.name}")

            target.c_atk = int(target.c_atk * 0.8)
            target.c_satk = int(target.c_satk * 0.8)
        else:
            logging.info(f"{owner.name} tried to use {self.name}, but failed")


test = Spylit(shiny=True, lvl=1)
test.generate_skills()

print(test.battle_stats())
print('--------------------------------------')

test = test.get_exp(1500)

print(test.battle_stats())
print('--------------------------------------')

test = test.get_exp(2000)

print(test.battle_stats())
print('--------------------------------------')
