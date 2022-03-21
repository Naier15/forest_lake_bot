from dbmysql import select, execute
from config import bot, substages, stages
from telebot import types


hide_board = types.ReplyKeyboardRemove()
def check_writer(message):
    try:
        data = select('SELECT user_id FROM writers WHERE user_id = %s;', \
            (message.from_user.id, )
        )

        if data and message.from_user.id in data[0]:
            return True
        return False
    except:
        return False

def check_worker(message):
    try:
        data = select('SELECT user_id FROM workers WHERE user_id = %s;', \
            (message.from_user.id, )
        )
        
        if data[0] and message.from_user.id in data[0]:
            return True
        return False
    except:
        return False

def add_writer(message):
    execute('INSERT INTO writers (user_id) VALUES (%s);', \
        (message.from_user.id,)
    )
    bot.send_message(message.chat.id, 'Добро пожаловать в меню редактора')

def add_worker(message):
    execute('INSERT INTO workers (user_id) VALUES (%s);', \
        (message.from_user.id,)
    )
    bot.send_message(message.chat.id, 'Теперь можете выбрать команду:')

def delete_writer(message):
    if check_writer(message):
        execute('DELETE FROM writers WHERE user_id=(%s);', \
            (message.from_user.id,)
        )
        bot.send_message(message.chat.id, 'Вы больше не редактор', reply_markup=hide_board)

def delete_worker(message):
    if check_worker(message):
        execute('DELETE FROM workers WHERE user_id=(%s);', \
            (message.from_user.id,)
        )
        bot.send_message(message.chat.id, 'Вы больше не сотрудник', reply_markup=hide_board)


def load_to_db(json):
    stage_index = substage_to_index(json['substage'])
    if has_building(json['building']):
        execute('UPDATE buildings SET stage = %s WHERE building = %s;', \
            (stage_index, json['building'])
        )
    else:
        execute('INSERT INTO buildings (building, stage) VALUES (%s, %s);', \
            (json['building'], stage_index)
        )
    execute('INSERT INTO data (photo, building, stage, comment) VALUES (%s, %s, %s, %s);', \
        (json['photo'][0], json['building'], stage_index, json['comment'])
    )
    for doc in json['docs']:
        execute('INSERT INTO docs (document, building, stage) VALUES (%s, %s, %s);', \
            (doc, json['building'], stage_index) 
        )

def fetch_buildings():
    return select('SELECT * FROM buildings;')

def fetch_data(building, stage):
    return select('SELECT photo, comment, date FROM data WHERE building = %s AND stage = %s;', \
        (building, stage)
    )

def fetch_docs(building, stage):
    return select('SELECT document FROM docs WHERE building = %s AND stage = %s;', \
        (building, stage)
    )

def fetch_stages(building):
    return select('SELECT stage FROM data WHERE building = %s ORDER BY stage;', \
        (building, )
    )

def fetch_current_stage(building):
    return select('SELECT stage FROM buildings WHERE building = %s;', \
        (building, )
    )

def delete_building_completely(message, building):
    if has_building(building):
        try:
            execute('DELETE FROM buildings WHERE building = %s;', \
                (building,)
            )
            execute('DELETE FROM data WHERE building = %s;', \
                (building,)
            )
            execute('DELETE FROM docs WHERE building = %s;', \
                (building,)
            )
            bot.send_message(message.chat.id, 'Успешно удалено', reply_markup=hide_board)
        except Exception as e:
            print(f'Во время удаления объекта полностью произошла ошибка - {e}')
            bot.send_message(message.chat.id, 'Во время удаления произошла ошибка', reply_markup=hide_board)
    else:
        bot.send_message(message.chat.id, f'В базе нет данных об объекте под номером: {building}', \
            reply_markup=types.ReplyKeyboardRemove())

def delete_building_by_stage(message, building, stage):
    if has_building(building):
        try:
            prev_stage = find_prev_stage(building)
            if prev_stage != -1:
                execute('UPDATE buildings SET stage = %s WHERE building = %s;', \
                    (prev_stage, building)
                )
                execute('DELETE FROM data WHERE building = %s AND stage = %s;', \
                    (building, stage)
                )
                execute('DELETE FROM docs WHERE building = %s AND stage = %s;', \
                    (building, stage)
                )
                bot.send_message(message.chat.id, 'Этап успешно удален', reply_markup=hide_board)
            else:
                delete_building_completely(message, building)
        except Exception as e:
            print(f'Во время удаления этапа объекта произошла ошибка - {e}')
            bot.send_message(message.chat.id, 'Во время удаления произошла ошибка', reply_markup=hide_board)
    else:
        bot.send_message(message.chat.id, f'В базе нет данных об объекте под номером: {message.text}', \
            reply_markup=types.ReplyKeyboardRemove())

def find_prev_stage(building):
    try:
        return select('SELECT stage FROM data WHERE building = %s ORDER BY stage DESC OFFSET 1;', \
            (building, )
        )[0][0]
    except:
        return -1

def has_building(building):
    return select('SELECT building FROM buildings WHERE building=(%s);', \
        (building,)
    )

def is_building_number_unique(number):
    result = fetch_buildings()
    for row in result:
        if row[1] == number:
            return False
    return True
    
def substage_to_index(substage: str):
    return substages.index(substage)

def index_to_substage(index: int):
    return substages[index]

def index_to_stage(index: int):
    for key, value in stages.items():
        if substages[index] in value:
            return key

