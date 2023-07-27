"""
Class Features

Name:          lib_datadynamic_results
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""
#######################################################################################
# Library
import logging

from os.path import exists

from hmc.default.lib_default_args import sLoggerName

from hmc.driver.data.drv_data_io_type import Drv_Data_IO
from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to collect file output in point format
def getFilePoint(sFileName):

    # Check file availability
    if exists(sFileName):

        # Open file
        oDrv_IO = Drv_Data_IO(sFileName).oFileWorkspace
        oFile_DATA = oDrv_IO.oFileLibrary.openFile(sFileName, 'r')
        oDataArray = oDrv_IO.oFileLibrary.getVar(oFile_DATA)
        oDrv_IO.oFileLibrary.closeFile(oFile_DATA)

    else:
        # File not found
        oDataArray = None

    return oDataArray
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to collect file output in gridded format
def getFileGridded():
    pass
# -------------------------------------------------------------------------------------
