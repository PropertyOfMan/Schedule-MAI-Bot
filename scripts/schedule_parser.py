import os.path

import openpyxl as op
import json
from datetime import datetime, date, timedelta
from calendar import monthrange

year = 2023


def parse(lst_input):  # в функцию передаётся значение ячейки таблицы
    if lst_input is None:
        return None  # пустая ячейка возвращает значение None

    # объявляем переменные
    (date, time_start, time_end, time_start_s,
     time_end_s, lector, room, subj_type, subj, joined) = (
        None, None, None, None, None, None, None, None, None, False)

    parsed = lst_input.split('---')  # в некоторых ячейках есть разбитие на две части через "---";

    for i in range(len(parsed)):
        # преобразуем переменную parse к виду без лишних пробелов и \n
        if i == 0:
            parsed[i] = parsed[i][:-1].rstrip()
            continue
        parsed[i] = parsed[i][1:-1].rstrip()

    temp = []

    for _ in parsed:
        # присваиваем всем переменным соответствующие значения

        lector, time_and_room, subj_and_type_and_dates = _.split("\n")

        lector = None if lector == '' else lector

        splitter = time_and_room.find('ауд.')
        room = time_and_room[splitter + 4:-1]
        time_start, time_end = time_and_room[:splitter - 1].split("-")

        subj, type_and_dates = subj_and_type_and_dates.split(", ")
        subj_type, date = type_and_dates.split(" ")

        # print(f"date - {date};")
        # print(f"start time - {time_start};\nendtime - {time_end};")
        # print(f"lector - {lector};")
        # print(f"room - {room};")
        # print(f"subject type - {subj_type};\nsubject - {subj};")
        #
        # print("\n")

        temp.append([date, time_start, time_end, time_start_s, time_end_s,
                     lector, room, subj_type, subj, joined])

    # возвращаем в виде списка все необходимые переменные
    return temp


def parser(file_name):

    # открываем Excel файл и лист в нём
    wb = op.load_workbook(f'data/{file_name}.xlsx')
    ws = wb["TDSheet"]

    # находим объединённые ячейки (объединённые ячейки означают, что занятие происходит на всех неделях)
    twice_merges = str(ws.merged_cells).split(" ")
    merges = []

    for elem in twice_merges:
        m1, m2 = elem.split(":")
        merges.append(m1)
        merges.append(m2)

    # merges - список всех объединённых ячеек

    table = []
    list_of_cells = []

    days_of_week = ['', '', '', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    # формируем список данных из всех ячеек
    for num in range(5, 19):
        for letter in "BCDEFGH":
            cell = parse(ws[letter + str(num)].value)
            # если в ячейке нет данных, мы её пропускаем
            if cell is None:
                continue
            # определяем по каким неделям проходит пара, добавляем соответствующее значение каждой ячейке
            for elem in cell:
                if (letter + str(num)) in merges:
                    week = 'every week'
                else:
                    week = "upper week" if num % 2 != 0 else "lower week"
                table.append([*elem, week])

    # проверка сдвоенных пар. Если таковые есть - меняем значения joined, start_time/start_time_s и end_time/end_time_s
    for i in range(len(table)):
        for j in range(i + 1, len(table)):
            cell_1, cell_2 = table[i], table[j]
            if cell_1[7] == cell_2[7]:
                if cell_1[0] == cell_2[0] and cell_1[8] == cell_2[8] and cell_1[-1] == cell_2[-1] and cell_1[8] != 'Военная подготовка':
                    if cell_1[1] == "09:00" and cell_2[1] == "10:45":
                        cell_1[3:5] = "10:45", "12:15"
                        cell_1[9], cell_2[9] = True, True
                    elif cell_1[1] == "10:45" and cell_2[1] == "13:00":
                        cell_1[3:5] = "13:00", "14:30"
                        cell_1[9], cell_2[9] = True, True
                    elif cell_1[1] == "13:00" and cell_2[1] == "14:45":
                        cell_1[3:5] = "14:45", "16:15"
                        cell_1[9], cell_2[9] = True, True
                    elif cell_1[1] == "14:45" and cell_2[1] == "16:30":
                        cell_1[3:5] = "16:30", "18:00"
                        cell_1[9], cell_2[9] = True, True
                    elif cell_1[1] == "16:30" and cell_2[1] == "18:15":
                        cell_1[3:5] = "18:15", "19:45"
                        cell_1[9], cell_2[9] = True, True
                    elif cell_1[1] == "18:15" and cell_2[1] == "20:00":
                        cell_1[3:5] = "20:00", "21:30"
                        cell_1[9], cell_2[9] = True, True

                    # cell_2[1:5] = None, None, *cell_2[1:3]

    table_tmp = []
    for cell in table:
        if cell[9] and cell[3] is None:
            continue
        table_tmp.append(cell)
    table = table_tmp
    def formate_date(date):
        # "2023-09-04T00:00:00"
        d, m = date.split('.')
        return f"{year}-{m}-{d}"

    # создаём словарь из всех данных
    list_of_lessons = []
    list_of_days = []

    for elem in table:

        days = elem[0][1:-1].split('-')
        tmp_dict = dict()
        tmp_dict[f"{elem[1]}-{elem[2]}"] = {
                'date': formate_date(days[0]),
                'time_start': elem[1],
                'time_end': elem[2],
                'time_start_s': elem[3],
                'time_end_s': elem[4],
                'lector': elem[5],
                'room': elem[6],
                'type': elem[7],
                'subject': elem[8],
                'joined': elem[9],
                'week': elem[10]
        }
        list_of_lessons.append(tmp_dict)
        list_of_days.append(formate_date(days[0]))
        if len(days) == 1:
            pass
        else:
            new_date = date.fromisoformat(formate_date(days[0]))
            end_date = date.fromisoformat(formate_date(days[1]))

            count_days = 7
            if elem[10] != 'every week':
                count_days = 14
            delta = timedelta(count_days)
            for i in range(31):
                if new_date != end_date:
                    new_date += delta
                    tmp_dict = dict()
                    tmp_dict[f"{elem[1]}-{elem[2]}"] = {
                        'date': new_date.isoformat(),
                        'time_start': elem[1],
                        'time_end': elem[2],
                        'time_start_s': elem[3],
                        'time_end_s': elem[4],
                        'lector': elem[5],
                        'room': elem[6],
                        'type': elem[7],
                        'subject': elem[8],
                        'joined': elem[9],
                        'week': elem[10]
                    }
                    list_of_days.append(new_date.isoformat())
                    list_of_lessons.append(tmp_dict)

    data = dict()
    list_of_days = sorted(list(set(list_of_days)))
    for _ in list_of_days:
        tmp = []
        for lesson in list_of_lessons:
            for key, value in lesson.items():
                if value.get('date') == _:
                    tmp.append(lesson)

        def get_time(x):
            a = int(list(tmp[x].items())[0][0].split('-')[0].split(':')[0])
            return a

        for i in range(len(tmp) - 1):
            for j in range(len(tmp) - i - 1):
                if get_time(j) > get_time(j + 1):
                    tmp[j], tmp[j+1] = tmp[j+1], tmp[j]
        data[_] = tmp

    def datetime_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    serialized_data = {datetime_serializer(key): datetime_serializer(value) for key, value in data.items()}
    with open(f'data/data {file_name}.json', 'w') as outfile:
        json.dump(serialized_data, outfile, default=datetime_serializer, indent=4, separators=(',', ': '),
                  sort_keys=True)

    if os.path.exists(f'data/{file_name}.xlsx'):
        os.remove(f'data/{file_name}.xlsx')
    else:
        print("Doesn't exist")


