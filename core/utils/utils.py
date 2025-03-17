from datetime import datetime

def get_current_english_weekday():
    weekday_map = {
        0: 'monday',
        1: 'tuesday',
        2: 'wednesday',
        3: 'thursday',
        4: 'friday',
        5: 'saturday',
        6: 'sunday'
    }
    current_weekday_number = datetime.today().weekday()
    return weekday_map[current_weekday_number]
