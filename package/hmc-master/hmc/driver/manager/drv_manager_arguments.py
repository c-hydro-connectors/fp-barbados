"""
Class Features

Name:          drv_manager_arguments
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20161114'
Version:       '2.0.6'
"""

#######################################################################################
# Library
import logging

from copy import deepcopy

from hmc.default.lib_default_args import ConfigArgs, sLoggerName
from hmc.default.lib_default_tags import ConfigTags
from hmc.default.lib_default_settings import FileSettings
from hmc.utils.lib_utils_op_dict import getDictValues, DictObj
from hmc.utils.lib_utils_op_string import defineString

from hmc.utils.lib_utils_apps_tags import setRunTags
from hmc.utils.lib_utils_file_args import checkFileSettings, getDataSettings, getDataTime

from hmc.driver.manager.drv_manager_debug import Exc

# Log
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Dictionary to define file to be selected from settings
oFileTags = ['FileLog', 'FileVarStatic', 'FileVarDynamic']
oTimeTags = ['TimeNow']
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class to configure algorithm
class HMC_Arguments:

    # -------------------------------------------------------------------------------------
    # Variable(s)
    oDataSettings = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method time info
    def __init__(self,
                 FileSetting=ConfigArgs['FileSetting'],
                 Time=ConfigArgs['Time']):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.sFileSetting = FileSetting
        self.sTimeArg = Time
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to import argument(s)
    def importArgs(self):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Import argument(s) ... ')

        # Method to check settings file
        checkFileSettings(self.sFileSetting, oSettings=FileSettings)

        # Method to get data settings
        oDataSettings = getDataSettings(self.sFileSetting, oSettings=FileSettings)[0]
        # Method to get data tags
        oDataTags = setRunTags(Tags=ConfigTags, Settings=oDataSettings, SkipTags=[])

        # Define data settings object
        oDataSettings = DictObj(oDataSettings)
        oDataSettings.FileLog = defineString(
            deepcopy(getDictValues(oDataSettings, 'FileLog', value=[])[0]), oDataTags)
        oDataSettings.FileVarStatic = defineString(
            deepcopy(getDictValues(oDataSettings, 'FileVarStatic', value=[])[0]), oDataTags)
        oDataSettings.FileVarDynamic = defineString(
            getDictValues(oDataSettings, 'FileVarDynamic', value=[])[0], oDataTags)
        oDataSettings.TimeNow = getDataTime(self.sTimeArg)

        # Info end
        oLogStream.info(' ---> Import argument(s) ... OK')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Return variable(s)
        return oDataSettings
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
