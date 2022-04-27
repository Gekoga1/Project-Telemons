import random

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from configure.configuraion import rooms, teams
from creating_rooms.Room import Room, Stage
from game_logic.game_lib import *





def choose_type_fight(update: Update, context: CallbackContext):
    query = update.callback_query
    fights = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('PVP', callback_data='PVP'),
        ],
        [
            InlineKeyboardButton('Вернуться в главное меню', callback_data='main menu')
        ]
    ])
    query.edit_message_text('Выберите тип сражения', reply_markup=fights)


def fight_PVP(update: Update, context: CallbackContext):
    if len(rooms):
        join_room(update=update, context=context)
    else:
        create_room(update=update, context=context)


def create_room(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = update.effective_user
    room = Room()
    room.author_id = user.id
    room.room_name = user.username
    context.chat_data['create_room'] = room

    room: Room = context.chat_data['create_room']

    rooms[room.room_name] = room
    del context.chat_data['create_room']
    context.chat_data['stage'] = Stage.HOSTING_GAME
    room.count_players = 0
    room.player_list = []
    room.round_data = {}


    query.edit_message_text(
        text='Подходящих комнат не нашлось, поэтому комната была создана.\nВы уже находитесь в ней, ждите пользователей')

    context.chat_data['roomName'] = user.username
    room.player_list.append(update.effective_message.chat_id)
    room.count_players += 1
    context.chat_data['stage'] = Stage.PLAY_GAME


def close_room(update: Update, context: CallbackContext, room_name) -> None:
    del rooms[room_name]


def join_room(update: Update, context: CallbackContext) -> None:
    for roomKey in rooms:
        if rooms[roomKey].count_players <= 2:
            context.chat_data['roomName'] = roomKey
            room_name = context.chat_data['roomName']
            room = rooms[room_name]
            show_room(update=update, context=context, room=room)
    # buttons = []
    # for roomKey in rooms:
    #     if rooms[roomKey].count_players <= 2:
    #         buttons.append(InlineKeyboardButton(rooms[roomKey].room_name, callback_data=rooms[roomKey].room_name))
    # keyboard = [buttons]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    # query = update.callback_query
    # query.edit_message_text(text='Выберите комнату', reply_markup=reply_markup)


# def select_room(update: Update, context: CallbackContext) -> None:
#     context.chat_data['roomName'] = update.callback_query.data
#     room_name = context.chat_data['roomName']
#     room = rooms[room_name]
#     show_room(update=update, context=context, room=room)


def show_room(update: Update, context: CallbackContext, room) -> None:
    query = update.callback_query
    room.player_list.append(update.effective_message.chat_id)
    room.count_players += 1
    context.chat_data['stage'] = Stage.PLAY_GAME
    query.edit_message_text(text=f'Проверка проверка, это комната {room.room_name}\n')
    if room.count_players == 2:
        room.count_round = 1
        room.room_battle = Battle(None, teams[room.player_list[0]], None, teams[room.player_list[1]])
        test_game(update=update, context=context, room=room)


def test_game(update: Update, context: CallbackContext, room) -> None:
    first_player = random.choice(room.player_list)
    for i in room.player_list:
        try:
            context.bot.send_message(chat_id=i, text='Игра началась')
            context.bot.send_message(chat_id=i,
                                     text=f'Раунд номер {room.count_round}\nДелайте свой ход и ждите противник')
            context.bot.send_message(chat_id=i, text=room.battle.print(reverse=True))
        except Exception as exception:
            print(exception)

    # text = update.message.text
    # if text == 'hello':
    #     room_name = context.chat_data['roomName']
    #     context.chat_data['stage'] = Stage.LOBBY
    #     update.message.reply_text('УРА! Вы угадали это слово')
    #     del rooms[room_name]
    #     main_menu(update, context)
    #     print(rooms)
    # else:
    #     update.message.reply_text(text='Вы не угадали слово')


def send_message_opponent(update: Update, context: CallbackContext) -> None:
    room_name = context.chat_data['roomName']
    room = rooms[room_name]

    text = update.message.text
    user_data = update.effective_user.id

    if user_data not in room.round_data:
        room.round_data[user_data] = text

    if len(room.round_data) == 2:
        for user_id in room.round_data:
            data = room.round_data[user_id]
            if data == 'смена':
                pass
            elif data == '1':
                pass
            elif data == '2':
                pass
            elif data == '3':
                pass
            elif data == '4':
                pass
            else:
                context.bot.send_message(chat_id=user_id, text='Я не понимаю ваших действий')
        #     context.bot.send_message(chat_id=user_id, text=f'ход совершён')
        # for user_id in room.round_data:
        #     context.bot.send_message(chat_id=user_id, text=room.round_data[user_id])
        # room.count_round += 1
        # for user_id in room.round_data:
        #     context.bot.send_message(chat_id=user_id,
        #                              text=f'Раунд номер {room.count_round}\nДелайте свой ход и ждите противника')
        # room.round_data = {}

def change_current_monster(update: Update, context: CallbackContext, monster) -> None:
    pass


def finishing_PvP(update: Update, context: CallbackContext, room) -> None:
    for user_id in room.player_list:
        try:
            context.chat_data['stage'] = Stage.LOBBY
            del context.chat_data['roomName']
            del rooms[room.room_name]
            context.bot.send_message(chat_id=user_id,
                                     text='Битва закончилась, победила дружба\nПереходите в главное меню /main_menu')
        except Exception as exception:
            context.bot.send_message(chat_id=user_id,
                                     text='Битва закончилась, победила дружба\nПереходите в главное меню /main_menu')

    # text = update.message.text
    # room_name = context.chat_data['roomName']
    #
    # room = rooms[room_name]
    # chat_id = update.effective_message.chat_id
    # name = update.effective_user.name
    # opponent_name = ''
    # for i in room.player_list:
    #     if i != chat_id:
    #         opponent_name = i
    # update.message.bot.send_message(chat_id=opponent_name, text=f'Вам пришло сообщение от {name}:\n {text}')
