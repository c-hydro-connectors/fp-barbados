"""
Class Features

Name:          drv_builder_datadynamic_forcing_timeseries
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
from typing import Dict, Any

from numpy import full
from os.path import join
from copy import deepcopy

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import ConfigTags
from hmc.default.lib_default_settings import FileSettings
from hmc.default.lib_default_datastatic import DataStatic as DataStatic_Default
from hmc.default.lib_default_datadynamic import DataDynamic as DataDynamic_Default

from hmc.default.lib_default_time import DataTime as DataTime_Default

from hmc.time.lib_time import putTimeSummary

from hmc.utils.lib_utils_op_dict import getDictValue, checkDictKeys, mergeDict
from hmc.utils.lib_utils_op_var import convertVarType
from hmc.utils.lib_utils_op_list import findIndexElement

from hmc.data_dynamic.lib_datadynamic_forcing_ascii import getForcingTimeSeries_ASCII, saveForcingTimeSeries_ASCII

from hmc.driver.manager.drv_manager_debug import Exc

# Log
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class Builder DataDynamic Forcing TimeSeries
class HMC_Builder_DataDynamic_Forcing_TimeSeries:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataDynamic = {}

    sPathTemp = ''

    oSummaryTime = {}
    oDataTime = {}

    oDataStaticGridded = {}

    oDataDynamicTimeSeries_INIT = {}
    oDataDynamicTimeSeries_RUN = {}
    oDataDynamicTimeSeries_GET = {}

    a1bDataCheck_Obs = None

    oDataLinkTimeSeries = {'Dam':
                               {'VarDyn': 'DamQ',
                                'VarStatic': 'Dam',
                                'Tag': '$NAME_PLANT'},
                           'Intake':
                               {'VarDyn': 'IntakeQ',
                                'VarStatic': 'Intake',
                                'Tag': '$NAME_PLANT'}
                           }
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method ClassInit
    def __init__(self, DataSettings=FileSettings, DataTags=ConfigTags,
                 DataVarStatic=DataStatic_Default,
                 DataVarDynamic=DataDynamic_Default,
                 DataTime=DataTime_Default):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = DataSettings
        self.oDataTags = DataTags
        self.oDataDynamic = DataVarDynamic

        self.sPathTemp = DataSettings['ParamsInfo']['Run_Path']['PathTemp']

        self.oDataTime = DataTime
        self.oSummaryTime = DataTime['DataTime']['TimeSummary']

        self.sTimeRun = DataTime['DataTime']['TimeRun']

        self.oDataStaticPoint = DataVarStatic['DataAllocate']['Point']

        self.oDataDynamicTimeSeries_INIT = DataVarDynamic['DataForcing']['TimeSeries']
        self.oDataDynamicTimeSeries_RUN = DataDynamic_Default['DataAllocate']['TimeSeries']
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get dynamic file(s)
    def getFile(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Get data dynamic forcing timeseries ... ')

        # Method to get observed dynamic point file(s)
        self.__getFileTimeSeries_Obs(sRunMode, getDictValue(self.oDataDynamicTimeSeries_INIT, ['FileType']))

        # Info end
        oLogStream.info(' ---> Get data dynamic forcing timeseries ... OK')

        return self.oDataTime
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get observed dynamic timeseries file(s)
    def __getFileTimeSeries_Obs(self, sRunMode, iFileType):

        # -------------------------------------------------------------------------------------
        # Cycle(s) over time(s)
        sDataFlag = 'OBS'
        a1bDataCheck = full((len(self.oSummaryTime['TimeStep'])), False, dtype=bool)
        # Get time for timeseries
        sDataTime = self.sTimeRun
        iDataID = findIndexElement(self.oSummaryTime['TimeStep'], sDataTime)[0]

        # Get static variables
        oDataStaticVars = self.oDataStaticPoint['FileVars']
        # Get variable(s) link(s)
        oDataLinkTimeSeries = self.oDataLinkTimeSeries
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Define extra tags based on hydraulic structure PLANT_NAME
        oTagName = []
        for sDataStaticKey, oDataStaticValue in iter(oDataStaticVars.items()):

            if 'Data' in oDataStaticVars[sDataStaticKey]:
                if hasattr(oDataStaticVars[sDataStaticKey]['Data'], 'connections'):
                    oListConn = oDataStaticVars[sDataStaticKey]['Data'].connections
                    for sListKey, oListValue in iter(oListConn.items()):
                        oTagName = oTagName + oListValue
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Select OBS step(s)
        if sDataFlag in self.oSummaryTime['DataType'][iDataID]:

            # -------------------------------------------------------------------------------------
            # Check file type
            if iFileType == 1:

                # -------------------------------------------------------------------------------------
                # Iterate over variable link(s)
                oDataDynamicTimeSeries_CHECK_STEP = []
                a1bDataCheck_STEP = full((len(self.oSummaryTime['TimeStep'])), False, dtype=bool)
                for sLinkKeys, oLinkValue in oDataLinkTimeSeries.items():

                    # -------------------------------------------------------------------------------------
                    # Get variable information
                    sVarNameDyn = oLinkValue['VarDyn']
                    sVarNameStatic = oLinkValue['VarStatic']
                    sVarTag = oLinkValue['Tag']

                    # Info start
                    oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag +
                                    ' DataVariable: ' + sVarNameDyn + ' ... ')
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Iterate over connection(s)
                    oVarConnection = oDataStaticVars[sVarNameStatic]['Data'].connections

                    # Check connection(s) found
                    if oVarConnection:
                        for oConnKeys, oConnValues in oVarConnection.items():

                            # -------------------------------------------------------------------------------------
                            # Iterate over connection point(s)
                            for sConnValue in oConnValues:

                                # -------------------------------------------------------------------------------------
                                # Set extra tags
                                oDataTagsExtra = {'NamePlant': {sVarTag: sConnValue}}

                                # Method to get variable from different file(s) --> ASCII
                                [oDataDynamicTimeSeries_GET, oDataDynamicTimeSeries_CHECK] = getForcingTimeSeries_ASCII(
                                    sDataTime, sRunMode, sDataFlag,
                                    None, 15,
                                    mergeDict(self.oDataTags, oDataTagsExtra),
                                    self.oDataStaticPoint,
                                    self.oDataDynamicTimeSeries_INIT,
                                    deepcopy(self.oDataDynamicTimeSeries_RUN),
                                    sVarNameDyn, sConnValue,
                                    self.sPathTemp)

                                # Store availability of file(s)
                                oDataDynamicTimeSeries_CHECK_STEP.append(checkDictKeys(oDataDynamicTimeSeries_CHECK)[0])
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Reduce file checking to single value (true or false)
                                if True in oDataDynamicTimeSeries_CHECK_STEP:
                                    a1bDataCheck_STEP[iDataID] = True
                                else:
                                    a1bDataCheck_STEP[iDataID] = False
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Check saving Data
                                if convertVarType(a1bDataCheck_STEP[iDataID]) is True:

                                    # Method to save Data in forcing folder
                                    saveForcingTimeSeries_ASCII(
                                        sDataTime,
                                        join(self.oDataDynamicTimeSeries_INIT['FilePath'],
                                             self.oDataDynamicTimeSeries_INIT['FileName']),
                                        sRunMode, sDataFlag,
                                        self.oDataSettings, mergeDict(self.oDataTags, oDataTagsExtra),
                                        oDataDynamicTimeSeries_GET)

                                    # Info end (ok)
                                    oLogStream.info(' ----> DataTime ' + sDataTime +
                                                    ' DataType: ' + sDataFlag +
                                                    ' DataVariable: ' + sVarNameDyn + ' ... OK')
                                else:
                                    # Info end (skip)
                                    oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag +
                                                    ' DataVariable: ' + sVarNameDyn + ' ... '
                                                    'SKIP - ALL DATA ARE NOT AVAILABLE')
                                # -------------------------------------------------------------------------------------

                            # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------

                    else:

                        # -------------------------------------------------------------------------------------
                        # Info end (skip)
                        oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag +
                                        ' DataVariable: ' + sVarNameDyn + ' ... '
                                        'SKIP - ALL DATA ARE NOT AVAILABLE')
                        # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------

            else:

                # -------------------------------------------------------------------------------------
                # Exit for file type mismatch
                Exc.getExc(' =====> ERROR: FileType flag is not correctly set! Check your settings!', 1, 1)
                # -------------------------------------------------------------------------------------

        else:

            # -------------------------------------------------------------------------------------
            # Pass for time step not match with Data flag
            pass
            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Reduce file checking to single value (true or false)
        if True in oDataDynamicTimeSeries_CHECK_STEP:
            a1bDataCheck[iDataID] = True

            # Put summary time information
            self.oSummaryTime = putTimeSummary(
                sDataTime, self.oSummaryTime,
                convertVarType(a1bDataCheck[iDataID]), 'DataForcingTimeSeries')

        else:
            a1bDataCheck[iDataID] = False
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Pass Data checking
        self.a1bDataCheck_Obs = a1bDataCheck
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
