from telebot import types
from fpdf import FPDF
from os import remove
from config import bot, edit_message_id, current_stage
import serializers as srlz


hide_board = types.ReplyKeyboardRemove()

def prepare_card(message, *args):
    try:        
        set_standard_command()
        result = list( filter(lambda row: str(row[1]) == message.text[1:], args[0]) )[0]
        show_building(message, result[1], result[2])
    except Exception as e:
        print(f'----- Ошибка 2 -- {e} ---')
        bot.send_message(message.chat.id, 'Произошла ошибка...\nПопробуйте еще раз', reply_markup=hide_board)

def show_building(message, building, stage_int, show_history=True):
    global current_stage, edit_message_id
    current_stage.clear()
    edit_message_id.clear()

    data = srlz.fetch_data(building, stage_int)
    docs = srlz.fetch_docs(building, stage_int)
    photo, comment, date = data[0]
    
    # Подготовливаем текст
    card = f"""<b>#Ю{building}</b>
                \n\n{srlz.index_to_stage(stage_int)} - {srlz.index_to_substage(stage_int)}
                \nДата: {date.strftime("%d.%m.%Y")}
                \n"""
    if comment.strip() != '':
        card += f'Примечание: {comment}\n'

    if show_history:
        history = srlz.fetch_stages(building)
        if history:
            keyboard = types.InlineKeyboardMarkup()
            for stage in history:
                stage = stage[0]
                callback_button = types.InlineKeyboardButton(
                    text=f'{srlz.index_to_stage(stage)} - {srlz.index_to_substage(stage)}', \
                        callback_data=f'{building} {stage}'
                )
                keyboard.add(callback_button)
            bot.send_message(message.chat.id, 'Кнопки покажут историю объекта...', reply_markup=keyboard)

    current_stage.append(stage_int)

    message = bot.send_photo(message.chat.id, photo, caption=card, parse_mode='html', reply_markup=hide_board)

    edit_message_id.append(message.message_id)

    # Оформляем документы
    pdf_docs = image2pdf(docs)
    with open(pdf_docs, 'rb') as file:
        message = bot.send_document(message.chat.id, file.read(), \
            visible_file_name=f'Документы для #Ю{building}.pdf')
        edit_message_id.append(message.message_id)
    remove(pdf_docs)

def delete_building_completely(message):
    set_standard_command()
    building = message.text[1:]
    srlz.delete_building_completely(message, building)
    return

def delete_building_partially(message):
    set_standard_command()
    building = message.text[1:]
    current_stage = srlz.fetch_current_stage(building)[0][0]
    srlz.delete_building_by_stage(message, building, current_stage)
    return

def convert_image_to_binary(photo):
    photo = bot.get_file(photo[-1].file_id).file_path
    return bot.download_file(photo)

def convert_binary_to_image(bytes, index):
    path = f'./photo{index}.jpg'
    with open(path, 'w+b') as file:
        file.write(bytes)
    return path

def set_markup(list=None, row=None):
    markup = types.ReplyKeyboardMarkup(row_width=row, one_time_keyboard=True) if row else \
        types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    if list:
        markup.add(*list, 'Назад')
    else:
        markup.add('Назад')
    return markup

def image2pdf(docs):
    pdf = FPDF(orientation='P', format='A4')
    pdf.add_page()
    for i, doc in enumerate(docs):
        photo = convert_binary_to_image(doc[0], i)
        pdf.image(photo, x=pdf.w/8, w=pdf.w-(pdf.w/4))
        pdf.ln(20)
        remove(photo)  # модуль os
    path = './Документы.pdf'
    pdf.output(path)
    return path

def set_standard_command():
    bot.set_my_commands([types.BotCommand('/get_info', 'Получить информацию об объекте'), 
                        types.BotCommand('/editor_menu', 'Войти в меню редактора')])
    return
