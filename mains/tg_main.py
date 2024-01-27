import telebot
import os
import sys
import datetime
import json
import requests
from threading import Thread
from time import sleep
import hashlib


dir_path = os.path.dirname(os.path.realpath(__file__))

scripts_path = os.path.join(dir_path, '..', 'scripts')
sys.path.append(scripts_path)
scripts_path = os.path.join(dir_path, '..', 'data')
sys.path.append(scripts_path)

import schedule_parser
import day_inf
import parse_api


current_date = datetime.date.fromisoformat(str(datetime.datetime.now()).split(' ')[0])
current_date = datetime.date.fromisoformat("2023-11-17") # используется для тестов
delta = datetime.timedelta(1)


weekdays = {1: 'Понедельник',
            2: 'Вторник',
            3: 'Среда',
            4: 'Четверг',
            5: 'Пятница',
            6: 'Суббота',
            7: 'Воскресенье'}


def to_hyphen(r_date):
    # converts dd.mm.yyyy to yyyy-mm-dd
    # r_date has str formate
    return datetime.date.fromisoformat('{2}-{1}-{0}'.format(*r_date.split('.')))


def to_dots(r_date):
    # converts yyyy-mm-dd to dd.mm.yyyy
    # r_date has datetime.date formate
    return '{2}.{1}.{0}'.format(*str(r_date).split('-'))


def get_weeks(gr_data):
    first_date = datetime.date.fromisoformat(list(gr_data.keys())[0])
    last_date = datetime.date.fromisoformat(list(gr_data.keys())[-1])
    first_week_mon = first_date - datetime.timedelta(days=first_date.weekday())
    last_week_mon = last_date - datetime.timedelta(days=last_date.weekday())
    i = 0
    lines = ['Выберите неделю:\n']
    tmp_butns = []
    while first_week_mon != last_week_mon + datetime.timedelta(7):
        i += 1
        line = (f'   <b>[{i}]</b> {to_dots(first_week_mon)} - {to_dots(first_week_mon + datetime.timedelta(6))}\n')
        tmp_but = telebot.types.InlineKeyboardButton(str(i), callback_data=str(i))
        tmp_butns.append(tmp_but)
        lines.append(line)
        first_week_mon += datetime.timedelta(7)
    return '\n'.join(lines), tmp_butns


def get_weeks_2(gr_data):
    first_date = to_hyphen(list(gr_data.keys())[1])
    last_date = to_hyphen(list(gr_data.keys())[-1])
    first_week_mon = first_date - datetime.timedelta(days=first_date.weekday())
    last_week_mon = last_date - datetime.timedelta(days=last_date.weekday())
    i = 0
    lines = ['Выберите неделю:\n']
    tmp_butns = []
    while first_week_mon != last_week_mon + datetime.timedelta(7):
        i += 1
        line = (f'   <b>[{i}]</b> {to_dots(first_week_mon)} - {to_dots(first_week_mon + datetime.timedelta(6))}\n')
        tmp_but = telebot.types.InlineKeyboardButton(str(i), callback_data=str(i)+'_2')
        tmp_butns.append(tmp_but)
        lines.append(line)
        first_week_mon += datetime.timedelta(7)
    return '\n'.join(lines), tmp_butns


def check(message):
    try:
        start, end = message.text.split('-')
        start = '2023-{}-{}'.format(*start.split('.')[::-1])
        end = '2023-{}-{}'.format(*end.split('.')[::-1])
        start_date = datetime.date.fromisoformat(start)
        end_date = datetime.date.fromisoformat(end)
        return [True, start_date, end_date]
    except:
        return [False]


with open('data/token.txt') as token:
    token = token.readline()
    bot = telebot.TeleBot(token)


keyboard = telebot.types.InlineKeyboardMarkup()
but_1 = telebot.types.InlineKeyboardButton('Сегодня', callback_data='today')
but_2 = telebot.types.InlineKeyboardButton('Завтра', callback_data='tomorrow')
but_3 = telebot.types.InlineKeyboardButton('Послезавтра', callback_data='after_tomorrow')
but_4 = telebot.types.InlineKeyboardButton('Текущая неделя', callback_data='week')
but_5 = telebot.types.InlineKeyboardButton('Следующая неделя', callback_data='next_week')
but_6 = telebot.types.InlineKeyboardButton('Выбрать неделю', callback_data='selected_week')
keyboard.row(but_1, but_2, but_3)
keyboard.row(but_4, but_5, but_6)


keyboard_2 = telebot.types.InlineKeyboardMarkup()
but_1_2 = telebot.types.InlineKeyboardButton('Сегодня', callback_data='today_2')
but_2_2 = telebot.types.InlineKeyboardButton('Завтра', callback_data='tomorrow_2')
but_3_2 = telebot.types.InlineKeyboardButton('Послезавтра', callback_data='after_tomorrow_2')
but_4_2 = telebot.types.InlineKeyboardButton('Текущая неделя', callback_data='week_2')
but_5_2 = telebot.types.InlineKeyboardButton('Следующая неделя', callback_data='next_week_2')
but_6_2 = telebot.types.InlineKeyboardButton('Выбрать неделю', callback_data='selected_week_2')
keyboard_2.row(but_1_2, but_2_2, but_3_2)
keyboard_2.row(but_4_2, but_5_2, but_6_2)


@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.send_message(message.from_user.id,
                     'Это бот расписания МАИ!\nДля получения расписания из файла оправьте файл. Для получения '
                     'расписания группы с сервера введите название группы. (Пример: М3О-206С-22)')


@bot.message_handler(commands=['groups'])
def get_groups():
    while True:
        files = os.listdir('data')
        print('Update started', datetime.datetime.now().time())
        agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                 'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15')

        for elem in files:
            try:
                if elem[:6] == 'group ':
                    url = f'https://public.mai.ru/schedule/data/{elem[6:]}'
                    response = requests.get(url, headers={'User-Agent': agent}).json()

                    with open(f'data/{elem}', 'w+') as json_file:
                        json.dump(response, json_file)

                    print(elem, 'Update success')

            except Exception:
                if os.path.exists(f'data/{elem}'):
                    os.remove(f'data/{elem}')
                    print(elem, 'An error has occurred. File has been deleted.')

        url = 'https://public.mai.ru/schedule/data/groups.json'

        response = requests.get(url, headers={'User-Agent': agent}).json()

        with open('data/groups.json', 'w+') as json_file:
            json.dump(response, json_file)

        print('groups.json Update success', datetime.datetime.now().time())

        with open('data/groups.json') as json_file:
            data = json.load(json_file)

        global list_of_groups
        list_of_groups = []
        for i in data:
            list_of_groups.append(i.get('name'))
        print('Update ended', datetime.datetime.now().time())
        sleep(3600 * 24)


thread = Thread(target=get_groups, daemon=True)
thread.start()


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    cid = message.chat.id
    if message.text in list_of_groups:

        agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                 'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15')
        hash_name = hashlib.md5(message.text.encode()).hexdigest()
        url = f'https://public.mai.ru/schedule/data/{hash_name}.json'

        response = requests.get(url, headers={'User-Agent': agent}).json()

        with open(f'data/group {hash_name}.json', 'w+') as file:
            json.dump(response, file, ensure_ascii=False)

        with open('data/selected_groups.json') as file:
            selected = json.load(file)

        try:
            del selected[str(cid)]
        except Exception:
            pass
        selected[cid] = message.text


        with open('data/selected_groups.json', 'w+') as file:
            json.dump(selected, file)

        bot.send_message(cid, f'Вы выбрали группу {message.text}\nВыберите нужный вариант расписания',
                         reply_markup=keyboard_2)

    else:
        bot.send_message(cid, 'Такой группы нет! (Пример: М3О-206С-22)')


@bot.callback_query_handler(func=lambda call: call.data in [str(i) for i in range(30)])
def redact_keyboard(call):
    cid = call.message.chat.id
    mid = call.message.message_id

    with open(f'data/data schedule {cid}.json') as json_file:
        data = json.load(json_file)


    first_date = datetime.date.fromisoformat(list(data.keys())[0])

    week_delta = datetime.timedelta((int(call.data) - 1) * 7)

    monday = first_date - datetime.timedelta(days=current_date.weekday()) + week_delta
    dates = [monday + datetime.timedelta(days=day) for day in range(7)]
    lines = []
    for day in dates:
        if day.isoformat() in data:
            lines.append('\n<b>Дата: {2}.{1}.{0}</b>'.format(*str(day).split('-')) +
                         f' <b>({weekdays.get(day.isocalendar()[2])})</b>' + '\n' +
                         day_inf.inf(data[str(day)]))
        else:
            lines.append('\n<b>Дата: {2}.{1}.{0}</b>'.format(*str(day).split('-')) +
                         f' <b>({weekdays.get(day.isocalendar()[2])})</b>' + '\n' + "В этот день нет пар!")
    bot.edit_message_text('\n--------------------------\n'.join(lines), cid, mid, reply_markup=keyboard,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data in [str(i)+'_2' for i in range(30)])
def redact_keyboard_2(call):
    cid = call.message.chat.id
    mid = call.message.message_id

    with open('data/selected_groups.json') as json_file:
        groups = json.load(json_file)

    with open(f'data/group {hashlib.md5(groups[str(cid)].encode()).hexdigest()}.json') as json_file:
        data = json.load(json_file)

    first_date = to_hyphen(list(data.keys())[1])

    week_delta = datetime.timedelta((int(call.data[:-2]) - 1) * 7)

    monday = first_date - datetime.timedelta(days=current_date.weekday()) + week_delta
    dates = [monday + datetime.timedelta(days=day) for day in range(7)]
    lines = []
    for day in dates:
        day_str = to_dots(day)
        if day_str in data:
            lines.append(parse_api.parse(day, data))
        else:
            lines.append(f'<b>Дата: {day_str} ({weekdays.get(day.isocalendar()[2])})</b>\n'
                         f'В этот день нет пар!')
        lines.append('--------------------------\n')
    bot.edit_message_text('\n'.join(lines[:-1]), cid, mid, reply_markup=keyboard_2, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data in
                                              ['today_2', 'tomorrow_2', 'after_tomorrow_2',
                                               'week_2', 'next_week_2', 'selected_week_2'])
def callback_handler_2(call):

    cid = call.message.chat.id
    mid = call.message.message_id

    try:
        with open('data/selected_groups.json') as json_file:
            groups = json.load(json_file)

        with open(f'data/group {hashlib.md5(groups[str(cid)].encode()).hexdigest()}.json') as json_file:
            data = json.load(json_file)

        flag = False
        is_week = False
        if call.data == 'today_2':
            day = current_date
        if call.data == 'tomorrow_2':
            day = current_date + delta
        if call.data == 'after_tomorrow_2':
            day = current_date + delta + delta
        if call.data == 'week_2':
            week_delta = datetime.timedelta(0)
            is_week = True
        if call.data == 'next_week_2':
            week_delta = datetime.timedelta(7)
            is_week = True
        if call.data == 'selected_week_2':
            flag = True
            weeks, buttons = get_weeks_2(data)
            keys_2 = telebot.types.InlineKeyboardMarkup()
            j = 0
            rows = len(buttons) // 5 + 1
            for i in range(rows):
                if i == rows - 1:
                    keys_2.row(*buttons[i * 5:])
                    continue
                keys_2.row(*buttons[i * 5: (i + 1) * 5])
            bot.edit_message_text(weeks, cid, mid, reply_markup=keys_2, parse_mode='HTML')
        if not is_week:
            if not flag:
                day_str = to_dots(day)
                if day_str in data:
                    bot.edit_message_text(parse_api.parse(day, data), cid, mid, reply_markup=keyboard_2, parse_mode='HTML')
                else:
                    bot.edit_message_text(f'<b>Дата: {day_str} ({weekdays.get(day.isocalendar()[2])})</b>\n'
                                          f'В этот день нет пар!', cid, mid, reply_markup=keyboard_2, parse_mode='HTML')
        else:
            monday = current_date - datetime.timedelta(days=current_date.weekday()) + week_delta
            dates = [monday + datetime.timedelta(days=day) for day in range(7)]
            lines = []
            for day in dates:
                day_str = to_dots(day)
                if day_str in data:
                    lines.append(parse_api.parse(day, data))
                else:
                    lines.append(f'<b>Дата: {day_str} ({weekdays.get(day.isocalendar()[2])})</b>\n'
                                 f'В этот день нет пар!')
                lines.append('--------------------------\n')
            bot.edit_message_text('\n'.join(lines[:-1]), cid, mid, reply_markup=keyboard_2, parse_mode='HTML')
        sleep(1)
    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data in ['today', 'tomorrow', 'after_tomorrow',
                                                            'week', 'next_week', 'selected_week'])
def callback_handler(call):

    cid = call.message.chat.id
    mid = call.message.message_id
    try:
        with open(f'data/data schedule {cid}.json') as json_file:
            data = json.load(json_file)
        is_week = False
        flag = False
        if call.data == 'today':
            day = str(current_date)
        if call.data == 'tomorrow':
            day = str(current_date + delta)
        if call.data == 'after_tomorrow':
            day = str(current_date + delta + delta)
        if call.data == 'week':
            week_delta = datetime.timedelta(0)
            is_week = True
        if call.data == 'next_week':
            week_delta = datetime.timedelta(7)
            is_week = True
        if call.data == 'selected_week':
            flag = True
            weeks, buttons = get_weeks(data)
            keys = telebot.types.InlineKeyboardMarkup()
            j = 0
            rows = len(buttons) // 5 + 1
            for i in range(rows):
                if i == rows - 1:
                    keys.row(*buttons[i * 5:])
                    continue
                keys.row(*buttons[i * 5: (i + 1) * 5])
            bot.edit_message_text(weeks, cid, mid, reply_markup=keys, parse_mode='HTML')
        if not is_week:
            if not flag:
                if day in data:
                    bot.edit_message_text('<b>Дата: {}</b>'.format(to_dots(day)) +
                                          f' <b>({weekdays.get(datetime.date.fromisoformat(day).isocalendar()[2])})</b>' +
                                          '\n' + day_inf.inf(data[day]), cid, mid, reply_markup=keyboard, parse_mode="HTML")
                else:
                    bot.edit_message_text('<b>Дата: {}</b>'.format(to_dots(day)) +
                                          f' <b>({weekdays.get(datetime.date.fromisoformat(day).isocalendar()[2])})</b>' +
                                          '\n' + "В этот день нет пар!", cid, mid, reply_markup=keyboard, parse_mode="HTML")
        else:
            monday = current_date - datetime.timedelta(days=current_date.weekday()) + week_delta
            dates = [monday + datetime.timedelta(days=day) for day in range(7)]
            lines = []
            for day in dates:
                if day.isoformat() in data:
                    lines.append('\n<b>Дата: {2}.{1}.{0}</b>'.format(*str(day).split('-')) +
                                 f' <b>({weekdays.get(day.isocalendar()[2])})</b>' + '\n' +
                                 day_inf.inf(data[str(day)]))
                else:
                    lines.append('\n<b>Дата: {2}.{1}.{0}</b>'.format(*str(day).split('-')) +
                                 f' <b>({weekdays.get(day.isocalendar()[2])})</b>' + '\n' + "В этот день нет пар!")
            bot.edit_message_text('\n--------------------------\n'.join(lines), cid, mid, reply_markup=keyboard, parse_mode="HTML")

    except Exception:
        pass


@bot.message_handler(content_types=['document'])
def addfile(message):
    bot.send_message(message.from_user.id, 'Загрузка...')
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(f'data/schedule {message.from_user.id}.xlsx', 'wb') as new_file:
        new_file.write(downloaded_file)
    try:
        schedule_parser.parser(f'schedule {message.from_user.id}')
        bot.send_message(message.from_user.id, 'Файл обработан успешно!')
        cid = message.chat.id
        bot.send_message(cid, "Выберите нужный вариант расписания.", reply_markup=keyboard)
    except ValueError:
        bot.send_message(message.from_user.id, 'Ошибка в обработке файла!')


bot.polling(none_stop=True, interval=0)