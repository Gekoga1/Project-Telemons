from enum import Enum


class Room:
    room_name: str
    author_id: str
    player_id: str
    score: int

    def __init__(self):
        self.score = 0
        print('проверка проверка')

class Stage(Enum):
    SELECT_DIFFICULTY = "select_difficulty"
    SELECT_WORD = "select_word"
    HOSTING_GAME = "hosting_game"
    SELECT_ROOM = "select_room"
    PLAY_GAME = "play_game"
