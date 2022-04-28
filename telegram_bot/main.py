import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

from configure.configuraion import MONSTER_NUM, ABILITY_NUM, NOTHING, TEAM_NUM, COLLECTION_NUM, NICKNAME
from authorisation import *
from configure.secrets import API_TOKEN
from fighting import *
from game_logic.game_lib import Monster_Template
from monsters import *
from settings import *
from random import choices

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
        context.chat_data['waiting for'] = NICKNAME
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
        write_team_num(update, context)
    elif query.data == 'change monster':
        change_monster(update, context)
    elif query.data == 'monster info':
        monster_info(update, context)
    elif query.data == 'main menu':
        main_menu(update, context)
    elif query.data == 'change ability':
        print_ability_num(update, context)
    elif query.data == 'spylit':
        monster_class = Monster_Template(uid=1, lvl=5, shiny=choices([True, False], weights=[50, 50], k=1)[0])
        registration(update, context, monster_class)
    elif query.data == 'ice':
        pass
    elif query.data == 'grass':
        pass
    elif context.chat_data['waiting_for'] == COLLECTION_NUM:
        select_monster(update, context)
    else:
        query.edit_message_text('Я вас не понимаю, повторите попытку ввода.')


def process_message(update: Update, context: CallbackContext):  # обработчик текстовых сообщений
    if context.chat_data['waiting_for'] == MONSTER_NUM:
        get_monster_num(update, context)
    elif context.chat_data['waiting for'] == NICKNAME:
        write_nickname(update, context)
    elif context.chat_data['waiting_for'] == ABILITY_NUM:
        get_ability_num(update, context)
    elif context.chat_data['waiting_for'] == TEAM_NUM:
        get_team_num(update, context)
    elif context.chat_data['waiting_for'] == NOTHING:
        return


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


# Начальная функция. Проверяет есть ли аккаунт или нет, регистрация
def start(update: Update, context: CallbackContext) -> None:
    id = update.effective_user.id

    update.message.reply_text('Добро пожаловать. Для начала пройдите авторизацию.')
    if check_user(update=update, context=context):
        database_manager.is_authorised_abled(id=id)

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
    updater = Updater('5291017589:AAGK_BHLg3g2NwjDuGLnGJl9ZC9nRoBldsw')

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

