from datetime import datetime
from config import DATE_FORMAT


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True
    except:
        return False