from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from configure.configuration import database_manager
from configure.monsters_information import spylit, ice, grass


def write_nickname(update: Update, context: CallbackContext):  # собственный ник
    name = update.message.text
    context.chat_data['name'] = name
    choose_fst_monster(update, context)


def name_from_telegram(update: Update, context: CallbackContext):  # имя из тг
    name = update.effective_user.username
    context.chat_data['name'] = name
    choose_fst_monster(update, context)


def choose_fst_monster(update: Update, context: CallbackContext):  # выбор стартового монстра
    ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Spylit', callback_data='propose_spylit'),
        ],
        [
            InlineKeyboardButton('Ailox', callback_data='propose_ice')
        ],
        [
            InlineKeyboardButton('Wulvit', callback_data='propose_grass')
        ]
    ])
    update.effective_user.send_message(text='Выберите своего первого монстра', reply_markup=ques)


def show_spylit_information(update: Update, context: CallbackContext):
    ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Выбрать Каменного паука', callback_data='spylit'),
        ],
        [
            InlineKeyboardButton('Вернуться к выбору', callback_data='choose_fst_monster')
        ]
    ])
    photo = open('../resources/monster_images/Spylit.png', 'rb')
    update.effective_user.send_photo(photo=photo, caption=spylit, reply_markup=ques)


def show_ice_information(update: Update, context: CallbackContext):
    ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Выбрать Ailox', callback_data='ice'),
        ],
        [
            InlineKeyboardButton('Вернуться к выбору', callback_data='choose_fst_monster')
        ]
    ])
    photo = open('../resources/monster_images/Ailox.png', 'rb')
    update.effective_user.send_photo(photo=photo, caption=ice, reply_markup=ques)


def show_grass_information(update: Update, context: CallbackContext):
    ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Выбрать Wulvit', callback_data='grass'),
        ],
        [
            InlineKeyboardButton('Вернуться к выбору', callback_data='choose_fst_monster')
        ]
    ])
    photo = open('../resources/monster_images/Wulvit.png', 'rb')
    update.effective_user.send_photo(photo=photo, caption=grass, reply_markup=ques)


def create_fst_team(update: Update, context: CallbackContext, team):  # добавление стартового монстра в команду
    user_id = update.effective_user.id
    database_manager.change_user_team(user_id, team)


def create_fst_collection(update: Update, context: CallbackContext, collection):
    user_id = update.effective_user.id
    collection = f'{str(collection)};'
    database_manager.change_user_collection(user_id, collection)


def registration(update: Update, context: CallbackContext, monster_class): # завершение регистрации
    try:
        user_id = update.effective_user.id
        name = context.chat_data['name']
        monsters_ids = database_manager.get_monsters_ids()
        if len(monsters_ids) == 0:
            monster_id = 1
            team = '1'
        else:
            monster_id = int(monsters_ids[-1][0]) + 1
            team = f'{str(monster_id)}'
        database_manager.add_monster(id=monster_id, name=monster_class.__class__.__name__,
                                     level=monster_class.lvl, exp=monster_class.exp, shiny=monster_class.shiny,
                                     skills=monster_class.convert_skills())
        create_fst_team(update, context, team)
        add_user(update, context, name, team)
        update.effective_user.send_message(f"Вы успешно зарегистрировались.\n\nВаше имя в игре {name}\n"
                                       f"Вы всегда можете его изменить, вызвав команду /game_settings\n\n"
                                       f"Чтобы выйти в главное меню, введите команду /main_menu\n"
                                           f"Ознакомиться в правилами можно по команде /info")
    except Exception as ex:
        print(ex)
        update.effective_user.send_message('Произошла ошибка при регистрации, попробуйте ещё раз')


# проверяем существует ли такой пользователь в базе
def check_user(update: Update, context: CallbackContext):
    try:
        id = update.effective_user.id
        return database_manager.check_user(id=id)
    except Exception as exception:
        print(exception)
        update.message.reply_text('Произошла ошибка при авторизации, повторите попытку позже.')


# добавляем пользователя в бд
def add_user(update: Update, context: CallbackContext, nickname, team):
    # query = update.callback_query
    try:
        id = update.effective_user.id
        username = update.effective_user.username
        if username is None:
            username = update.effective_user.name
        database_manager.add_user(id=id, username=username, game_name=nickname, team=team)
    except Exception as exception:
        print(exception)
        update.message.reply_text('Произошла ошибка при регистрации пользователя. Повторите попытку позже.')


# удаляем пользователя из бд
def delete_user(update: Update, context: CallbackContext):
    query = update.callback_query
    try:
        id = update.effective_user.id
        if delete_monsters_users(update, context) and database_manager.delete_user(id=id):
            query.edit_message_text('Удаление прошло успешно')
    except Exception as exception:
        print(exception)
        query.edit_message_text('Произошла ошибка при удалении пользователя, повторите попытку позже.')


def delete_monsters_users(update: Update, context: CallbackContext):  # удаление монстров пользователя
    try:
        user_id = update.effective_user.id
        collection = database_manager.get_collection(user_id).split(';')
        for monster_id in collection:
            if monster_id != '':
                database_manager.delete_monster(int(monster_id))
        team = database_manager.get_team(user_id).split(';')
        for monster_id in team:
            if monster_id != '':
                database_manager.delete_monster(int(monster_id))
        return True
    except Exception as ex:
        print(ex)
        return False


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
