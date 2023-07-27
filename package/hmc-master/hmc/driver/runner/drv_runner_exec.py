"""
Class Features

Name:          drv_runner_exec
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
import time
import os

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_args import sFileExec as FileExec_Default
from hmc.default.lib_default_tags import ConfigTags, StaticTags, DynamicTags
from hmc.default.lib_default_settings import FileSettings
from hmc.default.lib_default_datastatic import DataStatic as DataStatic_Default
from hmc.default.lib_default_datadynamic import DataDynamic as DataDynamic_Default
from hmc.default.lib_default_time import DataTime as DataTime_Default
from hmc.default.lib_default_namelist import DataNamelist as DataNamelist_Default
from hmc.default.lib_default_namelist import FileNamelist as FileNamelist_Default

from hmc.utils.lib_utils_apps_process import checkProcess, execProcess

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class RunnerExec
class HMC_Runner_Exec:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataVarStatic = {}
    oDataVarDynamic = {}
    oDataTime = {}

    oDataNML = {}
    sFileNML = None

    sFileExec = None
    sLineExec = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method ClassInit
    def __init__(self, DataSettings=FileSettings,
                 DataTags=ConfigTags,
                 DataVarStatic=DataStatic_Default,
                 DataVarDynamic=DataDynamic_Default,
                 DataTime=DataTime_Default,
                 DataNamelist=DataNamelist_Default,
                 FileNamelist=FileNamelist_Default,
                 FileNameExec=FileExec_Default,
                 PathNameExec='/'):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = DataSettings
        self.oDataTags = DataTags
        self.oDataVarStatic = DataVarStatic
        self.oDataVarDynamic = DataVarDynamic
        self.oDataTime = DataTime

        self.oDataNML = DataNamelist
        self.sFileNML = FileNamelist

        self.sFileExec = FileNameExec
        self.sPathExec = PathNameExec
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compose command-line
    def runExecution(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Execute model run ... ')

        # Run executable application
        self.__runExecApp()

        # Info end
        oLogStream.info(' ---> Execute model run ... OK')
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to run executable application
    def __runExecApp(self):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ----> Run model executable ... ')

        try:
            # Check process instance
            #checkProcess(self.sFileExec, self.sPathExec)
            oLogStream.info(' ----> WAIT 5 seconds before execution ...')
            time.sleep(5)
            oLogStream.info(' ----> WAIT 5 seconds before execution ... DONE')
            
            # Execute process instance
            sStdOut, sStdErr, iStdExit = execProcess(self.sFileExec, self.sPathExec)
            # Info end (ok)
            oLogStream.info(' ----> Run model executable ... OK')
        except BaseException:
            # Info end (fail)
            oLogStream.info(' ----> Run model executable ... FAILED!')
            Exc.getExc(' =====> ERROR: run model FAILED!', 1, 1)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
