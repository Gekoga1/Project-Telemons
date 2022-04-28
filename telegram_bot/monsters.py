from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from configure.configuraion import database_manager, MONSTER_NUM, NOTHING, ABILITY_NUM, TEAM_NUM, COLLECTION_NUM
from main import main_menu


def team_or_collection(update: Update, context: CallbackContext):  # выбор, что смотреть: коллекция или команда
    query = update.callback_query
    ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Просмотр коллекции', callback_data='collection'),
            InlineKeyboardButton('Просмотр команды', callback_data='team')
        ]
    ])
    query.edit_message_text('Что Вы хотите сделать?', reply_markup=ques)


def collection_info(update: Update, context: CallbackContext):  # вывод всей коллекции монстров
    collection = get_collection_info(update, context)
    msg = 'Ваши монстры:\n\n'
    for i in range(len(collection)):
        msg += f'{i + 1}) {collection[i][1]}\n'
    update.effective_user.send_message(text=msg)
    monster_choice(update, context)


def get_collection_info(update: Update, context: CallbackContext):  # получение информации о монстрах из коллекции
    user_id = update.effective_user.id
    monsters_id = database_manager.get_collection(user_id).split(';')
    collection = [database_manager.get_monster_info(int(i)) for i in monsters_id if i != '']
    return collection


def monster_choice(update: Update, context: CallbackContext):  # спрашивает номер монстра
    context.chat_data['waiting_for'] = MONSTER_NUM
    update.effective_user.send_message(text='Введите номер монстра')
    get_monster_num(update, context)


def get_monster_num(update: Update, context: CallbackContext):  # получает номер монстра
    try:
        monster_num = int(update.message.text)
        context.chat_data['monster_num'] = monster_num
        ques = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Заменить монстра', callback_data='change monster'),
                InlineKeyboardButton('Посмотреть характеристики', callback_data='monster info')
            ],
            [
                InlineKeyboardButton('Вернуться в главное меню', callback_data='main menu')
            ]
        ])
        update.message.reply_text(f'Вы выбрали монстра под номером {str(monster_num)} \n'
                                  f'Что Вы хотите сделать?', reply_markup=ques)
    except Exception as ex:
        print(ex)
        update.message.reply_text('Вы ввели не число, попробуйте ещё раз.')


def monster_info(update: Update, context: CallbackContext):  # информация о монстре
    collection = get_collection_info(update, context)
    monster_num = context.chat_data['monster_num']
    text = f'Монстр: {collection[monster_num - 1][1]}\nУровень: {collection[monster_num - 1][2]}\n' \
           f'Опыт: {collection[monster_num - 1][3]}'
    update.effective_user.send_message(text=text)
    monster_activity(update, context)


def monster_activity(update: Update, context: CallbackContext):  # предлагает действия с монстром
    ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Переименовать', callback_data='change monster name'),
            InlineKeyboardButton('Заменить способность', callback_data='change ability')
        ],
        [
            InlineKeyboardButton('Эволюционировать', callback_data='evolution'),
            InlineKeyboardButton('Заменить монстра', callback_data='change monster')
        ],
        [
            InlineKeyboardButton('Вернуться в главное меню', callback_data='main menu')
        ]
    ])
    update.effective_user.send_message(text='Что вы хотите сделать?', reply_markup=ques)


def print_ability_num(update: Update, context: CallbackContext):  # спрашивает номер способности
    update.effective_user.send_message(text='Введите номер способности, которую хотите заменить')
    context.chat_data['waiting_for'] = ABILITY_NUM
    get_ability_num(update, context)


def get_ability_num(update: Update, context: CallbackContext):  # получает номер способности от пользователя
    try:
        ability_num = int(update.message.text)
        show_ability_list(update, context, ability_num)
    except Exception as ex:
        print(ex)
        update.message.reply_text('Вы ввели не число, попробуйте ещё раз')


def show_ability_list(update: Update, context: CallbackContext,
                      ability_num):  # показывает список доступных способностей
    print(ability_num)
    update.message.reply_text('Здесь выводится список доступных способностей')


def team_info(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    monsters_id = database_manager.get_team(user_id).split(';')
    team = [database_manager.get_monster_info(int(i)) for i in monsters_id if i != '']
    text = 'Ваша команда:\n\n'
    for i in range(len(team)):
        text += f'{i + 1}) {team[i][1]}, уровень: {team[i][2]}, опыт: {team[i][3]}\n'

    update.effective_user.send_message(text=text)
    team_activity(update, context)


def team_activity(update: Update, context: CallbackContext):  # информация о команде
    change_ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Да', callback_data='change team'),
            InlineKeyboardButton('Нет', callback_data='main menu')
        ]
    ])
    update.callback_query.edit_message_text('Вы хотите изменить команду?', reply_markup=change_ques)


def change_team(update: Update, context: CallbackContext, team):  # изменение команды
    user_id = update.effective_user.id
    database_manager.change_user_team(user_id, team)
    update.effective_message.reply_text('Команда успешно изменена')


def change_collection(update: Update, context: CallbackContext, new_monster, send_back=False):  # добавление монстра в коллекцию игрока
    user_id = update.effective_user.id
    old_collection = database_manager.get_collection(user_id)
    new_collection = old_collection + ';' + str(new_monster)
    database_manager.change_user_collection(user_id, new_collection)


def check_add_monster(update: Update, context: CallbackContext, uid):  # проверка, есть ли новый монстр уже у игрока
    collection = database_manager.get_collection(update.effective_user.id).split(';')
    uid_in_coll = [database_manager.get_monster_uid(int(i)) for i in collection if i != '']
    if uid in uid_in_coll:
        return False
    else:
        return True


def write_team_num(update: Update, context: CallbackContext):
    context.chat_data['waiting_for'] = TEAM_NUM
    update.effective_user.send_message('Введите номер монстра в команде')
    get_team_num(update, context)


def get_team_num(update: Update, context: CallbackContext):
    try:
        team_amount = len(database_manager.get_team(update.effective_user.id).split(';'))
        team_num = int(update.message.text)
        if team_num > team_amount or team_num <= 0:
            raise Exception
        else:
            context.chat_data['team_num'] = team_num
            show_collection(update, context)
    except Exception as ex:
        print(ex)
        update.message.reply_text('Вы ввели не число или ввели номер, которого нет, попробуйте ещё раз')


def show_collection(update: Update, context: CallbackContext):
    context.chat_data['waiting_for'] = COLLECTION_NUM
    context.chat_data['collection_num'] = 0
    collection = get_collection_info(update, context)

    btns = []
    temp = []
    keyboard = []
    for i in range(len(collection) + 1):
        if i == len(collection):
            btns.append(temp)
        elif len(temp) <= 8:
            temp.append(i + 1)
        else:
            btns.append(temp)
            temp = []
    for group in btns:
        btns_in_row = []
        for num in group:
            btns_in_row.append(InlineKeyboardButton(str(num), callback_data=str(collection[num - 1][0])))
        keyboard.append(btns_in_row)

    text = 'Ваши монстры:\n\n'
    for i in range(len(collection)):
        text += f'{i + 1}. {collection[i][1]}\n'
    update.effective_user.send_message(text=text, reply_markup=InlineKeyboardMarkup(keyboard))


def select_monster(update: Update, context: CallbackContext):
    num = update.callback_query.data
    context.chat_data['collection_num'] = num
    context.chat_data['waiting for'] = NOTHING
    change_monster(update, context)


def change_monster(update: Update, context: CallbackContext):
    team = database_manager.get_team(update.effective_user.id).split(';')
    team_num = context.chat_data['team_num']
    coll_num = context.chat_data['collection_num']
    new_team = ''
    for i in range(len(team)):
        if i == team_num - 1:
            new_team += f'{str(coll_num)};'
        elif team[i] != '':
            new_team += f'{team[i]};'
    change_team(update, context, new_team)
    text = f'Новая команда:\n\n'
    monsters_id = database_manager.get_team(update.effective_user.id).split(';')
    new_team = [database_manager.get_monster_info(int(i)) for i in monsters_id if i != '']
    for i in range(len(new_team)):
        text += f'{i + 1}) {new_team[i][1]}, уровень: {new_team[i][2]}, опыт: {new_team[i][3]}\n'
    update.effective_user.send_message(text)
    next_activity(update, context)


def next_activity(update: Update, context: CallbackContext):
    ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Изменить команду ещё раз', callback_data='team'),
            InlineKeyboardButton('Вернуться в главное меню', callback_data='main menu')
        ]
    ])
    update.effective_user.send_message(text='Что Вы хотите сделать?', reply_markup=ques)
