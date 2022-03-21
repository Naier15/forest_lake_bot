#!/usr/bin/python
#  - *- coding: utf- 8 - *-
from telebot import types
from config import secret_key_for_writer, secret_key_for_worker, bot, script, \
    proccess, adding_info, stages, chapter, edit_message_id, current_stage
import control as ctrl
import dbmysql as db, serializers as srlz


hide_board = types.ReplyKeyboardRemove()

@bot.message_handler(commands=['start'])
def start(message):
    ctrl.set_standard_command()
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAANpYitwQuyY-LHX7TXxii0c-vfgEjoAAigAA05c0im406x7EjJN1CME')
    bot.send_message(message.chat.id, \
        '<b>Добрый день\nНачнем работу?\nЧтобы войти, введите ключ для сотрудника...</b>', parse_mode='html')

    db.init()
    db.create()

@bot.message_handler(commands=['close'])
def start(message):
    bot.send_message(message.chat.id, '<b>*Плак плак*</b>', parse_mode='html')

    srlz.delete_worker(message)
    srlz.delete_writer(message)

@bot.message_handler(commands=['get_info'])
def get_info(message):
    if not srlz.check_worker(message):
        return
    result = srlz.fetch_buildings()

    if result:
        commands = []
        for row in result:
            commands.append(types.BotCommand(f'/{row[1]}', f'Текущий этап {srlz.index_to_stage(row[2])}'))
        bot.set_my_commands(commands)

        sent = bot.send_message(message.chat.id, 'Выберете номер объекта: \n(начиная ввод с /)', reply_markup=hide_board)
        bot.register_next_step_handler(sent, ctrl.prepare_card, result)
    else:
        bot.send_message(message.chat.id, 'Пока в базе ни одной записи', reply_markup=hide_board)


@bot.message_handler(commands=['editor_menu'])
def editor(message):
    if srlz.check_writer(message):
        editor_menu(message)
    else:
        send = 'Чтобы вносить информацию введите <b><i>секретный ключ для редактора...</i></b>'
        bot.send_message(message.chat.id, send, parse_mode='html')

def editor_menu(message):
    if message.text == 'Добавить объект':
        start_dialog(message)
        return
    elif message.text in ['Удалить последний этап объекта', 'Удалить объект со всей историей']:
        result = srlz.fetch_buildings()

        if result:
            commands = []
            for row in result:
                commands.append(types.BotCommand(f'/{row[1]}', f'Текущий этап {srlz.index_to_stage(row[2])}'))
            bot.set_my_commands(commands)

            sent = bot.send_message(message.chat.id, 'Напишите номер объекта для удаления:\n(начиная ввод с /) ', reply_markup=hide_board)
            if message.text == 'Удалить объект со всей историей':
                bot.register_next_step_handler(sent, ctrl.delete_building_completely)
            elif message.text == 'Удалить последний этап объекта':
                bot.register_next_step_handler(sent, ctrl.delete_building_partially)
        else:
            bot.send_message(message.chat.id, 'Пока в базе ни одной записи', reply_markup=hide_board)
        return
    elif message.text == 'Назад':
        bot.send_message(message.chat.id, 'Выберете действие: ', reply_markup=hide_board)
        return

    
    markup = [  'Добавить объект', 
                'Удалить последний этап объекта', 
                'Удалить объект со всей историей' ]
    sent = bot.send_message(message.chat.id, 'Выберете действие: ', reply_markup=ctrl.set_markup(markup, 1))
    bot.register_next_step_handler(sent, editor_menu)


@bot.message_handler(content_types=['text', 'photo'])
def get_text(message, *args):
    # Регистрация сотрудников и редактора
    reg = srlz.check_writer(message)
    if not reg and message.text == secret_key_for_writer:
        srlz.add_writer(message)
        editor_menu(message)
        return

    reg = srlz.check_worker(message)
    if not reg and message.text == secret_key_for_worker:
        ctrl.set_standard_command()
        srlz.add_worker(message)
        return

    # Если не сотрудник нет доступа к боту
    if not reg:
        return
    try:
        if message.text:
            if message.text.strip().lower() in "кто твой создатель" or \
                message.text.strip().lower() in "кто тебя создал":
                bot.send_message(message.chat.id, 'grv1510@mail.ru', reply_markup=hide_board)
                return

        global adding_info
        if message.text == '/editor_menu':
            adding_info = False
            editor_menu(message)
            return
        elif message.text == '/get_info':
            adding_info = False
            get_info(message)
            return

        if message.content_type == 'text' and adding_info:
            parse_text(message)

        elif message.content_type == 'photo' and adding_info:
            parse_photo(message, *args)

    except AssertionError as e:
        bot.reply_to(message, f'{e}')
        say(message)
    except Exception as e:
        print(f'----- Ошибка -- {e} ---')
        bot.reply_to(message, 'Произошла ошибка...\nПопробуйте создать запрос заново')
        say(message, ctrl.set_markup())

@bot.callback_query_handler(func=lambda call: True)
def edit_message(call):
    if call.message:
        building, stage = map(int, call.data.split(' '))
        global current_stage, edit_message_id
        if stage in current_stage:
            return
        bot.delete_message(call.message.chat.id, edit_message_id[0])
        bot.delete_message(call.message.chat.id, edit_message_id[1])
        edit_message_id.clear()
        current_stage.clear()
        
        ctrl.show_building(call.message, building, stage, show_history=False)


def say(message, markup=hide_board, stop=False):
    global chapter, json
    send = bot.send_message(message.chat.id, script[chapter], reply_markup=markup)

    if not stop:
        bot.register_next_step_handler(send, get_text, 'Это первая фотография из загруженных')
    else:
        load_data()

def load_data():
    global adding_info, json, chapter
    chapter = 0
    adding_info = False
    if json['accept'] == 'Подтвержаю':
        srlz.load_to_db(json)
    json = {}

def start_dialog(message, markup=hide_board):
    global chapter, json, adding_info
    adding_info = True
    chapter = 0
    json = {}
    say(message, markup)

def parse_text(message):
    if message.text == 'Назад':
        current_key = get_back(message) 
    else:
        current_key = proccess[chapter]

        # Проверка на введение числа в building
        if current_key == 'building':
            try: int(message.text)
            except: raise AssertionError('Вы ввели не число')

        json[current_key] = message.text

        upgrade_chapter()
        current_key = proccess[chapter]

    if current_key in ['building']:
        start_dialog(message)
    elif current_key in ['stage']:
        say(message, ctrl.set_markup(list(stages.keys()), 2))
    elif current_key in ['substage']:
        say(message, ctrl.set_markup(stages[json['stage']], 2))
    elif current_key in ['photo', 'docs', 'comment']:
        say(message, ctrl.set_markup())
    elif current_key in ['accept']:
        say(message, ctrl.set_markup(['Подтвержаю'], 2))
    elif current_key in ['end']:
        say(message, stop=True)
    else:
        bot.send_message(message.chat.id, 'Извините, Ваш запрос не понятен', reply_markup=hide_board) 

def parse_photo(message, *args):
    current_key = proccess[chapter]
    if args:
        if current_key not in json.keys():
            json[current_key] = []
        bytes = ctrl.convert_image_to_binary(message.photo)
        json[current_key].append(bytes) #bytes
        
        upgrade_chapter()
        current_key = proccess[chapter]
        if current_key in ['docs']:
            say(message, ctrl.set_markup())
        elif current_key in ['comment']:
            say(message, ctrl.set_markup())
    else:
        if 'docs' in json.keys():
            bytes = ctrl.convert_image_to_binary(message.photo)
            json['docs'].append(bytes) #bytes

def get_back(message):
    global chapter

    if chapter == 0:
        global adding_info
        adding_info = False
        editor_menu(message)
        return

    chapter -= 1
    if proccess[chapter] in ['photo']:
        json.pop('photo')
    elif proccess[chapter] in ['docs']:
        json.pop('docs')
    return proccess[chapter]

def upgrade_chapter():
    global chapter
    chapter += 1


bot.polling(none_stop=True)