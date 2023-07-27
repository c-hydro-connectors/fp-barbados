# -------------------------------------------------------------------------------------
# Library
import numpy as np

from netCDF4 import Dataset
from datetime import datetime

from os import remove
from os.path import join, exists
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to add time in a unfilled string (path or filename)
def fill_tags2string(string_raw, tags_format=None, tags_filling=None):

    apply_tags = False
    if string_raw is not None:
        for tag in list(tags_format.keys()):
            if tag in string_raw:
                apply_tags = True
                break

    if apply_tags:
        string_filled = string_raw.format(**tags_format)

        for tag_format_name, tag_format_value in list(tags_format.items()):

            if tag_format_name in list(tags_filling.keys()):
                tag_filling_value = tags_filling[tag_format_name]
                if tag_filling_value is not None:

                    if isinstance(tag_filling_value, datetime):
                        tag_filling_value = tag_filling_value.strftime(tag_format_value)

                    string_filled = string_filled.replace(tag_format_value, tag_filling_value)

        string_filled = string_filled.replace('//', '/')
        return string_filled
    else:
        return string_raw
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to delete time-series filename
def delete_file_cell(path_ts, filename_ts='%04d.nc', cells=None):

    if cells is not None:
        for i, cell in enumerate(cells):

            filename_ts_def = filename_ts % cell
            file_ts = join(path_ts, filename_ts_def)
            if exists(file_ts):
                remove(file_ts)

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to check time-series filename availability
def check_filename(path_ts, path_grid, filename_ts='%04d.nc',
                   filename_grid='TUW_WARP5_grid_info_2_3.nc', var_cell='cell'):

    dset_grid = Dataset(join(path_grid, filename_grid), 'r')
    cells = np.unique(dset_grid.variables[var_cell][:])

    n = cells.__len__()

    file_available = np.ones(n, dtype=np.bool)
    file_available[:] = False
    for i, cell in enumerate(cells):

        filename_ts_def = filename_ts % cell
        file_ts = join(path_ts, filename_ts_def)
        if exists(file_ts):
            file_available[i] = True

    if np.any(file_available == False):
        return False
    else:
        return True
# -------------------------------------------------------------------------------------
