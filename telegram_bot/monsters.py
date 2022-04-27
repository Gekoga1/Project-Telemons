from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from configure.configuraion import database_manager, MONSTER_NUM, NOTHING, ABILITY_NUM


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
        msg += f'{i + 1}. {collection[i][0]}, уровень: {str(collection[i][1])}, опыт: {str(collection[i][2])}\n'
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
    update.effective_user.send_message(text='Здесь выводится инфа о монстре')
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


def team_info(update: Update, context: CallbackContext):  # информация о команде
    change_ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Да', callback_data='change team'),
            InlineKeyboardButton('Нет', callback_data='main menu')
        ]
    ])
    update.callback_query.edit_message_text('Вы хотите изменить команду?', reply_markup=change_ques)


def change_team(update: Update, context: CallbackContext, team):  # изменение команды
    user_id = update.effective_user.id
    # final_team = f'{str(team[0])};{str(team[1])};{str(team[2])};{str(team[3])}'
    database_manager.change_user_team(user_id, team)


def change_collection(update: Update, context: CallbackContext, new_monster):  # добавление монстра в коллекцию игрока
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
