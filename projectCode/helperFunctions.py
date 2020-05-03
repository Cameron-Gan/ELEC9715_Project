import math
from datetime import datetime, timedelta


def floor_ft(dt, delta):
    return datetime.min + math.floor((dt - datetime.min) / delta) * delta


def convert_to_datetime(period):
    current = datetime.now()
    current_floored = floor_ft(current, timedelta(minutes=30))
    period = period * 0.5
    period = timedelta(hours=period)
    return current_floored + period
