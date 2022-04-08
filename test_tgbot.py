import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

from database_manager import User
from game_lib import result1, result2, result3, result4

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# id = 0
# username = ''
# is_authorised = False


# устанавливаем текущие данные пользователя
# def set_user_data(user_id, name):
#     global id, username
#     id = user_id
#     username = name


def get_authorised(update: Update, context: CallbackContext):
    id = update.effective_user.id
    return database_manager.check_is_authorised(id=id)


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


# def process_message(update: Update, context: CallbackContext):
#     """
#     Обработчик текстовых сообщений
#     """
#     # Нам нужно обрабатывать только ввод слова во время создания комнаты, остальное делается кнопками
#     if 'stage' not in context.chat_data or context.chat_data['stage'] != Stage.SELECT_WORD:
#         return
#
#     select_word(update, context)


# проверяем существует ли такой пользователь в базе
def check_user(update: Update, context: CallbackContext):
    try:
        id = update.effective_user.id
        return database_manager.check_user(id=id)
    except Exception as exception:
        print(exception)
        update.message.reply_text('Произошла ошибка при авторизации, повторите ошибку позже.')


# добавляем пользователя в бд
def add_user(update: Update, context: CallbackContext):
    query = update.callback_query
    try:
        id = update.effective_user.id
        username = update.effective_user.username
        database_manager.add_user(id=id, username=username)
        query.edit_message_text("Вы успешно зарегистрировались. Вы можете продолжать")
    except Exception as exception:
        print(exception)
        query.edit_message_text('Произошла ошибка при регистрации пользователя. Повторите ошибку позже.')


# удаляем пользователя из бд
def delete_user(update: Update, context: CallbackContext):
    query = update.callback_query
    try:
        id = update.effective_user.id
        if database_manager.delete_user(id=id):
            query.edit_message_text('Удаление прошло успешно')
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

    #     update.message.reply_text("Вы успешно зарегистрировались. Вы можете продолжать")


# Вывод информации об игре
def info(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Это игра')


# Вывод данных о пользователе(больше для дебага)
def profile(update: Update, context: CallbackContext):
    id = update.effective_user.id
    username = update.effective_user.username
    if get_authorised(update=update, context=context):
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


def game_settings(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Изменить команду", callback_data='change_team'),
            InlineKeyboardButton("Изменить свое имя в игре", callback_data='change_game_name'),
        ],
    ])
    update.message.reply_text('Что вы хотите сделать?', reply_markup=keyboard)


# Начальная функция. Проверяет есть ли аккаунт или нет, регистрация
def start(update: Update, context: CallbackContext) -> None:
    id = update.effective_user.id

    update.message.reply_text('Добро пожаловать. Для начала пройдите авторизацию.')
    if check_user(update=update, context=context):
        update.message.reply_text('У вас уже есть аккаунт. Вы можете продолжать')
        database_manager.is_authorised_abled(id=id)
    else:
        registration_answer = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Да", callback_data='registration_yes'),
                InlineKeyboardButton("Нет", callback_data='registration_no'),
            ],
        ])
        update.message.reply_text('У вас ещё нет аккаунта. Хотите зарегистрироваться', reply_markup=registration_answer)


def terminate(update: Update, context: CallbackContext):
    id = update.effective_user.id

    database_manager.connection.commit()
    database_manager.is_authorised_disabled(id=id)


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
    database_manager = User()
    main()
