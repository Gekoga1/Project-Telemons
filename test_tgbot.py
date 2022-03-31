import logging
import sqlite3

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
CONNECTION = sqlite3.connect("databases/users.db", check_same_thread=False)
CURSOR = CONNECTION.cursor()
user_id = 0
username = ''
is_authorised = False


# устанавливаем текущие данные пользователя
def set_user_data(id, name):
    global user_id, username
    user_id = id
    username = name


# проверяем существует ли такой пользователь в базе
def check_user(update: Update, context: CallbackContext, user_id):
    global is_authorised
    try:
        request = f"""SELECT * FROM ids WHERE user_id = {user_id}"""
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
def add_user(update: Update, context: CallbackContext) -> None:
    global is_authorised
    query = update.callback_query
    if query.data == '1':
        try:
            request = f"""INSERT INTO ids VALUES(?, ?)"""
            CURSOR.execute(request, (user_id, username,))
            CONNECTION.commit()
            query.edit_message_text("Вы успешно зарегистрировались. Вы можете продолжать")
            is_authorised = True
        except Exception as exception:
            print(exception)
            query.edit_message_text('Произошла ошибка при регистрации пользователя. Повторите ошибку позже.')
    else:
        query.edit_message_text('Ну нет так нет.')


# удаляем пользователя из бд
def delete_user(update: Update, context: CallbackContext):
    global is_authorised, user_id, username
    try:
        request = f'''DELETE FROM ids WHERE user_id = {user_id}'''
        CURSOR.execute(request)
        CONNECTION.commit()
        update.message.reply_text(f'Пользователь удалён')
        is_authorised = False
        user_id = 0
        username = ''
    except Exception as exception:
        print(exception)
        update.message.reply_text('Произошла ошибка при удалении пользователя, повторите ошибку позже.')


# Начальная функция. Проверяет есть ли аккаунт или нет, регистрация
def start(update: Update, context: CallbackContext) -> None:
    global user_id, username, is_authorised
    print(update.message.from_user.id)
    print(update.message.from_user.username)
    update.message.reply_text('Добро пожаловать. Для начала пройдите авторизацию.')
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    if check_user(update=update, context=context, user_id=user_id):
        update.message.reply_text('У вас уже есть аккаунт. Вы можете продолжать')
        is_authorised = True
    else:
        registration_answer = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Да", callback_data='1'),
                InlineKeyboardButton("Нет", callback_data='2'),
            ],
        ])
        update.message.reply_text('У вас ещё нет аккаунта. Хотите зарегистрироваться', reply_markup=registration_answer)
        #     update.message.reply_text("Вы успешно зарегистрировались. Вы можете продолжать")


# Вывод информации об игре
def info(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Это игра')


# Вывод данных о пользователе(больше для дебага)
def profile(update: Update, context: CallbackContext):
    check_user(update=update, context=context, user_id=update.message.from_user.id)
    if is_authorised:
        update.message.reply_text(f'user_id: {user_id}\n'
                                  f'username: {username}')
    else:
        update.message.reply_text('Вы не авторизованы')


def main() -> None:
    updater = Updater("5278816766:AAFWnPxEguubVCXlGw9k8shgz_-0aroopq0")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("info", info))
    dispatcher.add_handler(CommandHandler("profile", profile))
    dispatcher.add_handler(CommandHandler("delete_account", delete_user))
    updater.dispatcher.add_handler(CallbackQueryHandler(add_user))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
