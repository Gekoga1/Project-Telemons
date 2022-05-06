from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from configure.configuration import database_manager, MONSTER_NUM, NOTHING, ABILITY_NUM, TEAM_NUM, COLLECTION_NUM, \
    COLLECTION_TEAM, DELETE_FROM_TEAM, EVOLUTION
from game_logic.game_lib import Spylit, Spylish, Ailox, Ailoprex, Wulvit, Wullies, Spyland, Ailopix, Wulkiss
from main import main_menu


def team_or_collection(update: Update, context: CallbackContext):  # выбор, что смотреть: коллекция или команда
    update.effective_message.delete()
    ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Просмотр коллекции', callback_data='collection'),
            InlineKeyboardButton('Просмотр команды', callback_data='team')
        ]
    ])
    update.effective_user.send_message('Что Вы хотите сделать?', reply_markup=ques)


def collection_info(update: Update, context: CallbackContext):  # вывод всей коллекции монстров
    update.effective_message.delete()
    collection = get_collection_info(update, context)
    msg = 'Ваши монстры:\n\n'
    if len(collection) == 0:
        update.effective_user.send_message('У Вас ещё нет монстров в коллекции, сыграйте в PVE бой, '
                                           'чтобы получить нового монстра')
        main_menu(update, context)
    else:
        for i in range(len(collection)):
            if collection[i][4]:
                msg += f'{i + 1}) 🌟{collection[i][1]}\n'
            else:
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
        user_id = update.effective_user.id
        collection = database_manager.get_collection(user_id).split(';')
        coll_amount = len(collection)
        monster_num = int(update.message.text)
        if monster_num > coll_amount or monster_num <= 0:  # проверка на правильность номера
            raise Exception
        else:
            context.chat_data['monster_num'] = monster_num
            context.chat_data['collection_num'] = database_manager.get_collection(user_id).split(';')[monster_num - 1]
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
        update.message.reply_text('Вы ввели не число или ввели номер, которого нет, попробуйте ещё раз')


def monster_info(update: Update, context: CallbackContext):  # информация о монстре
    update.effective_message.delete()
    collection = get_collection_info(update, context)
    monster_num = context.chat_data['monster_num']
    if collection[monster_num - 1][4]:
        text = f'Монстр: 🌟{collection[monster_num - 1][1]}\nУровень: {collection[monster_num - 1][2]}\n' \
               f'Опыт: {collection[monster_num - 1][3]}\nСпособности: {", ".join(collection[monster_num - 1][-1].split(";"))}'
    else:
        text = f'Монстр: {collection[monster_num - 1][1]}\nУровень: {collection[monster_num - 1][2]}\n' \
               f'Опыт: {collection[monster_num - 1][3]}\nСпособности: {", ".join(collection[monster_num - 1][-1].split(";"))}'
    update.effective_user.send_message(text=text)
    monster_activity(update, context)


def monster_activity(update: Update, context: CallbackContext):  # предлагает действия с монстром
    ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Эволюционировать', callback_data='want evolution'),
            InlineKeyboardButton('Заменить монстра', callback_data='change monster')
        ],
        [
            InlineKeyboardButton('Вернуться в главное меню', callback_data='main menu'),
            InlineKeyboardButton('Посмотреть способности', callback_data='show ability')
        ]
    ])
    update.effective_user.send_message(text='Что вы хотите сделать?', reply_markup=ques)


def team_for_evolution(update: Update, context: CallbackContext):
    context.chat_data['waiting_for'] = EVOLUTION
    team_info(update, context, only_show=True)

    team = database_manager.get_team(update.effective_user.id).split(';')
    btns = []  # создание кнопок
    temp = []
    for i in range(len(team)):
        temp.append(InlineKeyboardButton(str(i + 1), callback_data=i))
    btns.append(temp)
    keyboard = InlineKeyboardMarkup(btns)

    update.effective_user.send_message('С каким монстром Вы хотите провести эволюцию?', reply_markup=keyboard)


def select_monster_evolution(update: Update, context: CallbackContext):
    num = update.callback_query.data
    team = database_manager.get_team(update.effective_user.id).split(';')
    context.chat_data['collection_num'] = int(team[int(num)])
    context.chat_data['waiting_for'] = NOTHING
    evolution(update, context)


def want_evolution(update: Update, context: CallbackContext):  # удостоверяемся, точно ли игрок хочет провести
    # эволюцию своего монстра
    update.effective_message.delete()
    ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Да', callback_data='evolution'),
            InlineKeyboardButton('Нет', callback_data='main menu')
        ]
    ])
    update.effective_user.send_message('Вы точно хотите попробовать провести эволюцию монстра?', reply_markup=ques)


def evolution(update: Update, context: CallbackContext):  # эволюция монстров
    update.effective_message.delete()
    need_monster = context.chat_data['collection_num']
    all_info = database_manager.get_monster_info(need_monster)
    if all_info[1] == 'Spylit':
        monster = Spylit(lvl=int(all_info[2]), exp=int(all_info[3]), shiny=all_info[4], skills=all_info[-1].split(';'))
        if all_info[3] < 100:
            update.effective_user.send_message(
                'У вас недостаточно опыта для эволюции, играйте бои, чтобы получить опыт')
        elif all_info[2] < int(list(monster.evolution_rule.keys())[0]):
            update.effective_user.send_message('У вас маленький уровень, играйте бои, чтобы поднять свой уровень')
        elif all_info[3] >= 100 and all_info[2] >= int(list(monster.evolution_rule.keys())[0]):
            new_monster = monster.get_exp(0)
            context.chat_data['monster_id'] = all_info[0]
            new_name = 'Spylish'
            new_lvl = new_monster.lvl
            new_exp = new_monster.exp
            new_skills = ';'.join(new_monster.skills)
            try:
                database_manager.change_monster_params(new_name, new_lvl, new_exp, new_skills, need_monster)
                update.effective_user.send_message('Эволюция прошла успешно!')
                show_possible_skills(update, context, monster)
            except Exception as ex:
                print(ex)
                update.effective_user.send_message('Произошла ошибка, повторите попытку эволюции позже')
    elif all_info[1] == 'Spylish':
        monster = Spylish(lvl=int(all_info[2]), exp=int(all_info[3]), shiny=all_info[4], skills=all_info[-1].split(';'))
        if all_info[3] < 100:
            update.effective_user.send_message(
                'У вас недостаточно опыта для эволюции, играйте бои, чтобы получить опыт')
        elif all_info[2] < int(list(monster.evolution_rule.keys())[0]):
            update.effective_user.send_message('У вас маленький уровень, играйте бои, чтобы поднять свой уровень')
        elif all_info[3] >= 100 and all_info[2] >= int(list(monster.evolution_rule.keys())[0]):
            new_monster = monster.get_exp(0)
            context.chat_data['monster_id'] = all_info[0]
            new_name = 'Spyland'
            new_lvl = new_monster.lvl
            new_exp = new_monster.exp
            new_skills = ';'.join(new_monster.skills)
            try:
                database_manager.change_monster_params(new_name, new_lvl, new_exp, new_skills, need_monster)
                update.effective_user.send_message('Эволюция прошла успешно!')
                show_possible_skills(update, context, monster)
            except Exception as ex:
                print(ex)
                update.effective_user.send_message('Произошла ошибка, повторите попытку эволюции позже')
    elif all_info[1] == 'Spyland' or all_info[1] == 'Alopix' or all_info[1] == 'Wulkiss':
        update.effective_user.send_message('Ваш монстр уже на последней ступени эволюции')
    elif all_info[1] == 'Ailox':
        monster = Ailox(lvl=int(all_info[2]), exp=int(all_info[3]), shiny=all_info[4], skills=all_info[-1].split(';'))
        if all_info[3] < 100:
            update.effective_user.send_message(
                'У вас недостаточно опыта для эволюции, играйте бои, чтобы получить опыт')
        elif all_info[2] < int(list(monster.evolution_rule.keys())[0]):
            update.effective_user.send_message('У вас маленький уровень, играйте бои, чтобы поднять свой уровень')
        elif all_info[3] >= 100 and all_info[2] >= int(list(monster.evolution_rule.keys())[0]):
            new_monster = monster.get_exp(0)
            context.chat_data['monster_id'] = all_info[0]
            new_name = 'Ailoprex'
            new_lvl = new_monster.lvl
            new_exp = new_monster.exp
            new_skills = ';'.join(new_monster.skills)
            try:
                database_manager.change_monster_params(new_name, new_lvl, new_exp, new_skills, need_monster)
                update.effective_user.send_message('Эволюция прошла успешно!')
                show_possible_skills(update, context, monster)
            except Exception as ex:
                print(ex)
                update.effective_user.send_message('Произошла ошибка, повторите попытку эволюции позже')
    elif all_info[1] == 'Ailoprex':
        monster = Ailoprex(lvl=int(all_info[2]), exp=int(all_info[3]), shiny=all_info[4],
                           skills=all_info[-1].split(';'))
        if all_info[3] < 100:
            update.effective_user.send_message(
                'У вас недостаточно опыта для эволюции, играйте бои, чтобы получить опыт')
        elif all_info[2] < int(list(monster.evolution_rule.keys())[0]):
            update.effective_user.send_message('У вас маленький уровень, играйте бои, чтобы поднять свой уровень')
        elif all_info[3] >= 100 and all_info[2] >= int(list(monster.evolution_rule.keys())[0]):
            new_monster = monster.get_exp(0)
            context.chat_data['monster_id'] = all_info[0]
            new_name = 'Ailopix'
            new_lvl = new_monster.lvl
            new_exp = new_monster.exp
            new_skills = ';'.join(new_monster.skills)
            try:
                database_manager.change_monster_params(new_name, new_lvl, new_exp, new_skills, need_monster)
                update.effective_user.send_message('Эволюция прошла успешно!')
                show_possible_skills(update, context, monster)
            except Exception as ex:
                print(ex)
                update.effective_user.send_message('Произошла ошибка, повторите попытку эволюции позже')
    elif all_info[1] == 'Wulvit':
        monster = Wulvit(lvl=int(all_info[2]), exp=int(all_info[3]), shiny=all_info[4],
                         skills=all_info[-1].split(';'))
        if all_info[3] < 100:
            update.effective_user.send_message(
                'У вас недостаточно опыта для эволюции, играйте бои, чтобы получить опыт')
        elif all_info[2] < int(list(monster.evolution_rule.keys())[0]):
            update.effective_user.send_message('У вас маленький уровень, играйте бои, чтобы поднять свой уровень')
        elif all_info[3] >= 100 and all_info[2] >= int(list(monster.evolution_rule.keys())[0]):
            context.chat_data['monster_id'] = all_info[0]
            new_monster = monster.get_exp(0)
            new_name = 'Wullies'
            new_lvl = new_monster.lvl
            new_exp = new_monster.exp
            new_skills = ';'.join(new_monster.skills)
            try:
                database_manager.change_monster_params(new_name, new_lvl, new_exp, new_skills, need_monster)
                update.effective_user.send_message('Эволюция прошла успешно!')
                show_possible_skills(update, context, monster)
            except Exception as ex:
                print(ex)
                update.effective_user.send_message('Произошла ошибка, повторите попытку эволюции позже')
    elif all_info[1] == 'Wullies':
        monster = Wullies(lvl=int(all_info[2]), exp=int(all_info[3]), shiny=all_info[4],
                          skills=all_info[-1].split(';'))
        if all_info[3] < 100:
            update.effective_user.send_message(
                'У вас недостаточно опыта для эволюции, играйте бои, чтобы получить опыт')
        elif all_info[2] < int(list(monster.evolution_rule.keys())[0]):
            update.effective_user.send_message('У вас маленький уровень, играйте бои, чтобы поднять свой уровень')
        elif all_info[3] >= 100 and all_info[2] >= int(list(monster.evolution_rule.keys())[0]):
            new_monster = monster.get_exp(0)
            context.chat_data['monster_id'] = all_info[0]
            new_name = 'Wulkiss'
            new_lvl = new_monster.lvl
            new_exp = new_monster.exp
            new_skills = ';'.join(new_monster.skills)
            try:
                database_manager.change_monster_params(new_name, new_lvl, new_exp, new_skills, need_monster)
                update.effective_user.send_message('Эволюция прошла успешно!')
                show_possible_skills(update, context, monster)
            except Exception as ex:
                print(ex)
                update.effective_user.send_message('Произошла ошибка, повторите попытку эволюции позже')
    else:
        update.effective_user.send_message('Произошла ошибка, повторите попытку эволюции позже')


def show_possible_skills(update: Update, context: CallbackContext, monster):
    all_skills = monster.skills_rule
    possible_skills = []
    for key, val in all_skills.items():
        if monster.lvl >= int(key) and val.__class__.__name__ not in monster.skills:
            possible_skills.append(val.__class__.__name__)

    context.chat_data['skills'] = possible_skills
    if len(possible_skills) == 0:
        text = 'Ваш монстр уже выучил все доступные ему умения'
        update.effective_user.send_message(text)
    else:
        text = 'Монстр может выучить следующие навыки:\n\n'
        for i in range(len(possible_skills)):
            text += f'{i + 1}) {possible_skills[i]}\n'
        text += '\nБудете добавлять или заменять какой-то навык?'
        ques = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Да', callback_data='learn_skills'),
                InlineKeyboardButton('Нет', callback_data='main menu')
            ]
        ])
        context.chat_data['monster_class'] = monster
        update.effective_user.send_message(text=text, reply_markup=ques)


def ask_skill_num(update: Update, context: CallbackContext):
    context.chat_data['waiting_for'] = ABILITY_NUM
    update.effective_user.send_message('Введите номер способности, которую хотите добавить')
    get_skill_num(update, context)


def get_skill_num(update: Update, context: CallbackContext):
    skills = context.chat_data['skills']
    try:
        skill_num = int(update.message.text)
        if skill_num <= 0 or skill_num > len(skills):
            raise Exception
        else:
            context.chat_data['waiting_for'] = NOTHING
            context.chat_data['skill_num'] = skill_num
            learn_skills(update, context)
    except Exception as ex:
        print(ex)
        update.message.reply_text('Вы ввели не число или ввели номер, которого нет в списке, попробуйте ещё раз')


def learn_skills(update: Update, context: CallbackContext):
    monster = context.chat_data['monster_class']
    skills = context.chat_data['skills']
    skill_num = context.chat_data['skill_num']
    monster_id = context.chat_data['monster_id']

    monster.skills.append(skills[skill_num - 1])
    new_skills = ';'.join(monster.skills)
    database_manager.change_monster_skills(monster_id, new_skills)
    monster.deconvert_skills(new_skills)
    text = 'Ваш монстр успешно выучил новое умение!\n\nСпособности вашего монстра:\n'
    for i in range(len(monster.skills)):
        if monster.skills[i] is not None:
            text += f'{i + 1}) {monster.skills[i]}\n'
    update.effective_user.send_message(text)


def show_team_for_change(update: Update, context: CallbackContext):  # показывает команду при её изменении
    context.chat_data['waiting_for'] = COLLECTION_TEAM
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('1', callback_data='1'),
            InlineKeyboardButton('2', callback_data='2'),
            InlineKeyboardButton('3', callback_data='3'),
            InlineKeyboardButton('4', callback_data='4')
        ]
    ])
    team_info(update, context, only_show=True, reply_markup=keyboard)


def select_monster_in_team(update: Update, context: CallbackContext):  # выбор монстра из Inline
    num = update.callback_query.data
    context.chat_data['team_num'] = num
    context.chat_data['waiting for'] = NOTHING
    change_monster(update, context)


def show_abilities(update: Update, context: CallbackContext):  # показывает способности
    abilities, info = get_abilities(update, context)
    collection = get_collection_info(update, context)
    monster_num = int(context.chat_data['monster_num'])
    monster_name = collection[monster_num - 1][1]
    if collection[monster_num - 1][4]:
        text = f'Способности монстра 🌟{monster_name}: \n\n'
    else:
        text = f'Способности монстра {monster_name}: \n\n'
    for i in range(len(abilities)):
        if abilities[i] is not None:
            text += f'{i + 1}) {abilities[i].name}: {info[i].lower()}\n'
    update.effective_user.send_message(text)


def get_abilities(update: Update, context: CallbackContext):  # получение способностей и информации о них
    collection = get_collection_info(update, context)
    monster_num = context.chat_data['monster_num']
    need_id = collection[monster_num - 1][0]
    monster = create_monster_class(update, context, need_id)
    monster.deconvert_skills(collection[monster_num - 1][-1])
    abilities = monster.skills
    all_info = []
    for skill in abilities:
        if skill is not None:
            temp = database_manager.get_skill_info(skill.name)
            all_info.append(temp)
    return abilities, all_info


def create_monster_class(update: Update, context: CallbackContext, monster_id):
    monster_info = database_manager.get_monster_info(monster_id)
    if monster_info[1] == 'Spylit':
        monster = Spylit(lvl=monster_info[2], exp=monster_info[3], shiny=monster_info[4],
                         skills=monster_info[-1].split(';'))
    elif monster_info[1] == 'Spylish':
        monster = Spylish(lvl=monster_info[2], exp=monster_info[3], shiny=monster_info[4],
                          skills=monster_info[-1].split(';'))
    elif monster_info[1] == 'Spyland':
        monster = Spyland(lvl=monster_info[2], exp=monster_info[3], shiny=monster_info[4],
                          skills=monster_info[-1].split(';'))
    elif monster_info[1] == 'Ailox':
        monster = Ailox(lvl=monster_info[2], exp=monster_info[3], shiny=monster_info[4],
                        skills=monster_info[-1].split(';'))
    elif monster_info[1] == 'Ailoprex':
        monster = Ailoprex(lvl=monster_info[2], exp=monster_info[3], shiny=monster_info[4],
                           skills=monster_info[-1].split(';'))
    elif monster_info[1] == 'Ailopix':
        monster = Ailopix(lvl=monster_info[2], exp=monster_info[3], shiny=monster_info[4],
                          skills=monster_info[-1].split(';'))
    elif monster_info[1] == 'Wulvit':
        monster = Wulvit(lvl=monster_info[2], exp=monster_info[3], shiny=monster_info[4],
                         skills=monster_info[-1].split(';'))
    elif monster_info[1] == 'Wullies':
        monster = Wullies(lvl=monster_info[2], exp=monster_info[3], shiny=monster_info[4],
                          skills=monster_info[-1].split(';'))
    elif monster_info[1] == 'Wulkiss':
        monster = Wulkiss(lvl=monster_info[2], exp=monster_info[3], shiny=monster_info[4],
                          skills=monster_info[-1].split(';'))
    else:
        update.effective_user.send_message('Произошла ошибка, попробуйте ещё раз позже')
        return
    return monster


def team_info(update: Update, context: CallbackContext, only_show=False, reply_markup=None):  # показ команды
    update.effective_message.delete()
    user_id = update.effective_user.id
    monsters_id = database_manager.get_team(user_id).split(';')
    team = [database_manager.get_monster_info(int(i)) for i in monsters_id if i != '']
    text = 'Ваша команда:\n\n'
    if len(team) == 0:
        text = 'У вас пока нет монстров в команде. Выберите монстров для команды из коллекции'
        update.effective_user.send_message(text)
    else:
        for i in range(len(team)):
            if team[i][4]:
                text += f'{i + 1}) 🌟{team[i][1]}, уровень: {team[i][2]}, опыт: {team[i][3]}\n'
            else:
                text += f'{i + 1}) {team[i][1]}, уровень: {team[i][2]}, опыт: {team[i][3]}\n'
        if only_show:  # only_show - только показывать команду или предлагать дальше выбор монстра
            update.effective_user.send_message(text=text, reply_markup=reply_markup)
            return
        else:
            if len(team) < 4:
                text += f'\nВы можете добавить в команду ещё {4 - len(team)} монстра'
            update.effective_user.send_message(text=text)
            team_activity(update, context)


def team_activity(update: Update, context: CallbackContext):  # информация о команде
    change_ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Добавить или поменять монстра', callback_data='change team')
        ],
        [
            InlineKeyboardButton('Удалить монстра из команды', callback_data='delete from team')
        ]
    ])
    update.effective_user.send_message('Что Вы хотите сделать?', reply_markup=change_ques)


def show_team_for_delete(update: Update, context: CallbackContext):  # показ монстров для удаления
    context.chat_data['waiting_for'] = DELETE_FROM_TEAM
    team = database_manager.get_team(update.effective_user.id).split(';')

    btns = []  # создание кнопок
    temp = []
    for i in range(len(team)):
        temp.append(InlineKeyboardButton(str(i + 1), callback_data=i))
    btns.append(temp)
    keyboard = InlineKeyboardMarkup(btns)

    team_info(update, context, only_show=True, reply_markup=keyboard)


def select_monster_for_delete(update: Update, context: CallbackContext):  # выбор монстра из Inline
    num = update.callback_query.data
    context.chat_data['delete_num'] = num
    delete_from_team(update, context)


def delete_from_team(update: Update, context: CallbackContext):  # удаление из команды
    user_id = update.effective_user.id
    delete_num = int(context.chat_data['delete_num'])
    team = database_manager.get_team(user_id).split(';')
    collection = database_manager.get_collection(user_id)
    if len(collection) == 0:
        new_collection = str(team[delete_num])
    else:
        new_collection = f'{collection};{team[delete_num]}'
    change_collection(update, context, new_collection)
    del team[delete_num]
    context.chat_data['waiting_for'] = NOTHING
    change_team(update, context, ';'.join(team))
    team_info(update, context, only_show=True)


def change_team(update: Update, context: CallbackContext, team):  # изменение команды
    user_id = update.effective_user.id
    database_manager.change_user_team(user_id, team)
    update.effective_message.reply_text('Команда успешно изменена')


def change_collection(update: Update, context: CallbackContext,
                      new_collection):  # добавление монстра в коллекцию игрока
    user_id = update.effective_user.id
    database_manager.change_user_collection(user_id, new_collection)


# def check_add_monster(update: Update, context: CallbackContext, uid):  # проверка, есть ли новый монстр уже у игрока
#     collection = database_manager.get_collection(update.effective_user.id).split(';')
#     uid_in_coll = [database_manager.get_monster_uid(int(i)) for i in collection if i != '']
#     if uid in uid_in_coll:
#         return False
#     else:
#         return True


def write_team_num(update: Update, context: CallbackContext):  # запрашивает номер монстра из команды
    update.effective_message.delete()
    context.chat_data['waiting_for'] = TEAM_NUM
    update.effective_user.send_message('Введите номер монстра в команде')
    get_team_num(update, context)


def get_team_num(update: Update, context: CallbackContext):  # получает номер монстра из команды
    try:
        team_num = int(update.message.text)
        if team_num > 4 or team_num <= 0:
            raise Exception
        else:
            context.chat_data['team_num'] = team_num
            show_collection(update, context)
    except Exception as ex:
        print(ex)
        update.message.reply_text('Вы ввели не число или ввели номер, которого нет, попробуйте ещё раз')


def show_collection(update: Update, context: CallbackContext):  # показывает коллекцию с кнопками
    context.chat_data['waiting_for'] = COLLECTION_NUM
    context.chat_data['collection_num'] = 0
    collection = get_collection_info(update, context)

    btns = []  # создание кнопок
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
    if len(collection) == 0:
        update.effective_user.send_message('У вас больше нет монстров, сыграйте в бой PvE,'
                                           ' чтобы получить нового монстра')
    else:
        for i in range(len(collection)):
            if collection[i][4]:
                text += f'{i + 1}. 🌟{collection[i][1]}\n'
            else:
                text += f'{i + 1}. {collection[i][1]}\n'
        update.effective_user.send_message(text=text, reply_markup=InlineKeyboardMarkup(keyboard))


def select_monster(update: Update, context: CallbackContext):  # выбор монстра из Inline
    num = update.callback_query.data
    context.chat_data['collection_num'] = num
    context.chat_data['waiting for'] = NOTHING
    change_monster(update, context)


def change_monster(update: Update, context: CallbackContext):  # изменение команды и коллекции
    update.effective_message.delete()
    team = database_manager.get_team(update.effective_user.id).split(';')
    collection = database_manager.get_collection(update.effective_user.id).split(';')
    team_num = context.chat_data['team_num']
    coll_num = context.chat_data['collection_num']
    new_team = ''
    new_collection = ''

    for i in range(4):  # всего монстров 4
        if i == int(team_num) - 1:  # порядковый номер монстра в команде совпадает с номером нужного монстра
            new_team += f'{str(coll_num)};'
            if i >= len(team):  # если добавляем нового монстра
                continue
            else:
                new_collection += f'{team[i]};'  # если заменяем
        elif i >= len(team):  # если монстров меньше, чем 4
            continue
        elif team[i] != '':  # добавляем монстра из прошлой команды
            new_team += f'{team[i]};'
        else:
            new_team += f'{str(coll_num)}'  # добавляем нового монстра

    for i in range(len(collection)):  # создание новой коллекции
        if collection[i] == str(coll_num):
            new_collection += ''
        else:
            new_collection += f'{collection[i]};'

    change_team(update, context, new_team[:-1])  # изменение команды и коллекции в бд
    change_collection(update, context, new_collection[:-1])

    text = f'Новая команда:\n\n'  # текст для игрока
    monsters_id = database_manager.get_team(update.effective_user.id).split(';')
    new_team = [database_manager.get_monster_info(int(i)) for i in monsters_id if i != '']
    for i in range(len(new_team)):
        if new_team[i][4]:
            text += f'{i + 1}) 🌟{new_team[i][1]}, уровень: {new_team[i][2]}, опыт: {new_team[i][3]}\n'
        else:
            text += f'{i + 1}) {new_team[i][1]}, уровень: {new_team[i][2]}, опыт: {new_team[i][3]}\n'
    update.effective_user.send_message(text)
    next_activity(update, context)


def next_activity(update: Update, context: CallbackContext):  # предложение, что делать после изменения команды
    ques = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Изменить команду ещё раз', callback_data='team'),
            InlineKeyboardButton('Вернуться в главное меню', callback_data='main menu')
        ]
    ])
    update.effective_user.send_message(text='Что Вы хотите сделать?', reply_markup=ques)


def add_new_monster(update: Update, context: CallbackContext, monster_class):  # добавление нового монстра
    try:
        monsters_ids = database_manager.get_monsters_ids()
        monster_id = int(monsters_ids[-1][0]) + 1
        database_manager.add_monster(id=monster_id, name=monster_class.__class__.__name__,
                                     level=monster_class.lvl, exp=monster_class.exp, shiny=monster_class.shiny,
                                     skills=monster_class.convert_skills())
        return True
    except Exception as ex:
        print(ex)
        update.effective_user.send_message('Произошла ошибка при добавлении нового монстра, повторите попытку позже')
        return False


def change_monsters_exp(update: Update, context: CallbackContext, add_exp, user_id=None):  # изменение опыта монстра
    if user_id is None:
        user_id = update.effective_user.id
    try:
        monsters_id = database_manager.get_team(user_id).split(';')
        for i in monsters_id:
            new_exp = int(database_manager.get_monster_exp(int(i))) + int(add_exp)
            database_manager.change_monster_exp(new_exp, int(i))
            check_new_lvl(update, context, int(i))
    except Exception as ex:
        print(ex)


def check_new_lvl(update: Update, context: CallbackContext, monster_id):
    monster_info = database_manager.get_monster_info(monster_id)
    lvl = monster_info[2]
    exp = monster_info[3]
    if exp >= 100:
        monster = create_monster_class(update, context, monster_info[0])
        monster.get_exp(0)
        if list(monster.evolution_rule.keys()) != [] and lvl >= int(list(monster.evolution_rule.keys())[0]):
            context.chat_data['collection_num'] = monster_info[0]
            update.effective_user.send_message(
                f'Уровень Вашего монстра {monster.__class__.__name__} повысился: {monster.lvl}.'
                f' Вашему монстру теперь также доступна эволюция, чтобы её провести вызовите команду /evolution')
        else:
            database_manager.change_monster_lvl(monster_info[0], monster.lvl)
            new_exp = exp - 100
            database_manager.change_monster_exp(new_exp, monster_info[0])
            update.effective_user.send_message(
                f'Уровень Вашего монстра {monster.__class__.__name__} повысился: {monster.lvl}')
    else:
        update.effective_user.send_message(f'Опыт Вашего монстра {monster_info[1]} повысился: {exp}')
