"""Useful and general tools"""

from collections import defaultdict
from datetime import datetime
import os
import datetime
from PyPDF2 import PdfFileMerger, PdfFileReader
import pandas as pd
from openpyxl import load_workbook
import smtplib
import email.message


def defaultdict_of_depth(depth, default_func=list):
    """Create a default dict with default dict as default type, of any recursive depth"""
    if depth == 1:
        return defaultdict(default_func)
    else:
        func = defaultdict_of_depth(
            depth - 1, lambda: defaultdict_of_depth(1, default_func)
        )
        return func


class keydefaultdict(defaultdict):
    """Similar to a default dict except that the default value is a function of the key"""

    def __init__(self, key_func):
        self.key_func = key_func

    def __missing__(self, key):
        return self.key_func(key)


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


def date_string_to_ts(date_string):
    element = datetime.strptime(date_string, '%Y-%m-%d%H:%M:%S')
    return datetime.timestamp(element) * 1000


def ts_to_date_string(ts, div=1e3):
    t = datetime.fromtimestamp(ts / div)
    return '{:%Y-%m-%d %H:%M:%S}'.format(t)


def send_email(subject,
               content,
               recipients,
               username,
               password,
               from_email=None):
    if from_email is None:
        from_email = username
    m = email.message.Message()
    m['From'] = from_email
    m['To'] = recipients
    m['Subject'] = subject
    m.set_payload(content);

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(username, password)
        server.sendmail(m['From'], m['To'], m.as_string())
        server.quit()
        print('email sent')
    except Exception as e:
        print('email not sent, {}'.format(e))
