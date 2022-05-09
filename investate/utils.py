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
        func = defaultdict_of_depth(
            depth - 1, lambda: defaultdict_of_depth(1, default_func)
        )
        return func

<<<<<<< HEAD

def ts_to_date_string(ts, div=1e3):
    t = datetime.fromtimestamp(ts / div)
    return '{:%Y-%m-%d %H:%M:%S}'.format(t)
=======

import os
import datetime
from matplotlib.backends.backend_pdf import PdfPages
from PyPDF2 import PdfFileMerger, PdfFileReader
import pandas as pd
from openpyxl import load_workbook
import pickle
import glob


def merge_pdf_in_folder(directory_path, output_name='combined_pdf.pdf', delete=False):
    """
    Finds all pdf within the directory and merge them into one single pdf

    :param directory_path: seed directory
    :param output_name: name of the output file
    :param delete: whether or not to remove the original pdfs
    :return: creates a single pdf combining all

    """
    pdf_files = [i for i in os.listdir(directory_path) if i[-4:] == '.pdf']
    pdf_files = [os.path.join(directory_path, i) for i in pdf_files]
    print(pdf_files)

    merger = PdfFileMerger()
    for filename in pdf_files:
        merger.append(PdfFileReader(file(filename, 'rb')))
    merger.write(directory_path + output_name)

    if delete:
        for filename in pdf_files:
            os.remove(filename)


def add_frame_to_workbook(filename, tabname, dataframe):
    """
    Save a dataframe to a workbook tab with the filename and tabname

    :param filename: filename to create, can use strptime formatting
    :param tabname: tabname to create, can use strptime formatting
    :param dataframe: dataframe to save to workbook
    :return: None
    """

    sheet_name = tabname

    # create a writer for this month and year
    writer = pd.ExcelWriter(filename, engine='openpyxl')

    try:
        # try to open an existing workbook
        writer.book = load_workbook(filename)

        # copy existing sheets
        writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
    except IOError:
        # file does not exist yet, we will create it
        pass
>>>>>>> 963bbcaeebd03c97915845e0b14e1dcae8134167


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

<<<<<<< HEAD
    date = time.strptime(date, str_format)
    new_date = datetime.date(date.tm_year, date.tm_mon, date.tm_mday) + datetime.timedelta(n_days)

    return new_date.strftime(str_format)
=======
    dict_for_df = defaultdict(list)
    n_folders = 0

    for full_path in glob.iglob(root_dir + f'/**/*{extension}', recursive=True):
        if len(full_path.split('/')) > n_folders:
            n_folders = len(full_path.split('/')) - 1

    for full_path in glob.iglob(root_dir + f'/**/*{extension}', recursive=True):
        split = full_path.split('/')
        dict_for_df['filename'].append(split[-1])
        dict_for_df['full_path'].append(full_path)
        for idx, folder in enumerate(split[:-1]):
            dict_for_df[idx].append(folder)
        if n_folders > idx:
            for i in range(idx + 1, n_folders):
                dict_for_df[i].append(None)
    return pd.DataFrame(dict_for_df)


from datetime import datetime


def ts_to_date_string(ts, div=1e3):
    t = datetime.fromtimestamp(ts / div)
    return '{:%Y-%m-%d %H:%M:%S}'.format(t)


def date_string_to_ts(date_string):
    element = datetime.strptime(date_string, '%Y-%m-%d%H:%M:%S')
    return datetime.timestamp(element) * 1000
>>>>>>> 963bbcaeebd03c97915845e0b14e1dcae8134167
