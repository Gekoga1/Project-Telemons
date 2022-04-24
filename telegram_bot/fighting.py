import logging
import random

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters

from creating_rooms.Room import Room, Stage



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

    query.edit_message_text(
        text='Подходящих комнат не нашлось, поэтому комната была создана.\nВы уже находитесь в ней, ждите пользователей')

    context.chat_data['roomName'] = user.username
    room.player_list.append(update.effective_message.chat_id)
    room.count_players += 1
    context.chat_data['stage'] = Stage.PLAY_GAME


def join_room(update: Update, context: CallbackContext) -> None:
    buttons = []
    for roomKey in rooms:
        buttons.append(InlineKeyboardButton(rooms[roomKey].room_name, callback_data=rooms[roomKey].room_name))
    keyboard = [buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    query.edit_message_text(text='Выберите комнату', reply_markup=reply_markup)


def select_room(update: Update, context: CallbackContext) -> None:
    context.chat_data['roomName'] = update.callback_query.data
    room_name = context.chat_data['roomName']
    room = rooms[room_name]
    if room.count_players <= 2:
        show_room(update=update, context=context, room=room)
    else:
        query = update.callback_query
        query.edit_message_text('Комната занята, повторите попытку')


def show_room(update: Update, context: CallbackContext, room) -> None:
    query = update.callback_query
    room.player_list.append(update.effective_message.chat_id)
    room.count_players += 1
    context.chat_data['stage'] = Stage.PLAY_GAME
    query.edit_message_text(text=f'Проверка проверка, это комната {room.room_name}\n')
    if room.count_players == 2:
        test_game(update=update, context=context, room=room)


def test_game(update: Update, context: CallbackContext, room) -> None:
    first_player = random.choice(room.player_list)
    update.effective_user.send_message(text='Напишите слово своему другу на проводе')
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
    text = update.message.text
    room_name = context.chat_data['roomName']

    room = rooms[room_name]
    chat_id = update.effective_message.chat_id
    opponent_name = ''
    for i in room.player_list:
        if i != chat_id:
            opponent_name = i
    update.message.bot.send_message(chat_id=opponent_name, text=f'Вам пришло сообщение: {text}')