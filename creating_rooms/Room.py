from enum import Enum

from game_logic.game_lib import *


class Room:
    room_name: str
    count_players: int
    player_list: list
    count_round: int
    round_data: dict
    author_id: str
    player_id: str
    room_battle: Battle
    score: int

    def __init__(self):
        self.score = 0
        print('проверка проверка')


class Stage(Enum):
    HOSTING_GAME = "hosting_game"
    LOBBY = 'lobby'
    SELECT_ROOM = "select_room"
    PLAY_GAME = "play_game"

