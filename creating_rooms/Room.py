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
    blue_player: str
    red_player: str
    room_battle: Battle
    winner: str
    score: int


class Stage(Enum):
    HOSTING_GAME = "hosting_game"
    LOBBY = 'lobby'
    SELECT_ROOM = "select_room"
    PLAY_GAME = "play_game"
    PLAY_PVE = 'play_pve'
    CHANGE_MONSTER = 'change_monster'
