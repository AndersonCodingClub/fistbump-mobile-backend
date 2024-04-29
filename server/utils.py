import os
import pytz
import datetime as dt


def _utc_to_cst(date):
    utc_zone = pytz.utc
    cst_zone = pytz.timezone('America/Chicago')
    date_utc = utc_zone.localize(date)
    date_cst = date_utc.astimezone(cst_zone)
    
    return date_cst

def conditional_convert(date):
    if os.environ.get('ON_SERVER', 'True') == 'True':
        return _utc_to_cst(date)
    return date

def get_today_date():
    return conditional_convert(dt.date.today())