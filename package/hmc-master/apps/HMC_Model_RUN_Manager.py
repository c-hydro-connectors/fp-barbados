"""
        HYDROLOGICAL MODEL CONTINUUM
        Run manager to set hydrological model and its parameters

        Parameters
        ----------
        -settingfile : string
            Name of the setting file
        -logfile : string
            Name of the logging file
        -time: string
            Time of the run in YYYYMMDDHHMM format

        Returns
        -------
        iExitStatus : int
            Function error codes (0: OK, 1: Error in "Set model", 2: Error in "Initialize model"
                                  3: Error in "Run model")
"""

# -------------------------------------------------------------------------------------
# Libraries
from os.path import join, abspath
from logging import getLogger
from logging.config import fileConfig

from time import time
from argparse import ArgumentParser

# Import methods
from hmc.log.lib_logging import setLoggingFile

# Import classes
from hmc.driver.manager.drv_manager_debug import Exc
from hmc.driver.manager.drv_manager_arguments import HMC_Arguments
from hmc.driver.manager.drv_manager_configuration import HMC_Configuration_Params, \
     HMC_Configuration_Vars, HMC_Configuration_Time
from hmc.coupler.cpl_manager import cpl_manager
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to get script argument(s)
def GetArgs():

    oParser = ArgumentParser()
    oParser.add_argument('-settingfile', action="store", dest="sSettingFile")
    oParser.add_argument('-time', action="store", dest="sTimeArg")
    oParserValue = oParser.parse_args()
    
    sScriptName = oParser.prog
    
    if oParserValue.sSettingFile:
        sSettingsFile = oParserValue.sSettingFile
    else:
        sSettingsFile = 'hmc_model_run-manager_algorithm.config'

    if oParserValue.sTimeArg:
        sTimeArg = oParserValue.sTimeArg
    else:
        sTimeArg = ''
    
    return sScriptName, sSettingsFile, sTimeArg

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Script Main
def main():

    # -------------------------------------------------------------------------------------
    # Version and algorithm information
    sProgramVersion = '2.0.7'
    sProjectName = 'HMC'
    sAlgType = 'Tools'
    sAlgName = 'RUN MANAGER '

    # Time algorithm information
    dStartTime = time()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Get script argument(s)
    [sScriptName, sFileSettingArg, sTimeArg] = GetArgs()
    # Import script argument(s)
    oData_Settings = HMC_Arguments(FileSetting=sFileSettingArg, Time=sTimeArg).importArgs()
    # Set logging file
    oLogStream = setLoggingFile(oData_Settings.FileLog)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Start Program
    oLogStream.info('[' + sProjectName + ' ' + sAlgType + ' - ' + sAlgName + ' (Version ' + sProgramVersion + ')]')
    oLogStream.info('[' + sProjectName + '] Start Program ... ')
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Initialize algorithm
    oLogStream.info('[' + sProjectName + ' ' + sAlgType + '] - Initialize ' + sAlgName + '  ... ')

    # Check section
    try:

        # -------------------------------------------------------------------------------------
        # Configure run settings, tags, mode and variable(s) information
        [oConfig_Settings, oConfig_Tags, oConfig_Mode] = HMC_Configuration_Params(
            DataSettings=oData_Settings).configParams()
        [oConfig_VarStatic, oConfig_VarDyn] = HMC_Configuration_Vars(
            DataSettings=oData_Settings).configVars()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Configure run time information
        oConfig_Time = HMC_Configuration_Time(DataSettings=oData_Settings,
                                              DataStatic=oConfig_VarStatic,
                                              TimeArg=sTimeArg).configTime()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # End section
        oLogStream.info('[' + sProjectName + ' ' + sAlgType + '] - Initialize ' + sAlgName + '  ... OK')
        # -------------------------------------------------------------------------------------

    except BaseException:

        # -------------------------------------------------------------------------------------
        # Algorithm exception(s)
        oConfig_Settings = None
        oConfig_Tags = None
        oConfig_Mode = None
        oConfig_VarStatic = None
        oConfig_VarDyn = None
        oConfig_Time = None
        Exc.getExc('[' + sProjectName + ' ' + sAlgType + '] - Initialize ' + sAlgName + '  ... FAILED', 1, 2)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Run algorithm
    oLogStream.info('[' + sProjectName + ' ' + sAlgType + '] - Execute ' + sAlgName + '  ... ')

    # Check section
    try:

        # ----------------------------------------------------------------------------
        # Model execution coupler
        oCpl_Instance = cpl_manager(DataSettings=oConfig_Settings,
                                    DataTags=oConfig_Tags,
                                    DataVarStatic=oConfig_VarStatic,
                                    DataVarDyn=oConfig_VarDyn,
                                    DataTime=oConfig_Time)
        # ----------------------------------------------------------------------------

        # ----------------------------------------------------------------------------
        # Cycle(s) over run mode dictionary (deterministic or ensemble run)
        for sRunName, oRunArgs in oConfig_Mode.items():

            # ----------------------------------------------------------------------------
            # Built model instance
            oCpl_Instance.Builder(sRunName, oRunArgs)
            # ----------------------------------------------------------------------------

            # ----------------------------------------------------------------------------
            # Execute model instance
            oCpl_Instance.Runner(sRunName, oRunArgs)
            # ----------------------------------------------------------------------------

            # ----------------------------------------------------------------------------
            # Finalize model instance
            oCpl_Instance.Finalizer(sRunName, oRunArgs)
            # ----------------------------------------------------------------------------

        # ----------------------------------------------------------------------------

        # ----------------------------------------------------------------------------
        # End section
        oLogStream.info('[' + sProjectName + ' ' + sAlgType + '] - Execute ' + sAlgName + ' ... OK')
        # -----------------------------------------------------------------------------

    except BaseException:

        # -----------------------------------------------------------------------------
        # Algorithm exception(s)
        Exc.getExc('[' + sProjectName + ' ' + sAlgType + '] - Execute ' + sAlgName + ' ... FAILED', 1, 3)
        # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    # Note about script parameter(s)
    oLogStream.info('NOTE - Algorithm parameter(s)')
    oLogStream.info('Script: ' + str(sScriptName))
    # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    # End Program
    dTimeElapsed = round(time() - dStartTime, 1)

    oLogStream.info('[' + sProjectName + ' ' + sAlgType + ' - ' + sAlgName + ' (Version ' + sProgramVersion + ')]')
    oLogStream.info('End Program - Time elapsed: ' + str(dTimeElapsed) + ' seconds')

    Exc.getExc('', 0, 0)
    # ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Call script from external library
if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------------
