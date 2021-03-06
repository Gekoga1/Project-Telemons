from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

from authorisation import *
from configure.configuration import NICKNAME, SKILL_CHANGE
from configure.secrets import API_TOKEN
from fighting import *
from game_logic.game_lib import *
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
    id = update.effective_user.id
    query.answer()
    if query.data == 'registration_yes':
        nickname_or_tgname(update, context)
    elif query.data == 'registration_no':
        query.edit_message_text('Ну нет так нет.\n'
                                'Если надумаете, переходите по этой ссылке /start')
    elif query.data == 'delete_yes':
        delete_user(update=update, context=context)
    elif query.data == 'choose_fst_monster':
        choose_fst_monster(update, context)
    elif query.data == 'propose_spylit':
        show_spylit_information(update, context)
    elif query.data == 'propose_ice':
        show_ice_information(update, context)
    elif query.data == 'propose_grass':
        show_grass_information(update, context)
    elif query.data == 'spylit':
        monster_class = Spylit(lvl=5, shiny=choices([True, False], weights=[50, 50], k=1)[0])
        monster_class.generate_skills()
        registration(update, context, monster_class)
    elif query.data == 'ice':
        monster_class = Ailox(lvl=5, shiny=choices([True, False], weights=[50, 50], k=1)[0])
        monster_class.generate_skills()
        registration(update, context, monster_class)
    elif query.data == 'grass':
        monster_class = Wulvit(lvl=5, shiny=choices([True, False], weights=[50, 50], k=1)[0])
        monster_class.generate_skills()
        registration(update, context, monster_class)
    elif query.data == 'change_game_name':
        propose_change_user_nickname(update=update, context=context, query=query)
    elif query.data == 'delete_no':
        query.edit_message_text('Процесс отменён')
    elif query.data == 'main menu':
        main_menu(update, context)
    elif query.data == 'nickname':
        context.chat_data['waiting_for'] = NICKNAME
        query.edit_message_text('Введите свой ник')
        write_nickname(update, context)
    elif query.data == 'tg_name':
        name_from_telegram(update, context)
    elif query.data == 'delete from team':
        show_team_for_delete(update, context)
    elif query.data == 'game_settings':
        game_settings(update=update, context=context)
    elif query.data == 'choose_type_fight':
        choose_type_fight(update=update, context=context)
    elif query.data == 'PVP':
        fight_PVP(update=update, context=context)
    elif query.data == 'PVE':
        fighting_PVE(update, context)
    elif query.data == 'exit_fight':
        finishing_PvP(update, context, is_extra=True, room=None)
    elif query.data == 'exit_pve':
        finishing_PVE(update, context, id, extra=True)
    elif query.data == 'create_room':
        create_room(update, context)
    elif query.data == 'join_room':
        join_room(update, context)
        context.bot_data[id]['stage'] = Stage.SELECT_ROOM
    elif query.data == 'change monster':
        show_team_for_change(update, context)
    elif query.data == 'learn_skills':
        ask_skill_num(update, context)
    elif query.data == 'monster info':
        monster_info(update, context)
    elif query.data == 'show ability':
        show_abilities(update, context)
    elif query.data == 'monsters':
        team_or_collection(update, context)
    elif query.data == 'team':
        team_info(update, context)
    elif query.data == 'collection':
        collection_info(update, context)
    elif query.data == 'change team':
        write_team_num(update, context)
    elif query.data == 'want evolution':
        want_evolution(update, context)
    elif query.data == 'evolution':
        evolution(update, context)
    elif query.data.split(' ')[0] in ['Атака', 'Смена', 'Поймать'] and context.bot_data[id]['stage'] == Stage.PLAY_PVE:
        continue_fighting_PVE(update, context, text=query.data, id=id)
    elif query.data.split(' ')[0] in ['Атака', 'Смена'] and context.bot_data[id]['stage'] == Stage.PLAY_GAME:
        main_fight(update=update, context=context, text=query.data)
    elif query.data in [i.__class__.__name__ for i in teams[id]] and context.bot_data[id][
        'stage'] == Stage.CHANGE_MONSTER:
        change_monster_fight(update, context, monster=query.data, player_team=id)
    elif context.chat_data['waiting_for'] == DELETE_FROM_TEAM:
        select_monster_for_delete(update, context)
    elif context.chat_data['waiting_for'] == COLLECTION_NUM:
        select_monster(update, context)
    elif context.chat_data['waiting_for'] == COLLECTION_TEAM:
        select_monster_in_team(update, context)
    elif context.chat_data['waiting_for'] == SKILL_CHANGE:
        select_skill_for_change(update, context)
    elif context.chat_data['waiting_for'] == EVOLUTION:
        select_monster_evolution(update, context)
    else:
        query.edit_message_text('Я вас не понимаю, повторите попытку ввода.')


def process_message(update: Update, context: CallbackContext):  # обработчик текстовых сообщений
    if context.chat_data['waiting_for'] == MONSTER_NUM:
        get_monster_num(update, context)
    elif context.chat_data['waiting_for'] == NICKNAME:
        write_nickname(update, context)
    elif context.chat_data['waiting_for'] == COLLECTION_TEAM:
        get_collection_team_num(update, context)
    elif context.chat_data['waiting_for'] == ABILITY_NUM:
        get_skill_num(update, context)
    elif context.chat_data['waiting_for'] == TEAM_NUM:
        get_team_num(update, context)

    elif context.chat_data['waiting_for'] == NOTHING:
        return


def main_menu(update: Update, context: CallbackContext):  # главное меню
    id = update.effective_user.id
    if id not in context.bot_data:
        add_bot_data(update=update, context=context, id=id)
    try:
        if context.bot_data[id]['stage'] == Stage.PLAY_GAME or context.bot_data[id]['stage'] == Stage.PLAY_PVE:
            update.message.reply_text(text='Ты сейчас играешь, нельзя вернуться в меня до окончания матча')
        else:
            if get_authorised(update=update, context=context):
                teams[id] = pars_team(database_manager.get_team(user_id=id))
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
            teams[id] = pars_team(database_manager.get_team(user_id=id))
            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Выбор боёв", callback_data='choose_type_fight'),
                    InlineKeyboardButton("Просмотр монстров", callback_data='monsters')
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


def add_bot_data(update: Update, context: CallbackContext, id):
    context.bot_data[id] = {}


def propose_change_user_nickname(update: Update, context: CallbackContext, query):
    query.edit_message_text('Введите функцию формата\n/change_name <новый ник>')


def info(update: Update, context: CallbackContext) -> None:
    update.effective_user.send_message('Приветствуем Вас в нашей игре!\n\nПравила:\n1) Вы являетесь тренером монстров\n'
                                       '2) Главная цель игры - собрать всех монстров и стать самым сильным тренером\n'
                                       '3) Каждый монстрик имеет свой тип, а иногда даже два\n'
                                       '4) Вы можете выбрать 4 основных монстра в вашу команду и с ними проводить бои'
                                       ' против случайных монстров (PvE) или против других игроков-тренеров (PvP)\n'
                                       '5) Во время боя Вам нужно сначала либо выбрать следующую атаку, '
                                       'либо заменить активного монстра, и так пока одна из команд '
                                       'не будет полностью повержена\n6) В PvE Вы можете приручить нового монстра, '
                                       'как только у него останется немного hp\n7) НО! Нельзя приручить побеждённого'
                                       ' монстрика\n8) После боя у всей команды повышается уровень, опыт. '
                                       'Если монстр достигнет определённого уровня и опыта, он может эволюциониовать'
                                       ' и получить новые способности\n\nЖелаем удачи!\n\nЧтобы вернуться'
                                       ' в главное меню вызовите команду /main_menu')


# Вывод данных о пользователе(больше для дебага)
def profile(update: Update, context: CallbackContext):
    id = update.effective_user.id
    if get_authorised(update=update, context=context):
        update.message.reply_text(f'id: {id}\n'
                                  f'username: {database_manager.get_gamename(id)}')


def pars_team(team):
    new_team = []
    try:
        for monster_id in team.split(';'):
            data = database_manager.get_monster_info(monster_id)
            exec(f'new_team.append({data[1]}(lvl={data[2]}, exp={data[3]}, shiny={data[4]}))')
            new_team[-1].deconvert_skills(data[5])
    except Exception as ex:
        print(ex)
    return new_team


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
    updater = Updater(API_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("info", info))
    dispatcher.add_handler(CommandHandler("profile", profile))
    dispatcher.add_handler(CommandHandler("delete_account", delete_user_suggestion))
    dispatcher.add_handler(CommandHandler("change_name", change_user_nickname))
    dispatcher.add_handler(CommandHandler("game_settings", game_settings))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))
    dispatcher.add_handler(CommandHandler("main_menu", main_menu))
    dispatcher.add_handler(CommandHandler("evolution", team_for_evolution))
    updater.dispatcher.add_handler(CallbackQueryHandler(check_query))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
