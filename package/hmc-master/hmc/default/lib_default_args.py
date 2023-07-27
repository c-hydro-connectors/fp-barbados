"""
Library Features:

Name:          lib_default_args
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
from time import strftime, gmtime
from tempfile import mkdtemp
from os.path import join
#######################################################################################

# -------------------------------------------------------------------------------------
# Data formats
sTimeType = 'GMT'  # 'GMT', 'local'
sTimeFormat = "%Y%m%d%H%M"  # '%Y%m%d%H%M'
sTimeUnits = 'days since 1970-01-01 00:00'
sTimeCalendar = 'gregorian'

# Logging information
sLoggerName = 'sLogger' # 'sLogger'
sLoggerFile = 'log.txt'
sLoggerHandle = 'file'  # 'file' or 'stream'
sLoggerFormatter = '%(asctime)s %(name)-12s %(levelname)-8s %(filename)s:[%(lineno)-6s - %(funcName)20s()] %(message)s'

# Definition of run external file
sFileExec = 'HMC_Model_V2_$RUN.x'

# Definition of zip extension
sZipExt = 'gz'

# Definition of path delimiter
sPathDelimiter = '$'

# Debug filename(s)
sFolderTemp = mkdtemp()
#sFolderTemp = '/home/fabio/'
sFileBuilderTemp = 'builder.workspace'
sFileRunnerTemp = 'runner.workspace'
sFileFinalizerTemp = 'finalizer.workspace'

sFileBuilder = join(sFolderTemp, sFileBuilderTemp)
sFileRunner = join(sFolderTemp, sFileRunnerTemp)
sFileFinalizer = join(sFolderTemp, sFileFinalizerTemp)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Algorithm arguments Data structure
ConfigArgs = dict(FileSetting='hmc_model_run-manager_algorithm.config',
                  Time=strftime(sTimeFormat, gmtime()))
# -------------------------------------------------------------------------------------
