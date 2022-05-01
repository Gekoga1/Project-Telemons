import logging
import sqlite3
from math import floor, ceil
from random import choices, choice, randint
from typing import Union
from configure.configuraion import database_manager

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


type_dict = {
    "Normal": {
        "Normal": 1, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 2, "Ice": 1,
        "Fighting": 0.5, "Poison": 0.5, "Ground": 2, "Wind": 1, "Psychic": 1, "Bug": 1,
        "Rock": 1, "Ghost": 1, "Dragon": 1, "Dark": 0.5, "Steel": 1, "Fairy": 2, None: 1
    },
    "Fire": {
        "Normal": 1, "Fire": 1, "Water": 0.5, "Grass": 2, "Electric": 1, "Ice": 2,
        "Fighting": 1, "Poison": 1, "Ground": 0.5, "Wind": 1, "Psychic": 1, "Bug": 2,
        "Rock": 0.5, "Ghost": 1, "Dragon": 0.5, "Dark": 1, "Steel": 2, "Fairy": 1, None: 1
    },
    "Water": {
        "Normal": 1, "Fire": 2, "Water": 1, "Grass": 0.5, "Electric": 0.5, "Ice": 1,
        "Fighting": 1, "Poison": 0.5, "Ground": 1, "Wind": 1, "Psychic": 1, "Bug": 1,
        "Rock": 2, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 2, "Fairy": 1, None: 1
    },
    "Grass": {
        "Normal": 1, "Fire": 0.5, "Water": 2, "Grass": 1, "Electric": 1, "Ice": 0.5,
        "Fighting": 1, "Poison": 1, "Ground": 2, "Wind": 1, "Psychic": 1, "Bug": 0.5,
        "Rock": 2, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 1, "Fairy": 1, None: 1
    },
    "Electric": {
        "Normal": 0.5, "Fire": 1, "Water": 2, "Grass": 1, "Electric": 1, "Ice": 1,
        "Fighting": 1, "Poison": 1, "Ground": 0.5, "Wind": 2, "Psychic": 0.5, "Bug": 1,
        "Rock": 1, "Ghost": 1, "Dragon": 2, "Dark": 1, "Steel": 1, "Fairy": 1, None: 1
    },
    "Ice": {
        "Normal": 1, "Fire": 0.5, "Water": 1, "Grass": 2, "Electric": 1, "Ice": 1,
        "Fighting": 1, "Poison": 1, "Ground": 1, "Wind": 1, "Psychic": 1, "Bug": 2,
        "Rock": 0.5, "Ghost": 1, "Dragon": 2, "Dark": 1, "Steel": 0.5, "Fairy": 1, None: 1
    },
    "Fighting": {
        "Normal": 2, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 1, "Ice": 1,
        "Fighting": 1, "Poison": 1, "Ground": 1, "Wind": 0.5, "Psychic": 1, "Bug": 2,
        "Rock": 2, "Ghost": 0.5, "Dragon": 1, "Dark": 1, "Steel": 1, "Fairy": 0.5, None: 1
    },
    "Poison": {
        "Normal": 2, "Fire": 1, "Water": 2, "Grass": 1, "Electric": 1, "Ice": 1,
        "Fighting": 1, "Poison": 1, "Ground": 1, "Wind": 1, "Psychic": 0.5, "Bug": 1,
        "Rock": 1, "Ghost": 0.5, "Dragon": 1, "Dark": 1, "Steel": 0.5, "Fairy": 2, None: 1
    },
    "Ground": {
        "Normal": 1, "Fire": 2, "Water": 1, "Grass": 0.5, "Electric": 2, "Ice": 1,
        "Fighting": 1, "Poison": 1, "Ground": 1, "Wind": 0.5, "Psychic": 0.5, "Bug": 1,
        "Rock": 1, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 2, "Fairy": 1, None: 1
    },
    "Wind": {
        "Normal": 1, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 0.5, "Ice": 1,
        "Fighting": 2, "Poison": 1, "Ground": 2, "Wind": 1, "Psychic": 1, "Bug": 1,
        "Rock": 0.5, "Ghost": 2, "Dragon": 0.5, "Dark": 1, "Steel": 1, "Fairy": 1, None: 1
    },
    "Psychic": {
        "Normal": 1, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 2, "Ice": 1,
        "Fighting": 1, "Poison": 2, "Ground": 2, "Wind": 1, "Psychic": 1, "Bug": 0.5,
        "Rock": 1, "Ghost": 0.5, "Dragon": 1, "Dark": 0.5, "Steel": 1, "Fairy": 1, None: 1
    },
    "Bug": {
        "Normal": 1, "Fire": 0.5, "Water": 1, "Grass": 2, "Electric": 1, "Ice": 0.5,
        "Fighting": 0.5, "Poison": 1, "Ground": 1, "Wind": 1, "Psychic": 2, "Bug": 1,
        "Rock": 1, "Ghost": 1, "Dragon": 1, "Dark": 2, "Steel": 1, "Fairy": 1, None: 1
    },
    "Rock": {
        "Normal": 1, "Fire": 2, "Water": 0.5, "Grass": 0.5, "Electric": 1, "Ice": 2,
        "Fighting": 0.5, "Poison": 1, "Ground": 1, "Wind": 2, "Psychic": 1, "Bug": 1,
        "Rock": 1, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 1, "Fairy": 1, None: 1
    },
    "Ghost": {
        "Normal": 0.5, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 1, "Ice": 1,
        "Fighting": 2, "Poison": 2, "Ground": 1, "Wind": 0.5, "Psychic": 2, "Bug": 1,
        "Rock": 1, "Ghost": 1, "Dragon": 1, "Dark": 0.5, "Steel": 1, "Fairy": 1, None: 1
    },
    "Dragon": {
        "Normal": 1, "Fire": 2, "Water": 1, "Grass": 1, "Electric": 0.5, "Ice": 0.5,
        "Fighting": 1, "Poison": 1, "Ground": 1, "Wind": 2, "Psychic": 1, "Bug": 1,
        "Rock": 1, "Ghost": 1, "Dragon": 1, "Dark": 2, "Steel": 1, "Fairy": 0.5, None: 1
    },
    "Dark": {
        "Normal": 2, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 1, "Ice": 1,
        "Fighting": 1, "Poison": 1, "Ground": 1, "Wind": 1, "Psychic": 2, "Bug": 0.5,
        "Rock": 1, "Ghost": 2, "Dragon": 0.5, "Dark": 1, "Steel": 1, "Fairy": 0.5, None: 1
    },
    "Steel": {
        "Normal": 1, "Fire": 0.5, "Water": 0.5, "Grass": 1, "Electric": 1, "Ice": 2,
        "Fighting": 1, "Poison": 2, "Ground": 0.5, "Wind": 1, "Psychic": 1, "Bug": 1,
        "Rock": 1, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 1, "Fairy": 2, None: 1
    },
    "Fairy": {
        "Normal": 0.5, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 1, "Ice": 1,
        "Fighting": 2, "Poison": 0.5, "Ground": 1, "Wind": 1, "Psychic": 1, "Bug": 1,
        "Rock": 1, "Ghost": 1, "Dragon": 2, "Dark": 2, "Steel": 0.5, "Fairy": 1, None: 1
    }
}

cur = database_manager.cursor


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
        self.connection = sqlite3.connect('../databases/lib.db')
        self.cur = self.connection.cursor()
        # name and types init
        data = self.cur.execute(f"""SELECT name, type_1, type_2 FROM Monsters
                            WHERE id = {self.uid}""").fetchone()
        self.name, self.type_1, self.type_2 = data
        if nickname == '':
            self.nickname = self.name
        else:
            self.nickname = nickname

        # stats init
        data = self.cur.execute(f"""SELECT base_hp, base_atk, base_satk, base_speed FROM Monsters
                            WHERE id = {self.uid}""").fetchone()
        self.base_hp, self.base_atk, self.base_satk, self.base_speed = data
        self.iv_hp, self.iv_atk, self.iv_satk, self.iv_speed = iv

        # additional info init
        data = self.cur.execute(f"""SELECT catch_rate FROM Monsters
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
        self.hp_m, self.atk_m, self.satk_m, self.speed_m = 1, 1, 1, 1
        self.shield = 0
        self.alive = True

        self.statuses = []

    def __copy__(self):
        return self.__class__(uid=self.uid, lvl=self.lvl, exp=self.exp,
                              iv=(0, 0, 0, 0), shiny=self.shiny, skills=self.skills, owner=None)

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

    def convert_skills(self):
        return ';'.join([i.__class__.__name__ for i in self.skills if i is not None])

    def deconvert_skills(self, skills):
        self.skills = [None, None, None, None]
        for j, i in enumerate(skills.split(';')):
            exec(f'self.skills[{j}] = {i}()')

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
        self.hp_m, self.atk_m, self.satk_m, self.speed_m = 1, 1, 1, 1

        # current stats in battle
        self.update_current_stats()

        logging.debug(f"{self.name} stats rebuilded"
                      f"{self.get_stats()} - {self.get_current_stats()}")

    def update_current_stats(self, hp=True):
        if any(map(lambda x: not (0.2 < x < 5), [self.hp_m, self.atk_m, self.satk_m, self.speed_m])):
            self.hp_m, self.atk_m, self.satk_m, self.speed_m = \
                map(lambda x: clamp(0.2, 5, x), [self.hp_m, self.atk_m, self.satk_m, self.speed_m])

        self.c_atk, self.c_satk, self.c_speed = \
            self.atk * self.atk_m, self.satk * self.satk_m, self.speed * self.speed_m

        if hp:
            self.c_hp = self.hp * self.hp_m

        logging.debug(f"{self.name} stats updated"
                      f"{self.get_current_stats()}")

    def reset(self):
        self.rebuild_stats()
        self.alive = True
        self.shield = 0
        self.statuses = []

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
        logging.info(f"{self.name} got damaged for {floor(amount)} (true={true})")

        if true:
            self.c_hp -= floor(amount)
        else:
            if self.shield > 0:
                self.shield -= floor(amount)
                if self.shield < 0:
                    amount = -self.shield
                    self.shield = 0
                    self.c_hp -= amount
            else:
                self.c_hp -= floor(amount)

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

    def generate_ivs(self):
        self.iv_hp, self.iv_atk, self.iv_satk, self.iv_speed = (randint(0, 24) for _ in range(4))

    def get_ivs(self):
        return f"hp={self.iv_hp}, atk={self.iv_atk}, satk={self.iv_satk}, speed={self.iv_speed}"

    def get_skills(self):
        out = []
        for i in self.skills:
            if i is not None:
                out.append(i.name)
            else:
                out.append('None')
        return out


class Spylit(Monster_Template):
    def __init__(self, nickname='', lvl=1, exp=0, iv=(0, 0, 0, 0), shiny=False,
                 skills=None, owner=None):
        uid = 1
        super().__init__(uid, nickname, lvl, exp, iv, shiny, skills, owner)

        # dict of skills with levels when they're learnable
        # {lvl: skill id}
        self.skills_rule = {
            1: Screech(),
            2: Slash(),
            10: Blunt_strike()
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
            2: Slash(),
            10: Blunt_strike()
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
            2: Slash(),
            10: Blunt_strike(),
            15: Natures_call()
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
        self.connection = sqlite3.connect('../databases/lib.db')
        self.cur = self.connection.cursor()
        # init of basic data
        data = self.cur.execute(f"""SELECT name, info, type, stat, power, accuracy FROM Skills
                            WHERE id = {self.uid}""").fetchone()
        self.name, self.info, self.type, self.stat, self.power, self.accuracy = data
        self.c_accuracy = 100

    def __str__(self):
        return self.name

    def get_info(self):
        return self.info

    def use(self, owner: Monster_Template, target: Monster_Template):
        if choices([True, False], weights=[self.c_accuracy, 100 - self.c_accuracy], k=1)[0]:
            logging.info(f"{owner.name} uses {self.name} ({self.c_accuracy})")

            if self.stat == "atk":
                atk = owner.c_atk
            else:
                atk = owner.c_satk

            self.c_accuracy -= self.accuracy
            target.get_damage(self.power / 100 * atk *
                              type_dict[self.type][target.type_1] * type_dict[self.type][target.type_2])
        else:
            logging.info(f"{owner.name} tried to use {self.name}, but failed with chance {self.c_accuracy}%")


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
            logging.info(f"{owner.name} uses {self.name} ({self.c_accuracy})")

            target.atk_m = target.atk_m * 0.8
            target.satk_m = target.satk_m * 0.8

            self.c_accuracy -= self.accuracy
        else:
            logging.info(f"{owner.name} tried to use {self.name}, but failed with chance {self.c_accuracy}%")


class Gods_will(Skill_Template):
    def __init__(self):
        uid = 3
        super().__init__(uid)


class Blunt_strike(Skill_Template):
    def __init__(self):
        uid = 4
        super().__init__(uid)


class Natures_call(Skill_Template):
    def __init__(self):
        uid = 5
        super().__init__(uid)


class Battle:
    def __init__(self, blue_player, blue_team: list[Monster_Template], red_player, red_team: list[Monster_Template]):
        for monster in blue_team + red_team:
            monster.reset()

        self.blue_player = blue_player
        self.blue_team = blue_team
        self.blue_active = blue_team[0]
        self.blue_last = ''

        self.red_player = red_player
        self.red_team = red_team
        self.red_active = red_team[0]
        self.red_last = ''

    def print(self, reverse=False):
        if reverse:
            return f"{self.blue_active.battle_stats()}\n\n{self.red_active.battle_stats()}"
        else:
            return f"{self.red_active.battle_stats()}\n\n{self.blue_active.battle_stats()}"

    def change(self, player, new):
        if player == 0:
            if self.blue_active != self.blue_team[new] and self.blue_team[new].alive:
                self.blue_active = self.blue_team[new]
                self.blue_active.on_change()

                return True
            else:
                return False
        elif player == 1:
            if self.red_active != self.red_team[new] and self.red_team[new].alive:
                self.red_active = self.red_team[new]
                self.red_active.on_change()

                return True
            else:
                return False

    def red_turn(self, schoice):
        if self.red_active.skills[schoice].name != self.red_last:
            for skill in self.red_active.skills:
                if skill is not None:
                    skill.c_accuracy = 100
        self.red_active.skills[schoice].use(self.red_active, self.blue_active)
        self.red_last = self.red_active.skills[schoice].name

    def blue_turn(self, schoice):
        if self.blue_active.skills[schoice].name != self.blue_last:
            for skill in self.blue_active.skills:
                if skill is not None:
                    skill.c_accuracy = 100
        self.blue_active.skills[schoice].use(self.blue_active, self.red_active)
        self.blue_last = self.blue_active.skills[schoice].name

    def battle(self):
        while all(map(lambda x: x.alive, self.blue_team)) and \
                all(map(lambda x: x.alive, self.red_team)):
            red_choice = randint(0, 3 - self.red_active.skills.count(None))
            blue_choice = randint(0, 3 - self.blue_active.skills.count(None))

            if self.red_active.c_speed > self.blue_active.c_speed:
                self.red_turn(red_choice)
                self.blue_turn(blue_choice)
            elif self.red_active.c_speed < self.blue_active.c_speed:
                self.blue_turn(blue_choice)
                self.red_turn(red_choice)
            else:
                if choice([True, False]):
                    self.red_turn(red_choice)
                    self.blue_turn(blue_choice)
                else:
                    self.blue_turn(blue_choice)
                    self.red_turn(red_choice)

            self.update()
        print('gg')

    def update(self):
        for monster in self.blue_team + self.red_team:
            monster.update_current_stats(hp=False)

        print(self.print())

    def start(self):
        self.blue_active.on_change()
        self.red_active.on_change()


if __name__ == "__main__":
    test = Spylit(shiny=True, lvl=20)
    test.generate_skills()

    dummy = Spyland(lvl=15)
    dummy.generate_skills()

    battle = Battle(None, [test], None, [dummy])
    battle.start()
