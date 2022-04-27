from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from configure.configuraion import database_manager
from monsters import check_add_monster, change_team, change_collection


def write_nickname(update: Update, context: CallbackContext):  # собственный ник
    name = update.message.text
    add_user(update, context, name)
    choose_fst_monster(update, context)


def name_from_telegram(update: Update, context: CallbackContext):  # имя из тг
    name = update.effective_user.username
    add_user(update, context, name)
    choose_fst_monster(update, context)


def choose_fst_monster(update: Update, context: CallbackContext):  # выбор стартового монстра
    ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Каменный паук', callback_data='spylit'),
            InlineKeyboardButton('Ледяной лис', callback_data='ice'),
            InlineKeyboardButton('Травяной', callback_data='grass')
        ]
    ])
    update.effective_user.send_message(text='Выберите своего первого монстра', reply_markup=ques)


def registration(update: Update, context: CallbackContext, monster_class): # завершение регистрации
    user_id = update.effective_user.id
    name = database_manager.get_gamename(user_id)
    amount_monsters = database_manager.get_amount_monsters() + 1
    if check_add_monster(update, context, monster_class.uid):
        database_manager.add_monster(id=amount_monsters, uid=monster_class.uid, name=monster_class.name,
                                 level=1, exp=0, shiny=False)
        team = str(amount_monsters) + ';'
        change_team(update, context, team)
        change_collection(update, context, amount_monsters)
        update.effective_user.send_message(f"Вы успешно зарегистрировались.\n\nВаше имя в игре {name}\n"
                                        f"Вы всегда можете его изменить, вызвав команду /game_settings\n\n"
                                        f"Чтобы выйти в главное меню, введите команду /main_menu")
    else:
        print('this monster is already in team and in collection')


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
        if delete_monsters_users(update, context) and database_manager.delete_user(id=id):
            query.edit_message_text('Удаление прошло успешно')
    except Exception as exception:
        print(exception)
        query.edit_message_text('Произошла ошибка при удалении пользователя, повторите попытку позже.')


def delete_monsters_users(update: Update, context: CallbackContext):  # удаление монстров пользователя
    try:
        user_id = update.effective_user.id
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
