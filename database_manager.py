import sqlite3


class User:
    def __init__(self):
        self.connection = sqlite3.connect('databases/data.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.make_database()

    def make_database(self):
        request = """CREATE TABLE users (
            id            INT     UNIQUE
                                  NOT NULL,
            username      TEXT    NOT NULL,
            game_name     TEXT    UNIQUE,
            is_authorised BOOLEAN NOT NULL
        );
        """
        try:
            self.cursor.execute(request)
            self.connection.commit()
        except Exception as exception:
            print(exception)

    def add_user(self, id, username, game_name=None):
        try:
            request = f"""INSERT INTO users VALUES(?, ?, ?, ?)"""
            self.cursor.execute(request, (id, username, game_name, True,))
            self.connection.commit()
            return True
        except Exception as exception:
            print(exception)
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
            print(exception)
            return False

    def delete_user(self, id):
        try:
            request = f'''DELETE FROM users WHERE id = ?'''
            self.cursor.execute(request, (id,))
            self.connection.commit()
            return True
        except Exception as exception:
            print(exception)
            return False

    def check_is_authorised(self, id):
        try:
            request = """SELECT is_authorised FROM users WHERE id = ?"""
            result = self.cursor.execute(request, (id, )).fetchone()
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
            self.cursor.execute(request, (id, ))
            self.connection.commit()
            return True
        except Exception as exception:
            print(exception)
            return False

    def is_authorised_abled(self, id):
        try:
            request = """UPDATE users SET is_authorised = 1 WHERE id = ?"""
            self.cursor.execute(request, (id, ))
            self.connection.commit()
            return True
        except Exception as exception:
            print(exception)
            return False

    def update_user_gamename(self, name):
        pass
