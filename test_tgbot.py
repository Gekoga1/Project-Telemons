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
id = 0
username = ''
is_authorised = False


# устанавливаем текущие данные пользователя
def set_user_data(user_id, name):
    global id, username
    id = user_id
    username = name


# обработка нажатий inline buttons
def check_query(update: Update, context: CallbackContext) -> None:
    global is_authorised
    query = update.callback_query
    if query.data == 'registration_yes':
        add_user(query=query)
    elif query.data == 'registration_no':
        query.edit_message_text('Ну нет так нет.')
    elif query.data == 'delete_yes':
        delete_user(query=query)
    else:
        query.edit_message_text('Процесс удаления пользователя отменён')


def make_database():
    request = """CREATE TABLE users IF NOT EXISTS(
    id       INT  NOT NULL
                  UNIQUE,
    username TEXT NOT NULL
);"""
    CURSOR.execute(request)
    CONNECTION.commit()


# проверяем существует ли такой пользователь в базе
def check_user(update: Update, context: CallbackContext, id):
    global is_authorised
    try:
        request = f"""SELECT * FROM users WHERE id = {id}"""
        result = CURSOR.execute(request).fetchone()
        if result:
            is_authorised = True
            set_user_data(update.message.from_user.id, update.message.from_user.username)
            return True
        else:
            return False
    except:
        update.message.reply_text('Произошла ошибка при авторизации, повторите ошибку позже.')


# добавляем пользователя в бд
def add_user(query):
    global is_authorised
    try:
        request = f"""INSERT INTO users VALUES(?, ?)"""
        CURSOR.execute(request, (id, username,))
        CONNECTION.commit()
        query.edit_message_text("Вы успешно зарегистрировались. Вы можете продолжать")
        is_authorised = True
    except Exception as exception:
        print(exception)
        query.edit_message_text('Произошла ошибка при регистрации пользователя. Повторите ошибку позже.')


# удаляем пользователя из бд
def delete_user(query):
    global is_authorised, id, username
    try:
        request = f'''DELETE FROM users WHERE id = {id}'''
        CURSOR.execute(request)
        CONNECTION.commit()
        query.edit_message_text(f'Пользователь удалён')
        is_authorised = False
        id = 0
        username = ''
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
    global id, username, is_authorised
    print(update.message.from_user.id)
    print(update.message.from_user.username)
    update.message.reply_text('Добро пожаловать. Для начала пройдите авторизацию.')
    id = update.message.from_user.id
    username = update.message.from_user.username
    if check_user(update=update, context=context, id=id):
        update.message.reply_text('У вас уже есть аккаунт. Вы можете продолжать')
        is_authorised = True
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
    check_user(update=update, context=context, id=update.message.from_user.id)
    if is_authorised:
        update.message.reply_text(f'id: {id}\n'
                                  f'username: {username}')
    else:
        update.message.reply_text('Вы не авторизованы')


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

    make_database()
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
