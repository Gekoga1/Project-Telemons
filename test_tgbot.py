import logging
import sqlite3

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Filters, MessageHandler

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
confirm = ''


# устанавливаем текущие данные пользователя
def set_user_data(user_id, name):
    global id, username
    id = user_id
    username = name


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


# обработка нажатий inline buttons
def check_query(update: Update, context: CallbackContext) -> None:
    global is_authorised, confirm
    query = update.callback_query
    if query.data == '1':
        print(1)
        add_user(query=query)
    elif query.data == '2':
        query.edit_message_text('Ну нет так нет.')
    elif query.data == '3':
        delete_user(query=query)
    elif query.data == '4':
        query.edit_message_text('Процесс удаления пользователя отменён')
    elif query.data == 'Yes':
        pass
    elif query.data == 'No':
        query.edit_message_text('Грустно :(')
    elif query.data == 'Confirm':
        confirm = True
        query.edit_message_text('Введите новое имя')
        change_name(update, context)
    elif query.data == 'Not confirm':
        confirm = False
        query.edit_message_text('ну не меняй')  # должен быть переход в главное меню
    elif query.data == 'nickname':
        query.edit_message_text('Введите свой ник')
        name = update.message.text
        print(101)
        set_name(name, query=query)
    elif query.data == 'tg name':
        name = query.from_user.username
        set_name(name, query=query)


# Предложение удалить пользователя
def delete_user_suggestion(update: Update, context: CallbackContext):
    delete_user_answer = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Да", callback_data='3'),
            InlineKeyboardButton("Нет", callback_data='4'),
        ],
    ])
    update.message.reply_text('Вы действительно хотите удалить свой профиль из базы данных?',
                              reply_markup=delete_user_answer)


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


def set_name(name, query):
    print(123)
    req = """INSERT INTO users VALUES(?, ?)"""
    CURSOR.execute(req, (id, name,))
    CONNECTION.commit()
    query.edit_message_text(f'Твоё имя в игре {name}\nТы всегда можешь его изменить, вызвав команду /profile')


# Начальная функция. Проверяет есть ли аккаунт или нет, регистрация
def start(update: Update, context: CallbackContext) -> None:
    global id, username, is_authorised
    print(update.message.from_user.id)
    print(update.message.from_user.username)
    update.message.reply_text('Добро пожаловать. Для начала пройдите авторизацию.')
    id = update.message.from_user.id
    # username = get_username(id)
    if check_user(update=update, context=context, id=id):
        update.message.reply_text('У вас уже есть аккаунт. Вы можете продолжать')
        is_authorised = True
    else:
        name_ques = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Да', callback_data='nickname'),
                InlineKeyboardButton('Нет', callback_data='tg name')
            ]
        ])
        update.message.reply_text('У вас ещё нет аккаунта, нужно его создать. Вы хотите ник?', reply_markup=name_ques)
        #     update.message.reply_text("Вы успешно зарегистрировались. Вы можете продолжать")


# Вывод информации об игре
def info(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Это игра')


# Вывод данных о пользователе(больше для дебага)
def profile(update: Update, context: CallbackContext):
    check_user(update=update, context=context, id=update.message.from_user.id)
    if is_authorised:
        update.message.reply_text(f'Ваши данные\n\nid: {id}\n'
                                  f'username: {username}')
    else:
        update.message.reply_text('Вы не авторизованы')
    confirm_changes(update, context)


def get_user_id(username):  # получение id пользователя
    req = """SELECT id FROM users WHERE username = ?"""
    res = CURSOR.execute(req, username).fetchone()
    print(*res, 'get_user_id')
    return res


def get_username(user_id):  # получение имени пользователя
    req = """SELECT username FROM users WHERE id = ?"""
    res = CURSOR.execute(req, user_id).fetchone()
    print(res, 'get_username')
    return res


def change_name(update: Update, context):  # изменение имени
    print(123)
    if confirm:
        print(12341)
        new_name = update.message.text
        print(update.message.text, 'after')
        print(0)
        req = """UPDATE users SET username = ? WHERE id = ?"""
        user_id = get_user_id('update.message.text')
        print(*user_id)
        CONNECTION.execute(req, (new_name, *user_id))
        print(2)
        CONNECTION.commit()
        print(3)
        update.message.reply_text('Имя успешно изменено')


def change_ability(update: Update, context: CallbackContext):
    pass


def confirm_changes(update: Update, context: CallbackContext):  # подтверждение изменений
    confirm_ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Да', callback_data='Confirm'),
            InlineKeyboardButton('Нет', callback_data='Not confirm')
        ]
    ])
    update.message.reply_text('Хотите изменить данные?', reply_markup=confirm_ques)


# Пример функционала игры
def show_game_example(update: Update, context: CallbackContext):
    update.message.reply_text(result1)
    update.message.reply_text(result2)
    update.message.reply_text(result3)
    update.message.reply_text(result4)


def confirm_fight(update: Update, context: CallbackContext):  # подтверждение, что пользователь хочет начать бой
    check_user(update=update, context=context, id=update.message.from_user.id)
    if is_authorised:
        confirm_answer = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Да', callback_data='Yes'),
                InlineKeyboardButton('Нет', callback_data='No')
            ]
        ])
        update.message.reply_text('Вы хотите начать бой?', reply_markup=confirm_answer)
    else:
        update.message.reply_text('Вы не авторизованы. Чтобы начать бой, нужно авторизоваться')


def main() -> None:
    updater = Updater("5278816766:AAFWnPxEguubVCXlGw9k8shgz_-0aroopq0")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("info", info))
    dispatcher.add_handler(CommandHandler("profile", profile))
    dispatcher.add_handler(CommandHandler("show", show_game_example))
    dispatcher.add_handler(CommandHandler("delete_account", delete_user_suggestion))
    dispatcher.add_handler(CommandHandler("fight", confirm_fight))
    dispatcher.add_handler(CommandHandler("change_ability", change_ability))

    dispatcher.add_handler(MessageHandler(Filters.text, check_query))
    dispatcher.add_handler(MessageHandler(Filters.text, change_name))
    updater.dispatcher.add_handler(CallbackQueryHandler(check_query))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
