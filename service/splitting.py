from entity.day import DayEntry


def split_overlapping(events):
    date_counter = {}
    for event in events:
        if event.date not in date_counter:
            date_counter[event.date] = []
        date_counter[event.date].append(event)

    flattened_events = []
    for date, date_events in date_counter.items():
        flattened_events.extend(flatten(date_events))

    return flattened_events


def flatten(events: [DayEntry]):
    flattened_events = events
    if len(events) > 2:
        splitted_events = flatten(events[:2])
        index = len(splitted_events) - 1
        splitted_events.extend(events[2:])
        flattened_events = splitted_events[:index]
        flattened_events.extend(flatten(splitted_events[index:]))
    elif len(events) == 2:
        if is_same_start(*events):
            before = DayEntry(events[1].date, events[1].start, min(events[0].end, events[1].end), events[1].comment,
                              events[1].label)
            after = DayEntry(events[0].date, min(events[0].end, events[1].end), max(events[0].end, events[1].end),
                             events[0].comment, events[0].label)

            flattened_events = [before, after]

        elif is_in_between(*events):
            before = DayEntry(events[0].date, events[0].start, events[1].start, events[0].comment, events[0].label)
            middle = events[1]
            after = DayEntry(events[0].date, events[1].end, events[0].end, events[0].comment, events[0].label)

            if after.timediff.total_seconds() <= 0:
                flattened_events = [before, middle]
            else:
                flattened_events = [before, middle, after]

    return flattened_events


def is_same_start(a: DayEntry, b: DayEntry):
    """
    a.start = 16:00
    b.start = 16:00
    Returns:
        True, if a.start == b.start
    """
    return a.start == b.start


def is_in_between(a: DayEntry, b: DayEntry):
    """
    a.start = 16:00
    a.end = 17:00

    b.start = 16:30
    b.end = 16:50

    """
    return a.end > b.start
