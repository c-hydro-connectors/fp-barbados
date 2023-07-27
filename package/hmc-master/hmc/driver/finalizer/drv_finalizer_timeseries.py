"""
Class Features

Name:          drv_finalizer_timeseries
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
from os.path import join, split
from copy import deepcopy

from hmc.default.lib_default_args import sLoggerName

from hmc.default.lib_default_tags import ConfigTags, DynamicTags
from hmc.default.lib_default_settings import FileSettings
from hmc.default.lib_default_datastatic import DataStatic as DataStatic_Default
from hmc.default.lib_default_datadynamic import DataDynamic as DataDynamic_Default
from hmc.default.lib_default_time import DataTime as DataTime_Default

from hmc.data_dynamic.lib_datadynamic_results import getFilePoint
from hmc.data_dynamic.lib_datadynamic_timeseries import writeTS_Default, writeTS_Dewetra

from hmc.utils.lib_utils_apps_tags import updateRunTags, mergeRunTags
from hmc.utils.lib_utils_op_dict import mergeDict, getDictValue
from hmc.utils.lib_utils_apps_file import copyFile, createFolder
from hmc.utils.lib_utils_op_string import defineString

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class FinalizerTimeSeries
class HMC_Finalizer_TimeSeries:

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

    oDataAllocateTS = None

    oDataWorkspace = None
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

        self.oDataStaticPoint = DataVarStatic['DataAllocate']['Point']

        self.oDataOutputGridded = DataVarDynamic['DataOutput']['Gridded']
        self.oDataOutputPoint = DataVarDynamic['DataOutput']['Point']
        self.oDataOutputTimeSeries = DataVarDynamic['DataOutput']['TimeSeries']

        self.oDataStateGridded = DataVarDynamic['DataState']['Gridded']
        self.oDataStatePoint = DataVarDynamic['DataState']['Point']

        self.oDataAllocateTS = DataVarDynamic['DataAllocate']['TimeSeries']
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to write time series
    def writeData(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Write model time-series ... ')

        # Get data in point format
        self.oDataWorkspace = self.__getDataPoint(sRunMode, oRunArgs)

        # Write data point in timeseries generic format
        self.__writeDataTimeSeries(sRunMode, oRunArgs)

        # Info end
        oLogStream.info(' ---> Write model time-series ... OK')
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get Data in point format
    def __getDataPoint(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Get variable information
        oDataOutput = self.oDataOutputPoint
        oDataState = self.oDataStatePoint

        # Create Data archive dictionary
        oDataArchive = {'Output': oDataOutput, 'State': oDataState}
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Cycle(s) over Data archive(s)
        oDataWorkspace = {}
        for sArchiveKey, oArchiveValue in oDataArchive.items():

            # -------------------------------------------------------------------------------------
            # Get Data variable(s)
            oDataVars = getDictValue(oArchiveValue, ['FileVars', 'ARCHIVE', 'VarName'], 0)
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Check variable workspace
            if oDataVars:

                # -------------------------------------------------------------------------------------
                # Cycle(s) over variable(s)
                oDataWorkspace[sArchiveKey] = {}
                for sDataKey, oDataValue in oDataVars.items():

                    # -------------------------------------------------------------------------------------
                    # Info variable start
                    oLogStream.info(' ----> Get Variable ' + sDataKey + ' PointData ... ')
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Cycle(s) over time(s)
                    oDataWorkspace[sArchiveKey][sDataKey] = {}
                    for iDataTime, sDataTime in enumerate(self.oDataTime['TimeStep']):

                        # -------------------------------------------------------------------------------------
                        # Define tags and filename LOAD
                        oDynamicTags = updateRunTags({'Year': sDataTime[0:4],
                                                           'Month': sDataTime[4:6], 'Day': sDataTime[6:8],
                                                           'Hour': sDataTime[8:10], 'Minute': sDataTime[10:12],
                                                           'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                          deepcopy(DynamicTags))
                        oTagsUpd = mergeRunTags(oDynamicTags, self.oDataTags)

                        sFilePath_STEP = defineString(deepcopy(oArchiveValue['FilePath']), oTagsUpd)
                        sFileName_STEP = defineString(deepcopy(oArchiveValue['FileName']), oTagsUpd)

                        sFile_STEP = join(sFilePath_STEP, sFileName_STEP)
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Get Data
                        oDataPoint = getFilePoint(sFile_STEP)
                        # Store Data point
                        oDataWorkspace[sArchiveKey][sDataKey][sDataTime] = oDataPoint
                        # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Info variable start
                    oLogStream.info(' ----> Get Variable ' + sDataKey + ' PointData ... OK')
                    # -------------------------------------------------------------------------------------

            else:

                # -------------------------------------------------------------------------------------
                # Variable workspace not defined
                oDataWorkspace[sArchiveKey] = None
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Return Data
        return oDataWorkspace
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to write Data in timeseries format
    def __writeDataTimeSeries(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Get variable information
        oDataPoint = self.oDataStaticPoint
        oDataOutput = self.oDataOutputTimeSeries
        oDataAllocate = self.oDataAllocateTS

        # Get Data information
        oDataWorkspace_TS = self.oDataWorkspace

        # Get time information
        sTimeNow = self.sTimeNow
        sTimeFrom = self.oDataTime['TimeStep'][0]
        iEnsN = int(oRunArgs[2])

        # Get data sections
        oDataSection = getDictValue(oDataPoint, ['FileVars', 'Section', 'Data'], 0)
        # Create Data timeseries dictionary
        oDataTS = {'Output': oDataOutput}
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Cycle(s) over Data archive(s)
        for sKey_TS, oValue_TS in oDataTS.items():

            # -------------------------------------------------------------------------------------
            # Get Data variable(s)
            oInfoVars_TS = getDictValue(oValue_TS, ['FileVars', 'ARCHIVE', 'VarName'], 0)
            oInfoVars_DEW = getDictValue(oValue_TS, ['FileVars', 'DEWETRA', 'VarName'], 0)
            oInfoVars_SECTION = getDictValue(oValue_TS, ['FileVars', 'Section', 'Data'], 0)

            oDataVars_TS = getDictValue(oDataWorkspace_TS, [sKey_TS], 0)
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Check variable workspace
            if oInfoVars_TS is not None and oDataVars_TS is not None:

                # -------------------------------------------------------------------------------------
                # Cycle(s) over variable(s)
                for sDataKey_TS, oDataValue_TS in oDataVars_TS.items():

                    # -------------------------------------------------------------------------------------
                    # Info variable start
                    oLogStream.info(' ----> Save Variable ' + sDataKey_TS + ' TimeSeries ... ')
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Get variable Data
                    oVarInfo_TS = oInfoVars_TS[sDataKey_TS]
                    oVarData_TS = oDataVars_TS[sDataKey_TS]
                    # Get variable header
                    oVarHeader_TS = getDictValue(oDataAllocate, ['FileVars', 'ARCHIVE', sDataKey_TS, 'Attrs'])

                    if sDataKey_TS in oInfoVars_DEW:
                        oVarInfo_DEW = oInfoVars_DEW[sDataKey_TS]
                    else:
                        oVarInfo_DEW = None
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Define tags and filename TS
                    oDynamicTags_TS = updateRunTags({'Year': sTimeNow[0:4],
                                                       'Month': sTimeNow[4:6], 'Day': sTimeNow[6:8],
                                                       'Hour': sTimeNow[8:10], 'Minute': sTimeNow[10:12],
                                                       'RunMode': sRunMode, 'VarName': oVarInfo_TS['FileVar']},
                                                      deepcopy(DynamicTags))
                    oTagsUpd_TS = mergeRunTags(oDynamicTags_TS, self.oDataTags)

                    sFilePath_TS = defineString(deepcopy(oVarInfo_TS['FilePath']), oTagsUpd_TS)
                    sFileName_TS = defineString(deepcopy(oVarInfo_TS['FileName']), oTagsUpd_TS)

                    sFile_TS = join(sFilePath_TS, sFileName_TS)

                    # Create destination folder
                    createFolder(split(sFile_TS)[0])

                    if oVarInfo_DEW:
                        sFilePath_DEW = defineString(deepcopy(oVarInfo_DEW['FilePath']), oTagsUpd_TS)
                        sFileName_DEW = defineString(deepcopy(oVarInfo_DEW['FileName']), oTagsUpd_TS)

                        sFile_DEW = join(sFilePath_DEW, sFileName_DEW)

                        # Create destination folder
                        createFolder(split(sFile_DEW)[0])
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Create destination folder
                    createFolder(split(sFile_TS)[0])
                    # Write timeseries data to ASCII file in default format
                    writeTS_Default(sFile_TS, oVarData_TS, oVarHeader_TS)
                    # Write timeseries data to ASCII file in dewetra format
                    if oVarInfo_DEW:
                        writeTS_Dewetra(sFile_DEW, sTimeNow, sTimeFrom,
                                        oVarData_TS, None, oDataSection, 60, iEnsN, sRunMode)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Info variable end
                    oLogStream.info(' ----> Save Variable ' + sDataKey_TS + ' TimeSeries ... OK')
                    # -------------------------------------------------------------------------------------

            else:

                # -------------------------------------------------------------------------------------
                # No Data available
                pass
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Write data point in timeseries dewetra format
    def __writeDataDewetra(self, sRunMode, oRunArgs):

        '''
        # Convert array from float to string
        a1sDataObs = [a1dDataObs.tolist()]

        # Save update information
        oModelData = {}

        # Flag information
        oModelData['Line_01'] = 'Procedure=' + str(sRunType) + ' \n'
        oModelData['Line_02'] = 'DateMeteoModel=' + str(sTimeNow) + ' \n'
        oModelData['Line_03'] = 'DateStart=' + str(sTimeFrom) + ' \n'
        oModelData['Line_04'] = 'Temp.Resolution=' + str(iTimeRes) + ' \n'
        oModelData['Line_05'] = 'SscenariosNumber=' + str(int(iEnsN)) + ' \n'
        oModelData['Line_06'] = (' '.join(map(str, a1sDataObs[0]))) + ' \n'

        # Cycle(s) on Data dimension(s)
        sDigit = '%02d';
        for iEns in range(0, iEnsN):
            sLineName = 'Line_' + str(sDigit % (iEns + 7))

            a1dDataModel = a2dDataModel[iEns]
            a1sDataModel = [a1dDataModel.tolist()]

            oModelData[sLineName] = (' '.join(map(str, a1sDataModel[0]))) + ' \n'

        # Dictionary sorting
        oModelDataOrd = collections.OrderedDict(sorted(oModelData.items()))

        # Open ASCII file (to save all Data)
        oFileHandler = open(sFileName, 'w');

        # Write Data in ASCII file
        oFileHandler.writelines(oModelDataOrd.values())
        # Close ASCII file
        oFileHandler.close()

        print()




        '''
        pass
    # -------------------------------------------------------------------------------------