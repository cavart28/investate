"""A few simple functions to handle files"""

import pickle
import os
import pandas as pd
from PyPDF2 import PdfFileMerger, PdfFileReader
from openpyxl import load_workbook
import glob
from collections import defaultdict


def pickle_dump(obj, path):
    """
    Dump a pickle
    """
    with open(path, 'wb') as outfile:
        return pickle.dump(obj, outfile)


def pickle_load(path):
    """
    Load a pickle
    """
    with open(path, 'rb') as pickle_in:
        return pickle.load(pickle_in)


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

    merger = PdfFileMerger()
    for filename in pdf_files:
        merger.append(PdfFileReader(filename, 'rb'))
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
        writer.sheets = dict(
            (ws.title, ws) for ws in writer.book.worksheets)
    except IOError:
        # file does not exist yet, we will create it
        pass

    # write out the new sheet
    dataframe.to_excel(writer, sheet_name=sheet_name)

    # save the workbook
    writer.save()


def make_file_df(root_dir, extension='.wav'):
    """
    Goes recursively through root_dir and make a df with the filenames with matching extension. The enclosing
    subfolders are recorded in the df too. The goal being able to easily select sets of filenames based on
    their origin, typically when the folder name are meaningful for train/test or contain important meta data
    about the files.

    :param root_dir: a string of the path to the folder of interest
    :param extension: the extension of interest
    :return: a dataframe
    """

    dict_for_df = defaultdict(list)
    n_folders = 0

    for full_path in glob.iglob(root_dir + f'/**/*{extension}',
                                recursive=True):
        if len(full_path.split('/')) > n_folders:
            n_folders = len(full_path.split('/')) - 1

    for full_path in glob.iglob(root_dir + f'/**/*{extension}',
                                recursive=True):
        split = full_path.split('/')
        dict_for_df['filename'].append(split[-1])
        dict_for_df['full_path'].append(full_path)
        for idx, folder in enumerate(split[:-1]):
            dict_for_df[idx].append(folder)
        if n_folders > idx:
            for i in range(idx + 1, n_folders):
                dict_for_df[i].append(None)
    return pd.DataFrame(dict_for_df)
