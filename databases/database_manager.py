import sqlite3


class User:
    def __init__(self):
        self.connection = sqlite3.connect('../databases/data.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.make_database()

    def make_database(self):
        request = """CREATE TABLE IF NOT EXISTS users (
            id            INT     UNIQUE
                                  NOT NULL,
            username      TEXT    NOT NULL,
            game_name     TEXT    UNIQUE,
            is_authorised BOOLEAN NOT NULL,
            team    TEXT,
            collection TEXT
        );
        """
        req = """CREATE TABLE IF NOT EXISTS users_monsters (
            id    INTEGER PRIMARY KEY 
                          UNIQUE
                        NOT NULL,
            name  TEXT    NOT NULL,
            level INTEGER NOT NULL,
            exp   INTEGER NOT NULL,
            shiny BOOLEAN NOT NULL,
            skills TEXT
        );
        """
        try:
            self.cursor.execute(request)
            self.cursor.execute(req)
            self.connection.commit()
        except Exception as exception:
            return False

    def add_monster(self, id, name, level, exp, shiny, skills):
        try:
            req = """INSERT INTO users_monsters VALUES (?, ?, ?, ?, ?, ?)"""
            self.cursor.execute(req, (id, name, level, exp, shiny, skills))
            self.connection.commit()
        except Exception as exception:
            return False

    def add_user(self, id, username, game_name, team):
        collection = ''
        try:
            request = f"""INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)"""
            self.cursor.execute(request, (id, username, game_name, True, team, collection))
            self.connection.commit()
            return True
        except Exception as exception:
            return False

    def check_user(self, id):
        try:
            request = f"""SELECT * FROM users WHERE id = ?"""
            result = self.cursor.execute(request, (id,)).fetchone()
            if result:
                return True
            else:
                return False
        except Exception as exception:
            return False

    def delete_user(self, id):
        try:
            request = f'''DELETE FROM users WHERE id = ?'''
            self.cursor.execute(request, (id,))
            self.connection.commit()
            return True
        except Exception as exception:
            return False

    def change_user_nickname(self, nickname, id):
        try:
            request = f'''UPDATE users SET game_name = ? WHERE id = ?'''
            self.cursor.execute(request, (nickname, id,))
            self.connection.commit()
            return True
        except Exception as exception:
            return False

    def change_user_team(self, user_id, team):
        try:
            req = """UPDATE users SET team = ? WHERE id = ?"""
            self.cursor.execute(req, (team, user_id,))
            self.connection.commit()
        except Exception as ex:
            print(ex)

    def change_user_collection(self, user_id, collection):
        try:
            req = """UPDATE users SET collection = ? WHERE id = ?"""
            self.cursor.execute(req, (collection, user_id,))
            self.connection.commit()
        except Exception as ex:
            print(ex)

    def check_is_authorised(self, id):
        try:
            request = """SELECT is_authorised FROM users WHERE id = ?"""
            result = self.cursor.execute(request, (id,)).fetchone()
            result = result[0]
            if result == 1:
                return True
            return False
        except Exception as exception:
            print(exception)
            return False

    def is_authorised_disabled(self, id):
        try:
            request = """UPDATE users SET is_authorised = 0 WHERE id = ?"""
            self.cursor.execute(request, (id,))
            self.connection.commit()
            return True
        except Exception as exception:
            print(exception)
            return False

    def is_authorised_abled(self, id):
        try:
            request = """UPDATE users SET is_authorised = 1 WHERE id = ?"""
            self.cursor.execute(request, (id,))
            self.connection.commit()
            return True
        except Exception as exception:
            return False

    def update_user_gamename(self, name):
        pass

    def get_gamename(self, user_id):
        req = """SELECT game_name FROM users WHERE id = ?"""
        res = self.cursor.execute(req, (user_id,)).fetchone()
        return ''.join(res)

    def get_team(self, user_id):
        req = """SELECT team FROM users WHERE id = ?"""
        res = self.cursor.execute(req, (user_id,)).fetchone()
        return ''.join(res)

    def delete_monster(self, monster_id):
        req = """DELETE FROM users_monsters WHERE id = ?"""
        self.cursor.execute(req, (monster_id,))
        self.connection.commit()

    def get_monsters_ids(self):
        req = """SELECT id FROM users_monsters"""
        res = self.cursor.execute(req).fetchall()
        return res

    def get_collection(self, user_id):
        req = """SELECT collection FROM users WHERE id = ?"""
        res = self.cursor.execute(req, (user_id,)).fetchone()
        return ''.join(res)

    def get_monster_info(self, monster_id):
        req = """SELECT * FROM users_monsters WHERE id = ?"""
        res = self.cursor.execute(req, (monster_id,)).fetchone()
        return res

    def get_monster_name(self, monster_id):
        req = """SELECT name FROM users_monsters WHERE id = ?"""
        res = self.cursor.execute(req, (monster_id,)).fetchone()
        return ''.join(res)

    def get_monster_skills(self, monster_id):
        req = """SELECT skills FROM users_monsters WHERE id = ?"""
        res = self.cursor.execute(req, (monster_id,)).fetchone()
        return ''.join(res)

    def change_monster_exp(self, new_exp, monster_id):
        req = """UPDATE users_monsters SET exp = ? WHERE id = ?"""
        self.cursor.execute(req, (new_exp, monster_id,))
        self.connection.commit()

    def change_monster_params(self, new_name, new_lvl, new_exp, new_skills, monster_id):
        req = """UPDATE users_monsters SET name = ?, level = ?, exp = ?, skills = ? WHERE id = ?"""
        self.cursor.execute(req, (new_name, new_lvl, new_exp, new_skills, monster_id))
        self.connection.commit()

    def get_monster_exp(self, monster_id):
        req = """SELECT exp FROM users_monsters WHERE id = ?"""
        res = self.cursor.execute(req, (monster_id,)).fetchone()
        return res[0]

    def get_skill_info(self, skill):
        req = """SELECT info FROM Skills WHERE name = ?"""
        res = self.cursor.execute(req, (skill,)).fetchone()
        return ''.join(res)

    def change_monster_lvl(self, monster_id, level):
        req = """UPDATE users_monsters SET level = ? WHERE id = ?"""
        self.cursor.execute(req, (level, monster_id,))
        self.connection.commit()

    def change_monster_skills(self, monster_id, new_skills):
        req = """UPDATE users_monsters SET skills = ? WHERE id = ?"""
        self.cursor.execute(req, (new_skills, monster_id,))
        self.connection.commit()
