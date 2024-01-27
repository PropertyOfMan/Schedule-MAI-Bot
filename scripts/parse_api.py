days = {'Пн': 'Понедельник', 'Вт': 'Вторник',
        'Ср': 'Среда', 'Чт': 'Четверг',
        'Пт': 'Пятница', 'Сб': 'Суббота'}

times = {"9:00": "[1]", "10:45": "[2]", "13:00": "[3]",
         "14:45": "[4]", "16:30": "[5]", "18:15": "[6]", "20:00": "[7]"}


def parse(curr_date, data):
    lines = []
    curr_date = '{2}.{1}.{0}'.format(*str(curr_date).split('-'))
    day = data.get(curr_date)
    lines.append(f'<b>Дата: {curr_date} ({days.get(day.get('day'))})</b>')
    for pair in day.get('pairs').values():
        name = list(pair.keys())[0]
        info = list(pair.values())[0]
        time_start = info.get('time_start')[:-3]
        pair_num = times.get(time_start)
        pair_type = list(info.get('type').keys())[0]
        time_end = info.get('time_end')[:-3]
        room = list(info.get('room').values())[0]
        lector = list(info.get('lector').values())[0]

        lines.append(f'<b>{pair_num}</b> <i>{name}</i>')
        lines.append(f'{pair_type}  {time_start}-{time_end}  {room}')
        lines.append(f'{lector}\n' if lector != '' else '---\n')

    return '\n'.join(lines)
