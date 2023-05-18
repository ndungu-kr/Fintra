import datetime


def convert_time(last_updated):
    date_format = "%Y-%m-%dT%H:%M:%S"
    last_updated = datetime.strptime(last_updated, date_format)
    return last_updated
