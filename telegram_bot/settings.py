from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from main import database_manager


def game_settings(update: Update, context: CallbackContext):  # настройки игры
    query = update.callback_query
    if query is not None:
        keyboard = InlineKeyboardMarkup([
            [

                InlineKeyboardButton("Изменить свое имя в игре", callback_data='change_game_name'),
            ],
        ])
        query.edit_message_text('Что вы хотите сделать?', reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup([
            [

                InlineKeyboardButton("Изменить свое имя в игре", callback_data='change_game_name'),
            ],
        ])
        update.message.reply_text('Что вы хотите сделать?', reply_markup=keyboard)


def change_user_nickname(update: Update, context: CallbackContext):  # изменение ника
    id = update.effective_user.id
    message = update.message.text
    message_list = message.split()
    if len(message_list) <= 1:
        update.message.reply_text('Вы не ввели ник!')
    elif len(message_list) > 2:
        update.message.reply_text("Слишком много ников, введите только 1")
    else:
        nickname = message_list[1]
        if database_manager.change_user_nickname(nickname=nickname, id=id):
            update.message.reply_text("Ник изменён")
        else:
            update.message.reply_text("Ошибка при изменении ника, повторите попытку позже")


def nickname_or_tgname(update: Update, context: CallbackContext):  # выбор: имя из тг или придуманный ник
    query = update.callback_query
    name_ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Придумать ник', callback_data='nickname'),
            InlineKeyboardButton('Взять из телеграма', callback_data='tg_name')
        ]
    ])
    query.edit_message_text('Вы хотите придумать ник?', reply_markup=name_ques)