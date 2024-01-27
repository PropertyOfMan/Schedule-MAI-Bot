days = {'Пн': 'Понедельник', 'Вт': 'Вторник',
        'Ср': 'Среда', 'Чт': 'Четверг',
        'Пт': 'Пятница', 'Сб': 'Суббота'}

times = {"09:00": "[1]", "10:45": "[2]", "13:00": "[3]",
         "14:45": "[4]", "16:30": "[5]", "18:15": "[6]", "20:00": "[7]"}
times_joined = {"09:00": "[1-2]", "10:45": "[2-3]", "13:00": "[3-4]",
                "14:45": "[4-5]", "16:30": "[5-6]", "18:15": "[6-7]"}


def inf(pairs):
    lines = list()
    i = 1
    for pair in pairs:
        info = list(pair.items())[0][1]
        lines.append(f'<b>{times.get(info.get(
            'time_start')) if not info.get('joined') else times_joined.get(info.get('time_start'))}</b>'
                     f' <i>{info.get('subject')}</i>')
        if info.get('joined'):
            lines.append(f'Сдвоенная пара {info.get('type')}   {info.get('time_start')}-{info.get('time_end_s')}  {info.get('room')}')
        else:
            lines.append(f'{info.get('type')}  {info.get('time_start')}-{info.get('time_end')}  {info.get('room')}')
        lines.append(f'{info.get('lector') if info.get('lector') is not None else '---'}\n')
        i += 1
    return '\n'.join(lines)