import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters

from Room import Room, Stage
from database_manager import User
from game_lib import result1, result2, result3, result4, Monster_Template
from secrets import API_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
rooms = {}

# основные состояния игрока при вводе
NOTHING = 'nothing'
MONSTER_NUM = 'monster_num'
ABILITY_NUM = 'ability_num'


def get_authorised(update: Update, context: CallbackContext):
    id = update.effective_user.id
    return database_manager.check_is_authorised(id=id)


# обработка нажатий inline buttons
def check_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.data == 'registration_yes':
        nickname_or_tgname(update, context)
    elif query.data == 'registration_no':
        query.edit_message_text('Ну нет так нет.')
    elif query.data == 'delete_yes':
        delete_user(update=update, context=context)
    elif query.data == 'change_game_name':
        propose_change_user_nickname(update=update, context=context, query=query)
    elif query.data == 'delete_no':
        query.edit_message_text('Процесс отменён')
    elif query.data == 'nickname':
        query.edit_message_text('Введите свой ник')
        write_nickname(update, context)
    elif query.data == 'tg_name':
        name_from_telegram(update, context)
    elif query.data == 'game_settings':
        game_settings(update=update, context=context)
    elif query.data == 'choose_type_fight':
        choose_type_fight(update=update, context=context)
    elif query.data == 'PVP':
        fight_PVP(update=update, context=context)
    elif query.data == 'join_room':
        join_room(update, context)
        context.chat_data['stage'] = Stage.SELECT_ROOM
        # нажата кнопка создать комнату
    elif query.data == 'create_room':
        create_room(update, context)
        context.chat_data['stage'] = Stage.SELECT_DIFFICULTY
    elif query.data in rooms.keys():
        select_room(update, context)
        context.chat_data['stage'] = Stage.PLAYING_GAME
    elif query.data == 'monsters':
        team_or_collection(update, context)
    elif query.data == 'team':
        team_info(update, context)
    elif query.data == 'collection':
        collection_info(update, context)
    elif query.data == 'change team':
        collection_info(update, context)
    elif query.data == 'no':
        main_menu(update, context)
    elif query.data == 'change monster':
        pass
    elif query.data == 'monster info':
        monster_info(update, context)
    elif query.data == 'main menu':
        main_menu(update, context)
    elif query.data == 'change ability':
        print_ability_num(update, context)
    elif query.data == 'spylit':
        monster_class = Monster_Template(1, shiny=False)
        registration(update, context, monster_class)
    elif query.data == 'ice':
        pass
    elif query.data == 'grass':
        pass
    else:
        update.message.reply_text('Я вас не понимаю, повторите попытку ввода.')


def process_message(update: Update, context: CallbackContext):  # обработчик текстовых сообщений
    if check_user(update, context) is False:
        write_nickname(update, context)
    elif check_user(update, context) is True:
        if context.chat_data['waiting_for'] == MONSTER_NUM:
            get_monster_num(update, context)
        elif context.chat_data['waiting_for'] == ABILITY_NUM:
            get_ability_num(update, context)
        elif context.chat_data['waiting_for'] == NOTHING:
            return


def nickname_or_tgname(update: Update, context: CallbackContext):  # выбор: имя из тг или придуманный ник
    query = update.callback_query
    name_ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Придумать ник', callback_data='nickname'),
            InlineKeyboardButton('Взять из телеграма', callback_data='tg_name')
        ]
    ])
    query.edit_message_text('Вы хотите придумать ник?', reply_markup=name_ques)


def choose_type_fight(update: Update, context: CallbackContext):
    query = update.callback_query
    fights = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('PVP', callback_data='PVP'),
        ],
        [
            InlineKeyboardButton('Вернуться в главное меню', callback_data='main menu')
        ]
    ])
    query.edit_message_text('Выберите тип сражения', reply_markup=fights)


def fight_PVP(update: Update, context: CallbackContext):
    if len(rooms):
        join_room(update=update, context=context)
    else:
        create_room(update=update, context=context)


def create_room(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = update.effective_user
    room = Room()
    room.author_id = user.id
    room.room_name = user.username
    context.chat_data['create_room'] = room

    room: Room = context.chat_data['create_room']

    rooms[room.room_name] = room
    del context.chat_data['create_room']
    context.chat_data['stage'] = Stage.HOSTING_GAME

    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Список игр', callback_data='join_room'),
        ]
    ])
    query.edit_message_text(text='Комната была создана, ждите пользователей', reply_markup=reply_markup)


def join_room(update: Update, context: CallbackContext) -> None:
    buttons = []
    for roomKey in rooms:
        buttons.append(InlineKeyboardButton(rooms[roomKey].room_name, callback_data=rooms[roomKey].room_name))
    keyboard = [buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    query.edit_message_text(text='Выберите комнату', reply_markup=reply_markup)


def select_room(update: Update, context: CallbackContext) -> None:
    context.chat_data['roomName'] = update.callback_query.data
    show_room(update=update, context=context)


def show_room(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.edit_message_text(text=f'Проверка проверка, это комната {context.chat_data["roomName"]}')


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


def check_add_monster(update: Update, context: CallbackContext, uid):  # проверка, есть ли новый монстр уже у игрока
    collection = database_manager.get_collection(update.effective_user.id).split(';')
    uid_in_coll = [database_manager.get_monster_uid(int(i)) for i in collection if i != '']
    if uid in uid_in_coll:
        return False
    else:
        return True


def change_team(update: Update, context: CallbackContext, team):  # изменение команды
    user_id = update.effective_user.id
    # final_team = f'{str(team[0])};{str(team[1])};{str(team[2])};{str(team[3])}'
    database_manager.change_user_team(user_id, team)


def change_collection(update: Update, context: CallbackContext, new_monster):
    user_id = update.effective_user.id
    old_collection = database_manager.get_collection(user_id)
    new_collection = old_collection + ';' + str(new_monster)
    database_manager.change_user_collection(user_id, new_collection)


def main_menu(update: Update, context: CallbackContext):  # главное меню
    context.chat_data['waiting_for'] = NOTHING
    id = update.effective_user.id
    if get_authorised(update=update, context=context):
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Выбор боёв", callback_data='choose_type_fight'),
                InlineKeyboardButton("Просмотр монстров", callback_data='monsters'),
            ],
            [
                InlineKeyboardButton('Настройки игры', callback_data='game_settings')
            ]
        ])
        nickname = database_manager.get_gamename(id)
        update.effective_user.send_message(f'Добро пожаловать в игру, {nickname}!\n\n'
                                           f'Чем хотите заняться?', reply_markup=reply_markup)
    else:
        update.message.reply_text('Вы не авторизованы, чтобы играть нужно авторизоваться.')


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


def get_collection_info(update: Update, context: CallbackContext):
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
    update.effective_user.send_message(text='Инфа о команде')
    change_ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Да', callback_data='change team'),
            InlineKeyboardButton('Нет', callback_data='main menu')
        ]
    ])
    update.callback_query.edit_message_text('Вы хотите изменить команду?', reply_markup=change_ques)


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


def delete_monsters_users(update: Update, context: CallbackContext):
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

    #     update.message.reply_text("Вы успешно зарегистрировались. Вы можете продолжать")


def propose_change_user_nickname(update: Update, context: CallbackContext, query):
    query.edit_message_text('Введите функцию формата\n/change_name <новый ник>')


def change_user_nickname(update: Update, context: CallbackContext):  # изменение ника
    id = update.effective_user.id
    message = update.message.text
    message_list = message.split()
    if len(message_list) <= 1:
        update.message.reply_text('Вы не ввели ник!')
    elif len(message_list) > 2:
        update.message.reply_text("Слишком много ников, введите только 1")
    else:
        nickname = message_list[1]
        if database_manager.change_user_nickname(nickname=nickname, id=id):
            update.message.reply_text("Ник изменён")
        else:
            update.message.reply_text("Ошибка при изменении ника, повторите попытку позже")


# Вывод информации об игре
def info(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Это игра')


# Вывод данных о пользователе(больше для дебага)
def profile(update: Update, context: CallbackContext):
    id = update.effective_user.id
    if get_authorised(update=update, context=context):
        update.message.reply_text(f'id: {id}\n'
                                  f'username: {database_manager.get_gamename(id)}')


# Пример функционала игры
def show_game_example(update: Update, context: CallbackContext):
    update.message.reply_text(result1)
    update.message.reply_text(result2)
    update.message.reply_text(result3)
    update.message.reply_text(result4)


def game_settings(update: Update, context: CallbackContext):  # настройки игры
    query = update.callback_query
    if query is not None:
        keyboard = InlineKeyboardMarkup([
            [

                InlineKeyboardButton("Изменить свое имя в игре", callback_data='change_game_name'),
            ],
        ])
        query.edit_message_text('Что вы хотите сделать?', reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup([
            [

                InlineKeyboardButton("Изменить свое имя в игре", callback_data='change_game_name'),
            ],
        ])
        update.message.reply_text('Что вы хотите сделать?', reply_markup=keyboard)


def full_registration(update: Update, context: CallbackContext):  # проверка на то, выбрал ли игрок первого монстра
    user_id = update.effective_user.id
    team = database_manager.get_team(user_id).split(';')
    amount_monsters = database_manager.get_amount_monsters()
    if team[0] == '' and amount_monsters == 0:
        return False
    else:
        return True


# Начальная функция. Проверяет есть ли аккаунт или нет, регистрация
def start(update: Update, context: CallbackContext) -> None:
    id = update.effective_user.id

    update.message.reply_text('Добро пожаловать. Для начала пройдите авторизацию.')
    if check_user(update=update, context=context):
        database_manager.is_authorised_abled(id=id)

        if not full_registration(update, context):
            update.message.reply_text('Вы ещё не закончили регистрацию')
            choose_fst_monster(update, context)
        else:
            update.message.reply_text('У вас уже есть аккаунт. Вы можете продолжать')
            main_menu(update, context)
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
    updater = Updater(API_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("info", info))
    dispatcher.add_handler(CommandHandler("profile", profile))
    dispatcher.add_handler(CommandHandler("show", show_game_example))
    dispatcher.add_handler(CommandHandler("delete_account", delete_user_suggestion))
    dispatcher.add_handler(CommandHandler("change_name", change_user_nickname))
    dispatcher.add_handler(CommandHandler("game_settings", game_settings))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))
    dispatcher.add_handler(CommandHandler("main_menu", main_menu))
    updater.dispatcher.add_handler(CallbackQueryHandler(check_query))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    database_manager = User()
    main()
