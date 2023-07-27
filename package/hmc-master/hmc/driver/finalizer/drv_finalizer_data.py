"""
Class Features

Name:          drv_finalizer_data
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
from os.path import join, split, exists
from copy import deepcopy

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import ConfigTags, StaticTags, DynamicTags
from hmc.default.lib_default_settings import FileSettings
from hmc.default.lib_default_datastatic import DataStatic as DataStatic_Default
from hmc.default.lib_default_datadynamic import DataDynamic as DataDynamic_Default
from hmc.default.lib_default_time import DataTime as DataTime_Default

from hmc.utils.lib_utils_apps_tags import updateRunTags, mergeRunTags

from hmc.utils.lib_utils_op_system import copyFile, createFolder
from hmc.utils.lib_utils_op_string import defineString

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class FinalizerData
class HMC_Finalizer_Data:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataVarStatic = {}
    oDataVarDynamic = {}

    sTimeNow = None
    oDataTime = {}

    oDataOutputGridded = None
    oDataOutputPoint = None

    oDataStateGridded = None
    oDataStatePoint = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method ClassInit
    def __init__(self, DataSettings=FileSettings,
                 DataTags=ConfigTags,
                 DataVarStatic=DataStatic_Default,
                 DataVarDynamic=DataDynamic_Default,
                 DataTime=DataTime_Default):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = DataSettings
        self.oDataTags = DataTags
        self.oDataVarStatic = DataVarStatic
        self.oDataVarDynamic = DataVarDynamic
        self.oDataTime = DataTime['DataTime']['TimeSummary']
        self.sTimeNow = DataTime['DataTime']['TimeNow']

        self.oDataOutputGridded = DataVarDynamic['DataOutput']['Gridded']
        self.oDataOutputPoint = DataVarDynamic['DataOutput']['Point']
        self.oDataOutputTimeSeries = DataVarDynamic['DataOutput']['TimeSeries']

        self.oDataStateGridded = DataVarDynamic['DataState']['Gridded']
        self.oDataStatePoint = DataVarDynamic['DataState']['Point']
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect data
    def collectData(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Collect model results ... ')

        # Collect data point
        self.__collectDataObs(sRunMode, oRunArgs)

        # Collect data point
        self.__collectDataPoint(sRunMode, oRunArgs)

        # Collect data gridded
        self.__collectDataGridded(sRunMode, oRunArgs)

        # Collect data timeseries
        self.__collectDataTimeSeries(sRunMode, oRunArgs)

        # Info end
        oLogStream.info(' ---> Collect model results ... OK')
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect data observed
    def __collectDataObs(self, sRunMode, oRunArgs):
        pass
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect data timeseries
    def __collectDataTimeSeries(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Get variable information
        oDataOutput = self.oDataOutputTimeSeries

        # Get time now
        sTimeNow = self.sTimeNow

        # Create Data archive
        oDataArchive = {'Output': oDataOutput}
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Cycle(s) over Data archive(s)
        for sArchiveKey, oArchiveValue in iter(oDataArchive.items()):

            # -------------------------------------------------------------------------------------
            # Get Data variable(s)
            oDataVars = oArchiveValue['FileVars']['ARCHIVE']['VarName']
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Cycle(s) over variable(s)
            for sDataKey, oDataValue in iter(oDataVars.items()):

                # -------------------------------------------------------------------------------------
                # Info variable start
                oLogStream.info(' ----> Variable ' + sDataKey + ' TimeSeries Data ... ')
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Get time reference (for time-series data is time now)
                sDataTime = sTimeNow

                # Define tags and filename LOAD
                oDynamicTags_LOAD = updateRunTags({'Year': sDataTime[0:4],
                                                   'Month': sDataTime[4:6], 'Day': sDataTime[6:8],
                                                   'Hour': sDataTime[8:10], 'Minute': sDataTime[10:12],
                                                   'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                  deepcopy(DynamicTags))
                oTagsUpd_LOAD = mergeRunTags(oDynamicTags_LOAD, self.oDataTags)

                sFilePath_LOAD = defineString(deepcopy(oArchiveValue['FilePath']), oTagsUpd_LOAD)
                sFileName_LOAD = defineString(deepcopy(oArchiveValue['FileName']), oTagsUpd_LOAD)

                sFile_LOAD = join(sFilePath_LOAD, sFileName_LOAD)
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Check file availability
                if exists(sFile_LOAD):

                    # -------------------------------------------------------------------------------------
                    # Define tags and filename SAVE
                    oDynamicTags_SAVE = updateRunTags({'Year': sTimeNow[0:4],
                                                       'Month': sTimeNow[4:6], 'Day': sTimeNow[6:8],
                                                       'Hour': sTimeNow[8:10], 'Minute': sTimeNow[10:12],
                                                       'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                      deepcopy(DynamicTags))
                    oTagsUpd_SAVE = mergeRunTags(oDynamicTags_SAVE, self.oDataTags)

                    sFilePath_SAVE = defineString(deepcopy(oDataValue['FilePath']), oTagsUpd_SAVE)
                    sFileName_SAVE = defineString(deepcopy(oDataValue['FileName']), oTagsUpd_LOAD)

                    sFile_SAVE = join(sFilePath_SAVE, sFileName_SAVE)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Create destination folder
                    createFolder(split(sFile_SAVE)[0])

                    # Archive file in a new folder
                    copyFile(sFile_LOAD, sFile_SAVE)
                    # -------------------------------------------------------------------------------------
                else:
                    # -------------------------------------------------------------------------------------
                    # Info variable end
                    Exc.getExc(
                        ' =====> WARNING: file ' + sFile_LOAD + ' for time ' + sDataTime +
                        ' is not available! Check run data!', 2, 1)
                    # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Info variable end
                oLogStream.info(' ----> Variable ' + sDataKey + ' TimeSeries Data ... OK')
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect data point
    def __collectDataPoint(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Get variable information
        oDataOutput = self.oDataOutputPoint
        oDataState = self.oDataStatePoint
        # Get time now
        sTimeNow = self.sTimeNow

        # Create Data archive
        oDataArchive = {'Output': oDataOutput, 'State': oDataState}
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Cycle(s) over Data archive(s)
        for sArchiveKey, oArchiveValue in iter(oDataArchive.items()):

            # -------------------------------------------------------------------------------------
            # Get Data variable(s)
            oDataVars = oArchiveValue['FileVars']['ARCHIVE']['VarName']
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Cycle(s) over variable(s)
            for sDataKey, oDataValue in iter(oDataVars.items()):

                # -------------------------------------------------------------------------------------
                # Info variable start
                oLogStream.info(' ----> Variable ' + sDataKey + ' Point Data ... ')
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Cycle(s) over time(s)
                for iDataTime, sDataTime in enumerate(self.oDataTime['TimeStep']):

                    # -------------------------------------------------------------------------------------
                    # Define tags and filename LOAD
                    oDynamicTags_LOAD = updateRunTags({'Year': sDataTime[0:4],
                                                       'Month': sDataTime[4:6], 'Day': sDataTime[6:8],
                                                       'Hour': sDataTime[8:10], 'Minute': sDataTime[10:12],
                                                       'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                      deepcopy(DynamicTags))
                    oTagsUpd_LOAD = mergeRunTags(oDynamicTags_LOAD, self.oDataTags)

                    sFilePath_LOAD = defineString(deepcopy(oArchiveValue['FilePath']), oTagsUpd_LOAD)
                    sFileName_LOAD = defineString(deepcopy(oArchiveValue['FileName']), oTagsUpd_LOAD)

                    sFile_LOAD = join(sFilePath_LOAD, sFileName_LOAD)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check file availability
                    if exists(sFile_LOAD):

                        # -------------------------------------------------------------------------------------
                        # Define tags and filename SAVE
                        oDynamicTags_SAVE = updateRunTags({'Year': sTimeNow[0:4],
                                                           'Month': sTimeNow[4:6], 'Day': sTimeNow[6:8],
                                                           'Hour': sTimeNow[8:10], 'Minute': sTimeNow[10:12],
                                                           'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                          deepcopy(DynamicTags))
                        oTagsUpd_SAVE = mergeRunTags(oDynamicTags_SAVE, self.oDataTags)

                        sFilePath_SAVE = defineString(deepcopy(oDataValue['FilePath']), oTagsUpd_SAVE)
                        sFileName_SAVE = defineString(deepcopy(oDataValue['FileName']), oTagsUpd_LOAD)

                        sFile_SAVE = join(sFilePath_SAVE, sFileName_SAVE)
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Create destination folder
                        createFolder(split(sFile_SAVE)[0])

                        # Archive file in a new folder
                        copyFile(sFile_LOAD, sFile_SAVE)
                        # -------------------------------------------------------------------------------------
                    else:
                        # -------------------------------------------------------------------------------------
                        # Info variable end
                        Exc.getExc(
                            ' =====> WARNING: file ' + sFile_LOAD + ' for time ' + sDataTime +
                            ' is not available! Check run data!', 2, 1)
                        # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Info variable end
                oLogStream.info(' ----> Variable ' + sDataKey + ' Point Data ... OK')
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect data gridded
    def __collectDataGridded(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Get variable information
        oDataOutput = self.oDataOutputGridded
        oDataState = self.oDataStateGridded
        # Get time now
        sTimeNow = self.sTimeNow

        # Create Data archive
        oDataArchive = {'Output': oDataOutput, 'State': oDataState}
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Cycle(s) over Data archive(s)
        for sArchiveKey, oArchiveValue in iter(oDataArchive.items()):

            # -------------------------------------------------------------------------------------
            # Get Data variable(s)
            oDataVars = oArchiveValue['FileVars']['ARCHIVE']['VarName']
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Cycle(s) over variable(s)
            for sDataKey, oDataValue in iter(oDataVars.items()):

                # -------------------------------------------------------------------------------------
                # Info variable start
                oLogStream.info(' ----> Variable ' + sDataKey + ' Gridded Data ... ')
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Cycle(s) over time(s)
                for iDataTime, sDataTime in enumerate(self.oDataTime['TimeStep']):

                    # -------------------------------------------------------------------------------------
                    # Define tags and filename LOAD
                    oDynamicTags_LOAD = updateRunTags({'Year': sDataTime[0:4],
                                                       'Month': sDataTime[4:6], 'Day': sDataTime[6:8],
                                                       'Hour': sDataTime[8:10], 'Minute': sDataTime[10:12],
                                                       'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                      deepcopy(DynamicTags))
                    oTagsUpd_LOAD = mergeRunTags(oDynamicTags_LOAD, self.oDataTags)

                    sFilePath_LOAD = defineString(deepcopy(oArchiveValue['FilePath']), oTagsUpd_LOAD)
                    sFileName_LOAD = defineString(deepcopy(oArchiveValue['FileName']), oTagsUpd_LOAD)

                    sFile_LOAD = join(sFilePath_LOAD, sFileName_LOAD)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check file availability
                    if exists(sFile_LOAD):

                        # -------------------------------------------------------------------------------------
                        # Define tags and filename SAVE
                        oDynamicTags_SAVE = updateRunTags({'Year': sTimeNow[0:4],
                                                           'Month': sTimeNow[4:6], 'Day': sTimeNow[6:8],
                                                           'Hour': sTimeNow[8:10], 'Minute': sTimeNow[10:12],
                                                           'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                          deepcopy(DynamicTags))
                        oTagsUpd_SAVE = mergeRunTags(oDynamicTags_SAVE, self.oDataTags)

                        sFilePath_SAVE = defineString(deepcopy(oDataValue['FilePath']), oTagsUpd_SAVE)
                        sFileName_SAVE = defineString(deepcopy(oDataValue['FileName']), oTagsUpd_LOAD)

                        sFile_SAVE = join(sFilePath_SAVE, sFileName_SAVE)
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Create destination folder
                        createFolder(split(sFile_SAVE)[0])

                        # Archive file in a new folder
                        copyFile(sFile_LOAD, sFile_SAVE)
                        # -------------------------------------------------------------------------------------
                    else:
                        # -------------------------------------------------------------------------------------
                        # Info variable end
                        Exc.getExc(
                            ' =====> WARNING: file ' + sFile_LOAD + ' for time ' + sDataTime +
                            ' is not available! Check run data!', 2, 1)
                        # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Info variable end
                oLogStream.info(' ----> Variable ' + sDataKey + ' Gridded Data ... OK')
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
