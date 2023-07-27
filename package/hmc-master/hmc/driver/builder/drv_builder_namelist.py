"""
Class Features

Name:          drv_builder_namelist
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
from os.path import join

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import ConfigTags, StaticTags, DynamicTags
from hmc.default.lib_default_settings import FileSettings
from hmc.default.lib_default_datastatic import DataStatic as DataStatic_Default
from hmc.default.lib_default_datadynamic import DataDynamic as DataDynamic_Default
from hmc.default.lib_default_time import DataTime as DataTime_Default
from hmc.default.lib_default_namelist import DataNamelist as DataNamelist_Default
from hmc.default.lib_default_namelist import FileNamelist as FileNamelist_Default

from hmc.namelist.lib_namelist import updateData_NML, defineFile_NML, writeFile_NML

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class Builder Namelist
class HMC_Builder_Namelist:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataVarStatic = {}
    oDataVarDynamic = {}
    oDataTime = {}

    oDataNML = {}
    sFileNML = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method ClassInit
    def __init__(self, DataSettings=FileSettings,
                 DataTags=ConfigTags,
                 DataVarStatic=DataStatic_Default,
                 DataVarDynamic=DataDynamic_Default,
                 DataTime=DataTime_Default,
                 DataNamelist=DataNamelist_Default,
                 FileNamelist=FileNamelist_Default):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = DataSettings
        self.oDataTags = DataTags
        self.oDataVarStatic = DataVarStatic
        self.oDataVarDynamic = DataVarDynamic
        self.oDataTime = DataTime

        self.oDataNML = DataNamelist
        self.sFileNML = FileNamelist

        # Format
        self.__LineIndent = 4 * ' '
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to write namelist file
    def writeNML(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Write namelist file ... ')

        # Method to update namelist values
        self.oDataNML = updateData_NML(self.oDataSettings, self.oDataTags,
                                        self.oDataVarStatic, self.oDataVarDynamic,
                                        self.oDataTime,
                                        self.oDataNML)

        # Method to define namelist filename
        self.sFileNML = defineFile_NML(join(self.oDataSettings['ParamsInfo']['Run_Path']['PathExec'],
                                            self.oDataSettings['ParamsInfo']['Run_VarExec']['RunModelNamelist']),
                                       self.oDataTags)

        # Method to write namelist file
        writeFile_NML(self.sFileNML, self.oDataNML, self.__LineIndent)

        # Info end
        oLogStream.info(' ---> Write namelist file ... OK')

        # Return variable to global workspace
        return self.sFileNML, self.oDataNML
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
