"""
Class Features

Name:          drv_runner_info
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
from os.path import join, exists

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_args import sFileExec as FileExec_Default
from hmc.default.lib_default_tags import ConfigTags, StaticTags, DynamicTags
from hmc.default.lib_default_settings import FileSettings
from hmc.default.lib_default_datastatic import DataStatic as DataStatic_Default
from hmc.default.lib_default_datadynamic import DataDynamic as DataDynamic_Default
from hmc.default.lib_default_time import DataTime as DataTime_Default
from hmc.default.lib_default_namelist import DataNamelist as DataNamelist_Default
from hmc.default.lib_default_namelist import FileNamelist as FileNamelist_Default

from hmc.utils.lib_utils_apps_process import makeProcess
from hmc.utils.lib_utils_op_system import copyFile

from hmc.driver.manager.drv_manager_debug import Exc

# Log
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class RunnerInfo
class HMC_Runner_Info:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataVarStatic = {}
    oDataVarDynamic = {}
    oDataTime = {}

    oDataNML = {}
    sFileNML = None

    bDataExec = False
    sFileExec = None
    sPathExec = None
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
                 FileNameExec=FileExec_Default):

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
        self.sLineExec = ''
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compose command-line
    def collectInfo(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Collect model info ... ')

        # Check executable forcing Data (point and gridded)
        self.bDataExec = self.__checkExecData()

        # Data condition
        if self.bDataExec is True:

            # Get executable application
            self.sFileExec, self.sPathExec = self.__getExecApp()

            # Get executable command-line
            self.sLineExec = self.__getExecLine()

            # Info end (ok)
            oLogStream.info(' ---> Collect model info ... OK')
        else:
            # Info end (failed)
            oLogStream.info(' ---> Collect model info ... FAILED')
            Exc.getExc(' =====> ERROR: executable forcing Data are not sufficient to run model correctly!', 2, 1)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Return variable(s)
        return self.sLineExec, self.sPathExec
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to check executable Data
    def __checkExecData(self):

        # Get Data forcing availability threshold
        dDataForcingThr = self.oDataSettings['ParamsInfo']['HMC_Data']['ForcingDataThr']
        # Get Data forcing availability (point and gridded)
        dDataForcingPercG = self.oDataVarDynamic['DataAnalysis']['Gridded']
        dDataForcingPercP = self.oDataVarDynamic['DataAnalysis']['Point']

        # Check condition(s) forcing Data gridded
        if (dDataForcingPercG >= dDataForcingThr) and (dDataForcingPercP >= dDataForcingThr):
            bDataExec = True
        elif dDataForcingPercG < dDataForcingThr:
            bDataExec = False   # mandatory
            Exc.getExc(' =====> WARNING: executable available forcing gridded data are less than '
                       'Data forcing threshold! '
                       'DataPerc: ' + str(dDataForcingPercG) + ' DataThr: ' + str(dDataForcingThr), 2, 1)
        elif (dDataForcingPercG >= dDataForcingThr) and (dDataForcingPercP < dDataForcingThr):
            bDataExec = True
            Exc.getExc(' =====> WARNING: executable available forcing gridded data are less than '
                       'Data forcing threshold! '
                       'DataPerc: ' + str(dDataForcingPercP) + ' DataThr: ' + str(dDataForcingThr), 2, 1)

        # Return variable(s)
        return bDataExec

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get executable application
    def __getExecApp(self):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ----> Get model executable ... ')

        # Get information
        sFileExec_Source = join(self.oDataSettings['ParamsInfo']['Run_Path']['PathLibrary'],
                                self.sFileExec)

        sPathExec_Dest = self.oDataSettings['ParamsInfo']['Run_Path']['PathExec']
        sFileExec_Dest = join(sPathExec_Dest,
                              self.oDataSettings['ParamsInfo']['Run_VarExec']['RunModelExec'])

        # Check executable file availability
        if exists(sFileExec_Source):
            try:

                # Copy exec file process from source (library) to destination (run) folder
                copyFile(sFileExec_Source, sFileExec_Dest)

                # Make executable file process
                makeProcess(sFileExec_Dest)

                # Info end (ok)
                oLogStream.info(' ----> Get model executable ... OK')

                # Return variable(s)
                return sFileExec_Dest, sPathExec_Dest

            except BaseException:
                # Info end (fail)
                oLogStream.info(' ----> Get model executable ... FAILED!')
                Exc.getExc(' =====> ERROR: executable file ' + sFileExec_Source + ' NOT SET!', 1, 1)
        else:
            # Info end (fail)
            oLogStream.info(' ----> Get model executable ... FAILED!')
            Exc.getExc(' =====> ERROR: executable file ' + sFileExec_Source + ' NOT FOUND!', 1, 1)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get command-line
    def __getExecLine(self):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ----> Get model command-line ... ')

        # Define command line
        try:
            # Get information from global workspace
            sCLine = self.oDataSettings['ParamsInfo']['Run_VarExec']['RunModelCLine']
            sLineExec = ' '.join(filter(None, (self.sFileExec, sCLine)))
            # Info end (ok)
            oLogStream.info(' ----> Get model command-line ... OK')
            # Return variable
            return sLineExec
        except BaseException:
            # Info end (fail)
            oLogStream.info(' ----> Get model command-line ... FAILED!')
            Exc.getExc(' =====> ERROR: command line not correctly defined', 1, 1)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
