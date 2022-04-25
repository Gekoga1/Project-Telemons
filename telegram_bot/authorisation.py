from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from configure.configuraion import database_manager


def nickname_settings(update: Update, context: CallbackContext):  # собственный ник
    name = update.message.text
    add_user(update, context, name)
    database_manager.is_authorised_abled(update.effective_user.id)
    update.message.reply_text(f"Вы успешно зарегистрировались.\n\nВаше имя в игре {name}\n"
                              f"Вы всегда можете его изменить, вызвав команду /game_settings\n\n"
                              f"Чтобы выйти в главное меню, введите команду /main_menu")


def registration_success(update: Update, context: CallbackContext):  # имя из тг
    query = update.callback_query
    name = update.effective_user.name
    add_user(update, context, name)
    database_manager.is_authorised_abled(update.effective_user.id)
    query.edit_message_text(f"Вы успешно зарегистрировались.\n\nВаше имя в игре {name}\n"
                            f"Вы всегда можете его изменить, вызвав команду /game_settings\n\n"
                            f"Чтобы выйти в главное меню, введите команду /main_menu")


# проверяем существует ли такой пользователь в базе
def check_user(update: Update, context: CallbackContext):
    try:
        id = update.effective_user.id
        return database_manager.check_user(id=id)
    except Exception as exception:
        print(exception)
        update.message.reply_text('Произошла ошибка при авторизации, повторите попытку позже.')


# добавляем пользователя в бд
def add_user(update: Update, context: CallbackContext, nickname):
    # query = update.callback_query
    try:
        id = update.effective_user.id
        username = update.effective_user.username
        if username is None:
            username = update.effective_user.name
        database_manager.add_user(id=id, username=username, game_name=nickname)
    except Exception as exception:
        print(exception)
        update.message.reply_text('Произошла ошибка при регистрации пользователя. Повторите попытку позже.')


# удаляем пользователя из бд
def delete_user(update: Update, context: CallbackContext):
    query = update.callback_query
    try:
        id = update.effective_user.id
        if database_manager.delete_user(id=id):
            query.edit_message_text('Удаление прошло успешно')
    except Exception as exception:
        print(exception)
        query.edit_message_text('Произошла ошибка при удалении пользователя, повторите попытку позже.')


# Предложение удалить пользователя
def delete_user_suggestion(update: Update, context: CallbackContext):
    delete_user_answer = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Да", callback_data='delete_yes'),
            InlineKeyboardButton("Нет", callback_data='delete_no'),
        ],
    ])
    update.message.reply_text('Вы действительно хотите удалить свой профиль из базы данных?',
                              reply_markup=delete_user_answer)

    #     update.message.reply_text("Вы успешно зарегистрировались. Вы можете продолжать")
