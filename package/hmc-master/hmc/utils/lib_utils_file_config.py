"""
Library Features:

Name:          lib_utils_file_config
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging

from hmc.utils.lib_utils_op_dict import updateDictValue
from hmc.utils.lib_utils_apps_file import importFileDict

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import ConfigTags

from hmc.driver.manager.drv_manager_debug import Exc

# Log
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# --------------------------------------------------------------------------------
# Method to get configuration file (static and dynamic)
def getFileConfig(sFileName, sVarName='var', oTags=ConfigTags):

    # Get source in file containing dictionary
    [oFileData, bFileData] = importFileDict(sFileName, DataName=sVarName)

    if bFileData:

        for oTagKey, oTagValue in iter(oTags.items()):
            sTag = list(oTagValue.keys())[0]
            oValue = list(oTagValue.values())[0]
            if oValue:
                updateDictValue(oFileData, sTag, oValue)
            else:
                pass

    else:
        Exc.getExc(' =====> ERROR: variable(s) file ' + sFileName + ' NOT FOUND!', 1, 1)

    return oFileData, bFileData
# --------------------------------------------------------------------------------
