"""
Class Features

Name:          drv_builder_info
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
from copy import deepcopy

from hmc.default.lib_default_args import sLoggerName, sPathDelimiter
from hmc.default.lib_default_tags import ConfigTags, StaticTags, DynamicTags
from hmc.default.lib_default_settings import FileSettings
from hmc.default.lib_default_datastatic import DataStatic as DataStatic_Default
from hmc.default.lib_default_datadynamic import DataDynamic as DataDynamic_Default
from hmc.default.lib_default_time import DataTime as DataTime_Default

from hmc.settings.lib_settings import updateRunSettings

from hmc.utils.lib_utils_apps_tags import updateRunTags
from hmc.utils.lib_utils_op_string import defineString
from hmc.utils.lib_utils_op_list import reduceListUnique
from hmc.utils.lib_utils_op_dict import updateDictValue, getDictValues, getDictValue
from hmc.utils.lib_utils_op_system import createFolder

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class Builder Info
class HMC_Builder_Info:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataVarStatic = {}
    oDataVarDynamic = {}

    oDataTime = {}

    oDataSettings_VAR = {}
    oDataTags_VAR = {}
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

        self.sTimeNow = DataTime['DataTime']['TimeNow']
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to write namelist file
    def updateInfo(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Update info Data ... ')

        # Update run tag(s)
        self.__updateRunTag(sRunMode, oRunArgs)
        # Update run setting(s)
        self.__updateRunSettings()

        # Update static variable(s)
        self.__updateVarStatic()
        # Update dynamic variable(s)
        self.__updateVarDynamic()

        # Set run generic path(s)
        self.__setRunPath()

        # Info end
        oLogStream.info(' ---> Update info Data ... OK')

        # Return variable to global workspace
        return self.oDataSettings, self.oDataTags, self.oDataVarStatic, self.oDataVarDynamic
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to update setting(s)
    def __updateRunSettings(self):
        self.oDataSettings = updateRunSettings(Tags=self.oDataTags, Settings=deepcopy(self.oDataSettings))
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to update tags
    def __updateRunTag(self, sRunMode, oRunArgs):

        # Get ensemble mode
        oEnsMode = getDictValue(self.oDataSettings, ['ParamsInfo', 'Run_Params', 'RunMode', 'EnsMode'])

        # Update run tag
        self.oDataTags = updateRunTags({'RunMode': sRunMode}, deepcopy(self.oDataTags))

        # Update run tag for ensemble mode (if True)
        if oEnsMode is True:
            self.oDataTags = updateRunTags({oRunArgs[0]: oRunArgs[1]}, deepcopy(self.oDataTags))
        else:
            pass

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to update static variable(s)
    def __updateVarStatic(self):
        for oTagKey, oTagValue in iter(self.oDataTags.items()):
            sTag = list(oTagValue.keys())[0]
            oValue = list(oTagValue.values())[0]
            updateDictValue(self.oDataVarStatic, sTag, oValue)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to update dynamic variable(s)
    def __updateVarDynamic(self):
        for oTagKey, oTagValue in iter(self.oDataTags.items()):
            sTag = list(oTagValue.keys())[0]
            oValue = list(oTagValue.values())[0]
            updateDictValue(self.oDataVarDynamic, sTag, oValue)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set run path(s)
    def __setRunPath(self):

        # -------------------------------------------------------------------------------------
        # Get path(s) from settings, static and dynamic variable(s)
        oPathSettings = self.oDataSettings['ParamsInfo']['Run_Path']
        oPathStatic = getDictValues(self.oDataVarStatic, 'FilePath')
        oPathDynamic = getDictValues(self.oDataVarDynamic, 'FilePath')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Cycle(s) over settings path(s) to create run folder(s)
        for sPathKey, sPathValue in iter(oPathSettings.items()):
            # Define path tags
            oPathTags = updateRunTags({'Year': self.sTimeNow[0:4],
                                        'Month': self.sTimeNow[4:6], 'Day': self.sTimeNow[6:8],
                                        'Hour': self.sTimeNow[8:10], 'Minute': self.sTimeNow[10:12]},
                                       deepcopy(DynamicTags))
            # Define path name
            sPathRun = defineString(sPathValue, oPathTags)
            # Create folder
            createFolder(sPathRun, sPathDelimiter)
            # Update path in settings
            self.oDataSettings['ParamsInfo']['Run_Path'][sPathKey] = sPathRun
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Reduce list to unique value(s) for Data path
        oPathData = sorted(reduceListUnique(oPathStatic + oPathDynamic))
        # Cycle(s) over path to create Data folder(s)
        for sPathData in oPathData:
            createFolder(sPathData, sPathDelimiter)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
