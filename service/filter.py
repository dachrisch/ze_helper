from entity.day import VacationDayEntry, DayEntry


def filter_vacations(day_entries: [DayEntry]):
    return list(filter(lambda entry: not entry.__class__ == VacationDayEntry, day_entries))


def filter_breaks(day_entries: [DayEntry]):
    return list(filter(lambda entry: not entry.comment == 'Pause', day_entries))
