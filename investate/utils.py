"""Useful and general tools"""

import pandas as pd
from collections import defaultdict
from datetime import datetime
import time
import os


def defaultdict_of_depth(depth, default_func=list):
    """Create a default dict with default dict as default type, of any recursive depth"""
    if depth == 1:
        return defaultdict(default_func)
    else:
        func = defaultdict_of_depth(depth - 1, lambda: defaultdict_of_depth(1, default_func))
        return func


def ts_to_date_string(ts, div=1e3):
    t = datetime.fromtimestamp(ts / div)
    return '{:%Y-%m-%d %H:%M:%S}'.format(t)


def date_string_to_ts(date_string, format="%Y-%m-%d%H:%M:%S", mult_fact=1000):
    element = datetime.strptime(date_string, format)
    return datetime.timestamp(element) * mult_fact


def add_days_to_date(date, n_days=1, str_format='%Y-%m-%d'):
    """
    >>> add_days_to_date('2022-03-25')
    '2011-06-01'
    >>> add_days_to_date('2022/03/25', str_format='%Y/%m/%d')
    '2022/03/26'
    """

    date = time.strptime(date, str_format)
    new_date = datetime.date(date.tm_year, date.tm_mon, date.tm_mday) + datetime.timedelta(n_days)

    return new_date.strftime(str_format)
