# -------------------------------------------------------------------------------------
# Library
import numpy as np
from scipy.interpolate import griddata
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to clip data 2D/3D using a min/max threshold(s) and assign a missing value
def clip_map(map, valid_range=[None, None], missing_value=None):

    # Set variable valid range
    if valid_range is not None:
        if valid_range[0] is not None:
            valid_range_min = float(valid_range[0])
        else:
            valid_range_min = None
        if valid_range[1] is not None:
            valid_range_max = float(valid_range[1])
        else:
            valid_range_max = None
        # Set variable missing value
        if missing_value is None:
            missing_value_min = valid_range_min
            missing_value_max = valid_range_max
        else:
            missing_value_min = missing_value
            missing_value_max = missing_value

        # Apply min and max condition(s)
        if valid_range_min is not None:
            map = map.where(map >= valid_range_min, missing_value_min)
        if valid_range_max is not None:
            map = map.where(map <= valid_range_max, missing_value_max)

        return map
    else:
        return map

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to interpolate points to grid
def interpolate_point2map(lons_in, lats_in, values_in, lons_out, lats_out, nodata=-9999, interp='nearest'):

    values_out = griddata((lons_in.ravel(), lats_in.ravel()), values_in.ravel(),
                          (lons_out, lats_out), method=interp,
                          fill_value=nodata)
    return values_out
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to scale data using a mean-std scaling method
def mean_std(src_nrt, src_dr, ref_dr):

    return ((src_nrt - np.mean(src_dr)) /
            np.std(src_dr)) * np.std(ref_dr) + np.mean(ref_dr)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to scale data using mix-max normalized scaling method
def norm_min_max(src, ref):

    ref_min = np.min(ref) / 100
    ref_max = np.max(ref) / 100

    src = src / 100

    norm_src = (src - ref_min) / (ref_max - ref_min) * 100

    return norm_src
# -------------------------------------------------------------------------------------
