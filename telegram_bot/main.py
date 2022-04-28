from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

from authorisation import *
from configure.secrets import API_TOKEN
from fighting import *
# from game_logic.game_lib import result1, result2, result3, result4
from monsters import *
from settings import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


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
        query.edit_message_text('Ну нет так нет.\n'
                                'Если надумаете, переходите по этой ссылке /start')
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
    # elif query.data in rooms.keys():
    #     select_room(update, context)
    #     context.chat_data['stage'] = Stage.PLAYING_GAME

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
    elif query.data in teams[update.effective_user.id] and context.chat_data['stage'] == Stage.CHANGE_MONSTER:
        change_monster(update, context, query.data, update.effective_user.id)
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
    if 'stage' in context.chat_data and context.chat_data['stage'] == Stage.PLAY_GAME:
        main_fight(update=update, context=context)
    elif check_user(update, context) is False:
        write_nickname(update, context)
    elif check_user(update, context) is True:
        if context.chat_data['waiting_for'] == MONSTER_NUM:
            get_monster_num(update, context)
        elif context.chat_data['waiting_for'] == ABILITY_NUM:
            get_ability_num(update, context)
        elif context.chat_data['waiting_for'] == NOTHING:
            return


# def nickname_or_tgname(update: Update, context: CallbackContext):  # выбор: имя из тг или придуманный ник
#     query = update.callback_query
#     name_ques = InlineKeyboardMarkup([
#         [
#             InlineKeyboardButton('Придумать ник', callback_data='nickname'),
#             InlineKeyboardButton('Взять из телеграма', callback_data='tg_name')
#         ]
#     ])
#     query.edit_message_text('Вы хотите придумать ник?', reply_markup=name_ques)
#
#
# def choose_type_fight(update: Update, context: CallbackContext):
#     query = update.callback_query
#     fights = InlineKeyboardMarkup([
#         [
#             InlineKeyboardButton('PVP', callback_data='PVP'),
#         ],
#         [
#             InlineKeyboardButton('Вернуться в главное меню', callback_data='main menu')
#         ]
#     ])
#     query.edit_message_text('Выберите тип сражения', reply_markup=fights)
#
#
# def fight_PVP(update: Update, context: CallbackContext):
#     if len(rooms):
#         join_room(update=update, context=context)
#     else:
#         create_room(update=update, context=context)
#
#
# def create_room(update: Update, context: CallbackContext) -> None:
#     query = update.callback_query
#     user = update.effective_user
#     room = Room()
#     room.author_id = user.id
#     room.room_name = user.username
#     context.chat_data['create_room'] = room
#
#     room: Room = context.chat_data['create_room']
#
#     rooms[room.room_name] = room
#     del context.chat_data['create_room']
#     context.chat_data['stage'] = Stage.HOSTING_GAME
#     room.count_players = 0
#     room.player_list = []
#
#     query.edit_message_text(
#         text='Подходящих комнат не нашлось, поэтому комната была создана.\nВы уже находитесь в ней, ждите пользователей')
#
#     context.chat_data['roomName'] = user.username
#     room.player_list.append(update.effective_message.chat_id)
#     room.count_players += 1
#     context.chat_data['stage'] = Stage.PLAY_GAME
#
#
# def join_room(update: Update, context: CallbackContext) -> None:
#     buttons = []
#     for roomKey in rooms:
#         buttons.append(InlineKeyboardButton(rooms[roomKey].room_name, callback_data=rooms[roomKey].room_name))
#     keyboard = [buttons]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     query = update.callback_query
#     query.edit_message_text(text='Выберите комнату', reply_markup=reply_markup)
#
#
# def select_room(update: Update, context: CallbackContext) -> None:
#     context.chat_data['roomName'] = update.callback_query.data
#     room_name = context.chat_data['roomName']
#     room = rooms[room_name]
#     if room.count_players <= 2:
#         show_room(update=update, context=context, room=room)
#     else:
#         query = update.callback_query
#         query.edit_message_text('Комната занята, повторите попытку')
#
#
# def show_room(update: Update, context: CallbackContext, room) -> None:
#     query = update.callback_query
#     room.player_list.append(update.effective_message.chat_id)
#     room.count_players += 1
#     context.chat_data['stage'] = Stage.PLAY_GAME
#     query.edit_message_text(text=f'Проверка проверка, это комната {room.room_name}\n')
#     if room.count_players == 2:
#         test_game(update=update, context=context, room=room)
#
#
# def test_game(update: Update, context: CallbackContext, room) -> None:
#     first_player = random.choice(room.player_list)
#     update.effective_user.send_message(text='Напишите слово своему другу на проводе')
#     # text = update.message.text
#     # if text == 'hello':
#     #     room_name = context.chat_data['roomName']
#     #     context.chat_data['stage'] = Stage.LOBBY
#     #     update.message.reply_text('УРА! Вы угадали это слово')
#     #     del rooms[room_name]
#     #     main_menu(update, context)
#     #     print(rooms)
#     # else:
#     #     update.message.reply_text(text='Вы не угадали слово')
#
#
# def send_message_opponent(update: Update, context: CallbackContext) -> None:
#     text = update.message.text
#     room_name = context.chat_data['roomName']
#
#     room = rooms[room_name]
#     chat_id = update.effective_message.chat_id
#     opponent_name = ''
#     for i in room.player_list:
#         if i != chat_id:
#             opponent_name = i
#     update.message.bot.send_message(chat_id=opponent_name, text=f'Вам пришло сообщение: {text}')


# def process_message(update: Update, context: CallbackContext):
#     """
#     Обработчик текстовых сообщений
#     """
#     pass
# Нам нужно обрабатывать только ввод слова во время создания комнаты, остальное делается кнопками

#
#
# def nickname_settings(update: Update, context: CallbackContext):  # собственный ник
#     name = update.message.text
#     add_user(update, context, name)
#     database_manager.is_authorised_abled(update.effective_user.id)
#     update.message.reply_text(f"Вы успешно зарегистрировались.\n\nВаше имя в игре {name}\n"
#                               f"Вы всегда можете его изменить, вызвав команду /game_settings\n\n"
#                               f"Чтобы выйти в главное меню, введите команду /main_menu")
#
#
# def registration_success(update: Update, context: CallbackContext):  # имя из тг
#     query = update.callback_query
#     name = update.effective_user.name
#     add_user(update, context, name)
#     database_manager.is_authorised_abled(update.effective_user.id)
#     query.edit_message_text(f"Вы успешно зарегистрировались.\n\nВаше имя в игре {name}\n"
#                             f"Вы всегда можете его изменить, вызвав команду /game_settings\n\n"
#                             f"Чтобы выйти в главное меню, введите команду /main_menu")
#
#
# def main_menu(update: Update, context: CallbackContext):  # главное меню
#     id = update.effective_user.id
#     query = update.callback_query
#     if check_user(update, context) is False:
#         write_nickname(update, context)
#     elif check_user(update, context) is True:
#         if context.chat_data['waiting_for'] == MONSTER_NUM:
#             get_monster_num(update, context)
#         elif context.chat_data['waiting_for'] == ABILITY_NUM:
#             get_ability_num(update, context)
#         elif context.chat_data['waiting_for'] == NOTHING:
#             return


def main_menu(update: Update, context: CallbackContext):  # главное меню
    context.chat_data['waiting_for'] = NOTHING
    id = update.effective_user.id
    try:
        if context.chat_data['stage'] == Stage.PLAY_GAME:
            update.message.reply_text(text='Ты сейчас играешь, нельзя вернуться в меня до окончания матча')
        else:
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
    except Exception as exception:
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


def propose_change_user_nickname(update: Update, context: CallbackContext, query):
    query.edit_message_text('Введите функцию формата\n/change_name <новый ник>')


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
    pass


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
    main()
