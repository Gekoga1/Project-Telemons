import logging
import sqlite3

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

from game_lib import result1, result2, result3, result4

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
CONNECTION = sqlite3.connect("databases/data.db", check_same_thread=False)
CURSOR = CONNECTION.cursor()


# id = 0
# username = ''
# is_authorised = False


# устанавливаем текущие данные пользователя
# def set_user_data(user_id, name):
#     global id, username
#     id = user_id
#     username = name

def get_user_id(username):  # получение id пользователя
    req = """SELECT id FROM users WHERE username = ?"""
    res = CURSOR.execute(req, username).fetchone()
    print(*res, 'get_user_id')
    return res


def get_username(user_id):  # получение имени пользователя
    req = """SELECT username FROM users WHERE id = ?"""
    res = CURSOR.execute(req, (user_id,)).fetchone()
    return ''.join(res)


def get_authorised(user_id):
    req = """SELECT is_authorised FROM users WHERE id = ?"""
    result = CURSOR.execute(req, (user_id,)).fetchone()
    result = result[0]
    if result == 1:
        return True
    return False


# обработка нажатий inline buttons
def check_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query.data == 'registration_yes':
        add_user(update=update, context=context)
    elif query.data == 'registration_no':
        query.edit_message_text('Ну нет так нет.')
    elif query.data == 'delete_yes':
        delete_user(update=update, context=context)
    else:
        query.edit_message_text('Процесс удаления пользователя отменён')


def make_database():
    request = """CREATE TABLE users (
    id            INT     UNIQUE
                          NOT NULL,
    username      TEXT    NOT NULL,
    is_authorised BOOLEAN NOT NULL
);
"""
    CURSOR.execute(request)
    CONNECTION.commit()


# проверяем существует ли такой пользователь в базе
def check_user(update: Update, context: CallbackContext):
    try:
        id = update.effective_user.id
        request = f"""SELECT * FROM users WHERE id = {id}"""
        result = CURSOR.execute(request).fetchone()
        if result:
            return True
        else:
            return False
    except Exception as exception:
        print(exception)
        update.message.reply_text('Произошла ошибка при авторизации, повторите ошибку позже.')


# добавляем пользователя в бд
def add_user(update: Update, context: CallbackContext):
    query = update.callback_query
    try:
        id = update.effective_user.id
        username = update.effective_user.username
        request = f"""INSERT INTO users VALUES(?, ?, ?)"""
        CURSOR.execute(request, (id, username, True))
        CONNECTION.commit()
        query.edit_message_text("Вы успешно зарегистрировались. Вы можете продолжать")
    except Exception as exception:
        print(exception)
        query.edit_message_text('Произошла ошибка при регистрации пользователя. Повторите ошибку позже.')


# удаляем пользователя из бд
def delete_user(update: Update, context: CallbackContext):
    query = update.callback_query
    try:
        username = update.effective_user.username
        id = get_user_id(username=username)
        request = f'''DELETE FROM users WHERE id = {id}'''
        CURSOR.execute(request)
        CONNECTION.commit()
        query.edit_message_text(f'Пользователь удалён')
    except Exception as exception:
        print(exception)
        query.edit_message_text('Произошла ошибка при удалении пользователя, повторите ошибку позже.')


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


# Начальная функция. Проверяет есть ли аккаунт или нет, регистрация
def start(update: Update, context: CallbackContext) -> None:
    print(update.effective_user.id)
    print(update.effective_user.username)
    update.message.reply_text('Добро пожаловать. Для начала пройдите авторизацию.')
    if check_user(update=update, context=context):
        update.message.reply_text('У вас уже есть аккаунт. Вы можете продолжать')
    else:
        registration_answer = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Да", callback_data='registration_yes'),
                InlineKeyboardButton("Нет", callback_data='registration_no'),
            ],
        ])
        update.message.reply_text('У вас ещё нет аккаунта. Хотите зарегистрироваться', reply_markup=registration_answer)
        #     update.message.reply_text("Вы успешно зарегистрировались. Вы можете продолжать")


# Вывод информации об игре
def info(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Это игра')


# Вывод данных о пользователе(больше для дебага)
def profile(update: Update, context: CallbackContext):
    check_user(update=update, context=context)
    id = update.effective_user.id
    username = update.effective_user.username
    if get_authorised(user_id=id):
        update.message.reply_text(f'id: {id}\n'
                                      f'username: {username}')
    # if is_authorised:
    #     update.message.reply_text(f'id: {id}\n'
    #                               f'username: {username}')
    # else:
    #     update.message.reply_text('Вы не авторизованы')


# Пример функционала игры
def show_game_example(update: Update, context: CallbackContext):
    update.message.reply_text(result1)
    update.message.reply_text(result2)
    update.message.reply_text(result3)
    update.message.reply_text(result4)


def main() -> None:
    updater = Updater("5278816766:AAFWnPxEguubVCXlGw9k8shgz_-0aroopq0")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("info", info))
    dispatcher.add_handler(CommandHandler("profile", profile))
    dispatcher.add_handler(CommandHandler("show", show_game_example))
    dispatcher.add_handler(CommandHandler("delete_account", delete_user_suggestion))
    updater.dispatcher.add_handler(CallbackQueryHandler(check_query))

    # make_database()
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
