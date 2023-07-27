"""
Library Features:

Name:          drv_data_io_h03b
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180717'
Version:       '1.0.0'
"""
#################################################################################
# Library
import logging
import progressbar

from sys import version_info

from datetime import timedelta
from datetime import datetime
from os import remove
from os.path import exists, isfile
from copy import deepcopy
from numpy import reshape, full, empty, nan, zeros, isnan, asarray

from fp.analysis.lib_analysis_interpolation_grid import interpGridData, interpGridIndex

from fp.utils.lib_utils_op_string import defineString, convertUnicode2ASCII
from fp.utils.lib_utils_op_list import mergeList
from fp.utils.lib_utils_apps_data import updateDictStructure
from fp.utils.lib_utils_apps_file import handleFileData, selectFileDriver, zipFileData
from fp.utils.lib_utils_file_workspace import savePickle, restorePickle
from fp.utils.lib_utils_apps_time import getTimeFrom, getTimeTo, getTimeSteps, checkTimeRef, roundTimeStep, findTimeDiff

from fp.default.lib_default_args import sZipExt as sZipExt_Default
from fp.default.lib_default_args import sTimeFormat as sTimeFormat_Default
from fp.default.lib_default_args import sTimeCalendar as sTimeCalendar_Default
from fp.default.lib_default_args import sTimeUnits as sTimeUnits_Default
from fp.default.lib_default_conventions import oVarConventions as oVarConventions_Default
from fp.default.lib_default_conventions import oFileConventions as oFileConventions_Default

from fp.default.lib_default_args import sLoggerName

from fp.driver.configuration.drv_configuration_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
import matplotlib.pylab as plt
#################################################################################

# -------------------------------------------------------------------------------------
# Algorithm valid keys definition(s)
oVarKey_Valid = {'time': 'Time', 'longitude': 'lon', 'latitude': 'lat'}
# Algorithm not valid keys definition(s)
oVarKey_NotValid = ['codedValues', 'distinctLatitudes', 'distinctLongitudes', 'g2grid',
                             'hundred', 'latLonValues', 'latitudes', 'longitudes',
                             'numberOfSection', 'sectionNumber', 'values']
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class data object
class DataObj(dict):
    pass
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class to compute time product
class DataProductTime:

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, **kwargs):
        self.sVarTimeStep = kwargs['timestep']
        self.sVarTimeRun = kwargs['timerun']
        self.oVarTime = kwargs['settings']['data']['dynamic']['time']
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to round time to closest time to closest defined time interval
    def __roundTimeStep(self, sTimeStep):

        oVarTime = self.oVarTime

        if 'time_reference_type' in oVarTime:

            sTimeUnits = oVarTime['time_reference_type']['units']
            iTimeRound = oVarTime['time_reference_type']['rounding']
            oTimeSteps = oVarTime['time_reference_type']['steps']

            bTimeMM = checkTimeRef(sTimeStep, oTimeMins=oTimeSteps)
            if bTimeMM is False:

                sTimeRound = roundTimeStep(sTimeStep, sDeltaUnits=sTimeUnits, iDeltaValue=iTimeRound)
                return sTimeRound
            else:
                return sTimeStep
        else:
            return sTimeStep

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute reference time (to control files mount and avoid memory fails)
    def __selectRefTime(self, sVarTimeStep, sVarTimeRun):

        oVarTimeStep = datetime.strptime(sVarTimeStep, sTimeFormat_Default)
        oVarTimeRun = datetime.strptime(sVarTimeRun, sTimeFormat_Default)

        oVarTimeDelta = timedelta(seconds=self.oVarTime['time_observed_step'] * self.oVarTime['time_observed_delta'])
        oVarTimeCheck = oVarTimeStep + oVarTimeDelta

        if oVarTimeCheck > oVarTimeRun:
            sVarTimeRef = oVarTimeRun.strftime(sTimeFormat_Default)
        elif oVarTimeCheck < oVarTimeRun:
            sVarTimeRef = oVarTimeStep.strftime(sTimeFormat_Default)
        else:
            sVarTimeRef = oVarTimeRun.strftime(sTimeFormat_Default)

        iVarTimeDiff = findTimeDiff(sVarTimeRef, sVarTimeStep)

        return sVarTimeRef, iVarTimeDiff
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute data time
    def computeDataTime(self):

        sVarTimeStep = self.sVarTimeStep
        sVarTimeRun = self.sVarTimeRun
        oVarTime = self.oVarTime

        sVarTimeRun = self.__roundTimeStep(sVarTimeRun)

        sVarTimeRef, iVarTimeDiff = self.__selectRefTime(sVarTimeStep, sVarTimeRun)

        if 'time_observed_step' in oVarTime and 'time_observed_delta' in oVarTime:
            iVarTimeObsStep = oVarTime['time_observed_step']
            iVarTimeObsDelta = oVarTime['time_observed_delta']
        else:
            iVarTimeObsStep = 0
            iVarTimeObsDelta = 0

        if 'time_forecast_step' in oVarTime and 'time_forecast_delta' in oVarTime:
            iVarTimeForStep = oVarTime['time_forecast_step']
            iVarTimeForDelta = oVarTime['time_forecast_delta']
        else:
            iVarTimeForStep = 0
            iVarTimeForDelta = 0

        iVarTimeRefStep = int(iVarTimeDiff / iVarTimeObsDelta)
        iVarTimeObsStep = iVarTimeObsStep + iVarTimeRefStep

        sVarTimeFrom = getTimeFrom(sVarTimeRef, iVarTimeObsDelta, iVarTimeObsStep)[0]
        sVarTimeTo = getTimeTo(sVarTimeRef, iVarTimeForDelta, iVarTimeForStep)[0]

        a1oVarTimeObs = getTimeSteps(sVarTimeFrom, sVarTimeRef, iVarTimeObsDelta)
        a1oVarTimeFor = getTimeSteps(sVarTimeRef, sVarTimeTo, iVarTimeForDelta)

        a1oVarTime = mergeList(a1oVarTimeObs, a1oVarTimeFor)
        a1oVarTime.sort()

        return a1oVarTime

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class to clean data product
class DataProductCleaner:

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, **kwargs):
        self.a1oFile = kwargs['file']
        self.a1bFlag = kwargs['flag']
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to clean selected file(s)
    def cleanDataProduct(self):

        if isinstance(self.a1bFlag, bool):
            self.a1bFlag = [self.a1bFlag]
        if isinstance(self.a1oFile, str):
            self.a1oFile = [self.a1oFile]

        if self.a1bFlag.__len__() < self.a1oFile.__len__():
            self.a1bFlag = full(self.a1oFile.__len__(),  self.a1bFlag[0], dtype=bool)

        for bFlag, oFile in zip(self.a1bFlag, self.a1oFile):

            if version_info < (3, 0):
                oFile = convertUnicode2ASCII(oFile)

            if isinstance(oFile, str):
                oFile = [oFile]
            for sFile in oFile:
                if exists(sFile):
                    if bFlag:
                        remove(sFile)
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class to analyze data product
class DataProductAnalyzer:

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, **kwargs):
        self.sVarTime = kwargs['time']
        self.oVarDef = kwargs['settings']['variables']['input']
        self.oVarData = kwargs['data']
        self.oVarFile = {'grid_ref': kwargs['grid_ref_file']}
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute data
    def computeDataProduct(self, oDataGeo=None):

        # -------------------------------------------------------------------------------------
        # Iterate over file variable(s)
        oVarWS = self.oVarData
        oVarSel = DataObj()
        for sVarKey, oVarDef in self.oVarDef.items():

            # -------------------------------------------------------------------------------------
            # Get input variable information
            oVarType = oVarDef['id']['var_type']
            oVarName = oVarDef['id']['var_name']
            sVarFile = oVarDef['id']['var_file']
            sVarMethod = oVarDef['id']['var_method_compute']

            oVarAttrs = oVarDef['attributes']

            # Info start about computing variable
            oLogStream.info(' ---> Compute variable: ' + sVarKey + ' ... ')
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Create workspace for each variable and ancillary data
            oVarSel[sVarKey] = {}
            for sVarName in oVarName:
                oVarSel[sVarKey][sVarName] = {}
                if oVarWS[sVarName]:
                    if 'values' in oVarWS[sVarName] \
                            and 'attributes' in oVarWS[sVarName] \
                            and 'parameters' in oVarWS[sVarName] \
                            and 'times' in oVarWS[sVarName]:
                        oVarSel[sVarKey][sVarName]['values'] = {}
                        oVarSel[sVarKey][sVarName]['values'] = oVarWS[sVarName]['values']
                        oVarSel[sVarKey][sVarName]['parameters'] = {}
                        oVarSel[sVarKey][sVarName]['parameters'] = oVarWS[sVarName]['parameters']
                        oVarSel[sVarKey][sVarName]['attributes'] = {}
                        oVarSel[sVarKey][sVarName]['attributes'] = oVarWS[sVarName]['attributes']
                        oVarSel[sVarKey][sVarName]['times'] = {}
                        oVarSel[sVarKey][sVarName]['times'] = oVarWS[sVarName]['times']

                        if 'longitude' not in oVarSel:
                            oVarSel[sVarKey]['longitude'] = oVarWS[sVarName]['longitude']
                        if 'latitude' not in oVarSel:
                            oVarSel[sVarKey]['latitude'] = oVarWS[sVarName]['latitude']

                    else:
                        oVarSel[sVarKey][sVarName] = None
                else:
                    oVarSel[sVarKey][sVarName] = None

            # Check data available for all selected ancillary variable(s)
            for sVarName in oVarSel[sVarKey]:
                if oVarSel[sVarKey][sVarName] is None:
                    oVarSel[sVarKey] = None
                    break
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Check data field(s) availability to compute results
            if oVarSel[sVarKey]:

                # -------------------------------------------------------------------------------------
                # Adjust dictionary and delete unnecessary field(s)
                oVarSel[sVarKey]['values'] = {}
                oVarSel[sVarKey]['values'] = oVarSel[sVarKey][sVarName]['values']
                oVarSel[sVarKey]['times'] = {}
                oVarSel[sVarKey]['times'] = oVarSel[sVarKey][sVarName]['times']
                oVarSel[sVarKey]['attributes'] = {}
                oVarSel[sVarKey]['attributes'] = oVarSel[sVarKey][sVarName]['attributes']

                oVarSel[sVarKey].pop(sVarName, None)
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Check fields definition in variable workspace
                if ('values' in oVarSel[sVarKey]) and ('attributes' in oVarSel[sVarKey]) and (
                        'times' in oVarSel[sVarKey]):

                    # -------------------------------------------------------------------------------------
                    # Get data and attributes
                    a2dVarValue = deepcopy(oVarSel[sVarKey]['values']).astype(float)
                    a1dVarGeoX = deepcopy(oVarSel[sVarKey]['longitude']).astype(float)
                    a1dVarGeoY = deepcopy(oVarSel[sVarKey]['latitude']).astype(float)
                    oVarAttrs = deepcopy(oVarSel[sVarKey]['attributes'])
                    oVarTime = deepcopy(oVarSel[sVarKey]['times'])

                    # Get missing value
                    if 'Missing_value' in oVarAttrs:
                        dVarMissValue = oVarAttrs['Missing_value']
                    else:
                        dVarMissValue = -9999.0
                    # Get scale factor
                    if 'ScaleFactor' in oVarAttrs:
                        dScaleFactor = oVarAttrs['ScaleFactor']
                    else:
                        dScaleFactor = 1
                    # Get fill value
                    if '_FillValue' in oVarAttrs:
                        dVarFillValue = oVarAttrs['_FillValue']
                    else:
                        dVarFillValue = -9999.0
                    # Get units
                    if 'units' in oVarAttrs:
                        sVarUnits = oVarAttrs['units']
                    else:
                        sVarUnits = None
                    # Get valid range
                    if 'Valid_range' in oVarAttrs:
                        oVarValidRange = asarray(oVarAttrs['Valid_range'])
                    else:
                        oVarValidRange = None
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check data attributes to control units conversion
                    if sVarUnits:
                        assert sVarUnits == 'kg.m-2.s-1'
                        assert dScaleFactor == 3600
                    else:
                        Exc.getExc(' ---> Variable units are not defined! Mismatching in outcome data!', 2, 1)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Initialize variable to store results
                    a3dVarValue_FILTER = zeros(
                        [oDataGeo.a2dGeoX.shape[0], oDataGeo.a2dGeoY.shape[1], oVarTime.__len__()])
                    a3dVarValue_FILTER[:, :, :] = nan

                    # Info start interpolating variable
                    oLogStream.info(' ----> Interpolate variable over domain ... ')

                    # Iterate over time step(s)
                    iVarDim = None
                    oPBar = progressbar.ProgressBar()
                    for iTimeStep, sTimeStep in enumerate(oPBar(oVarTime)):

                        # -------------------------------------------------------------------------------------
                        # Get data
                        a1dVarValue = a2dVarValue[:, iTimeStep]

                        # Check data dimension to avoid grid mismatching
                        if iVarDim is None:
                            iVarDim = a1dVarValue.shape[0]
                            if exists(self.oVarFile['grid_ref']):
                                remove(self.oVarFile['grid_ref'])
                        else:
                            try:
                                assert iVarDim == a1dVarValue.shape[0]
                            except BaseException:
                                iVarDim = a1dVarValue.shape[0]
                                remove(self.oVarFile['grid_ref'])
                                Exc.getExc(' ---> Changing in data dimension! Update grid index reference!', 2, 1)
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Create grid reference(s)
                        if not exists(self.oVarFile['grid_ref']):
                            a1iVarIndex_INTERP = interpGridIndex(a1dVarValue,
                                                                 a1dVarGeoX, a1dVarGeoY,
                                                                 oDataGeo.a2dGeoX, oDataGeo.a2dGeoY)

                            savePickle(self.oVarFile['grid_ref'], a1iVarIndex_INTERP)
                        else:
                            a1iVarIndex_INTERP = restorePickle(self.oVarFile['grid_ref'])
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Set nan for missing and outbounds values
                        a1dVarValue[a1dVarValue == dVarMissValue] = nan
                        if oVarValidRange[0] is not None:
                            a1dVarValue[a1dVarValue < oVarValidRange[0]] = nan
                        if oVarValidRange[1] is not None:
                            a1dVarValue[a1dVarValue > oVarValidRange[0]] = nan
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Interpolate variable over grid reference
                        a2dVarValue_INTERP = interpGridData(a1dVarValue,
                                                            a1dVarGeoX, a1dVarGeoY,
                                                            oDataGeo.a2dGeoX, oDataGeo.a2dGeoY,
                                                            a1iVarIndex_OUT=a1iVarIndex_INTERP)

                        # Apply scale factor (from kg m^-2 s^-1 to mm/h (kg/m^2 == mm, s*3600 == h)
                        a2dVarValue_INTERP = a2dVarValue_INTERP * dScaleFactor

                        # Set fill value for undefined data (nan)
                        a1dVarValue_INTERP = deepcopy(a2dVarValue_INTERP.ravel())
                        a1dVarValue_INTERP[oDataGeo.a1iGeoIndexNaN] = dVarFillValue
                        a1dVarValue_INTERP[isnan(a1dVarValue_INTERP)] = dVarFillValue

                        # Reshape data with selected domain
                        a2dVarValue_DEF = reshape(a1dVarValue_INTERP,
                                                  [oDataGeo.a2dGeoX.shape[0], oDataGeo.a2dGeoY.shape[1]])
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Debug
                        # plt.figure()
                        # plt.imshow(a2dVarValue_INTERP); plt.colorbar(); plt.clim(0, 1)
                        # plt.figure()
                        # plt.imshow(a2dVarValue_DEF); plt.colorbar(); plt.clim(0, 1)
                        # plt.show()
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Store results
                        a3dVarValue_FILTER[:, :, iTimeStep] = a2dVarValue_DEF
                        # -------------------------------------------------------------------------------------

                    # Info end interpolating variable
                    oLogStream.info(' ----> Interpolate variable over domain ... OK')
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Add attributes to workspace
                    if not hasattr(oVarSel, 'iRows'):
                        oVarSel.iRows = a3dVarValue_FILTER.shape[0]
                    if not hasattr(oVarSel, 'iCols'):
                        oVarSel.iCols = a3dVarValue_FILTER.shape[1]
                    if not hasattr(oVarSel, 'iTime'):
                        oVarSel.iTime = a3dVarValue_FILTER.shape[2]
                    if not hasattr(oVarSel, 'oDataTime'):
                        oVarSel.oDataTime = oVarTime

                    # Save data
                    oVarSel[sVarKey]['results'] = a3dVarValue_FILTER
                    # Info end computing variable
                    oLogStream.info(' ---> Compute variable: ' + sVarKey + ' ... OK')
                    # -------------------------------------------------------------------------------------

                else:

                    # -------------------------------------------------------------------------------------
                    # Exit variable key not in workspace
                    Exc.getExc(' ---> Compute variable: ' + sVarKey +
                               ' ... FAILED! Values and/or attributes field(s) is/are not defined!', 2, 1)
                    oVarSel[sVarKey] = None
                    # -------------------------------------------------------------------------------------

            else:

                # -------------------------------------------------------------------------------------
                # Exit variable key not in workspace
                Exc.getExc(' ---> Compute variable: ' + sVarKey +
                           ' ... FAILED! One or more data field(s) is/are not defined!', 2, 1)
                oVarSel[sVarKey] = None
                # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Return workspace
        return oVarSel
        # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class to finalize data product
class DataProductFinalizer:

    # -------------------------------------------------------------------------------------
    # Class declaration(s)
    oVarCM = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, **kwargs):

        self.sVarTime = kwargs['time']
        self.oVarDef = kwargs['settings']['variables']['outcome']
        self.oVarData = kwargs['data']
        self.oVarFile = {'rain_product': kwargs['rain_product_file']}
        self.oVarColorMap = kwargs['rain_colormap_file']
        self.oAlgConventions = kwargs['settings']['algorithm']

        self.bVarSubSet = True

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to subset data
    @staticmethod
    def subsetData(oData_Dynamic, iData_Index=None):

        # Define time index
        if iData_Index is None:
            iData_Index = 0
        else:
            iData_Index = iData_Index + 1

        iData_Dynamic_Index = oData_Dynamic.iTime - 1

        # Check time step availability in data
        if iData_Dynamic_Index >= iData_Index:

            # Get data
            oData_Dynamic_Step = deepcopy(oData_Dynamic)
            # Subset data
            sData_Time = oData_Dynamic.oDataTime[iData_Index]
            oData_Results = oData_Dynamic['rain_istantaneous_data']['results']
            oData_Time = oData_Dynamic['rain_istantaneous_data']['times']

            # Remove unnecessary fields
            oData_Dynamic_Step['rain_istantaneous_data'].pop('values', None)
            oData_Dynamic_Step['rain_istantaneous_data'].pop('results', None)
            oData_Dynamic_Step['rain_istantaneous_data'].pop('times', None)

            # Redefine data
            oData_Dynamic_Step.iTime = 1
            oData_Dynamic_Step.oDataTime = [sData_Time]
            oData_Dynamic_Step['rain_istantaneous_data']['results'] = oData_Results[:, :, iData_Index]
            oData_Dynamic_Step['rain_istantaneous_data']['times'] = [oData_Time[iData_Index]]
            # Information
            oLogStream.info(' ---> SubsetData Time: ' + sData_Time + ' Index: ' + str(iData_Index))

        else:

            sData_Time = None
            iData_Index = None
            oData_Dynamic_Step = None

        return sData_Time, iData_Index, oData_Dynamic_Step

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get variable colormap
    @staticmethod
    def __getColorMap(sFileCM):

        # Get file driver (according with filename extensions
        if isfile(sFileCM):
            oFileDriver = selectFileDriver(sFileCM, sFileMode='r')[0]
            oFileCM = oFileDriver.oFileLibrary.openFile(sFileCM, 'r')
            oFileLines = oFileDriver.oFileLibrary.getLines(oFileCM)
        else:
            oFileLines = ''

        return oFileLines

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to save data
    def saveDataProduct(self, oDataGeo=None, oDataDynamic=None):

        # -------------------------------------------------------------------------------------
        # Get information if single or recursive method
        if self.bVarSubSet:
            sVarTime = oDataDynamic[0]
            iVarIndex = oDataDynamic[1]
            oVarData = oDataDynamic[2]

            if oVarData is None:
                return None
        else:
            sVarTime = self.sVarTime
            iVarIndex = 0
            oVarData = oDataDynamic
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Define time tags
        oTimeTags = {'$yyyy': sVarTime[0:4],
                     '$mm': sVarTime[4:6], '$dd': sVarTime[6:8], '$HH': sVarTime[8:10],
                     '$MM': sVarTime[10:12]}

        # Define general and geo-system information
        oFileGeneralInfo = updateDictStructure(oFileConventions_Default, self.oAlgConventions, 'general')
        oFileGeoSystemInfo = updateDictStructure(oFileConventions_Default, self.oAlgConventions, 'geosystem')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Iterate over outcome variable(s)
        for sVarKey, oVarDef in self.oVarDef.items():

            # -------------------------------------------------------------------------------------
            # Info start saving variable
            oLogStream.info(' ---> Save workspace: ' + sVarKey + ' ... ')

            # Get outcome variable information
            oVarType = oVarDef['id']['var_type']
            sVarName = oVarDef['id']['var_name']
            sVarFile = oVarDef['id']['var_file']
            sVarMethod = oVarDef['id']['var_method_save']
            sVarColormap = oVarDef['id']['var_colormap']

            # Get outcome variable colormap
            oVarCM = {}
            if sVarKey in oVarData:
                if sVarColormap in self.oVarColorMap:
                    oVarCM['colormap'] = self.__getColorMap(self.oVarColorMap[sVarColormap])
                else:
                    oVarCM['colormap'] = None
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Check variable workspace
            if oVarData[sVarKey]:

                # -------------------------------------------------------------------------------------
                # Check file tag in file definition(s)
                if sVarFile in self.oVarFile:

                    # -------------------------------------------------------------------------------------
                    # Get filename from file definition(s) using file tag in outcome variable(s)
                    sVarFileName = defineString(deepcopy(self.oVarFile[sVarFile]), oTimeTags)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check file saved on disk
                    if not exists(sVarFileName):

                        # -------------------------------------------------------------------------------------
                        # Info create file
                        oLogStream.info(' ----> Create file ' + sVarFileName + ' ... ')

                        # Get file driver (according with filename extensions
                        [oFileDriver, sFileUnzip, _] = selectFileDriver(sVarFileName, sZipExt_Default)

                        # Open file outcome
                        oFileData = oFileDriver.oFileLibrary.openFile(sFileUnzip, 'w')

                        # Write file attributes
                        oFileDriver.oFileLibrary.writeFileAttrs(oFileData, oFileGeneralInfo)
                        # Write geo system information
                        oFileDriver.oFileLibrary.writeGeoSystem(oFileData, oFileGeoSystemInfo)
                        # Write X, Y, time, nsim, ntime and nens
                        oFileDriver.oFileLibrary.writeDims(oFileData, 'X', oVarData.iCols)
                        oFileDriver.oFileLibrary.writeDims(oFileData, 'Y', oVarData.iRows)
                        oFileDriver.oFileLibrary.writeDims(oFileData, 'time', oVarData.iTime)
                        oFileDriver.oFileLibrary.writeDims(oFileData, 'nsim', 1)
                        oFileDriver.oFileLibrary.writeDims(oFileData, 'ntime', 2)
                        oFileDriver.oFileLibrary.writeDims(oFileData, 'nens', 1)

                        # Get file dimension(s)
                        oFileDims = oFileDriver.oFileLibrary.getDims(oFileData)

                        # Write time information
                        oFileDriver.oFileLibrary.writeTime(oFileData, 'time', oVarData.oDataTime, 'float64', 'time',
                                                           sTimeFormat_Default, sTimeCalendar_Default,
                                                           sTimeUnits_Default)

                        # Write longitude information
                        sVarNameX = 'longitude'
                        a2dVarDataX = oDataGeo.a2dGeoX
                        oVarAttrsX = oVarConventions_Default[sVarNameX]
                        sVarFormatX = oVarConventions_Default[sVarNameX]['Format']
                        oFileDriver.oFileLibrary.write2DVar(oFileData, sVarNameX,
                                                            a2dVarDataX, oVarAttrsX, sVarFormatX,
                                                            sVarDimY=oFileDims['Y']['name'],
                                                            sVarDimX=oFileDims['X']['name'])
                        # Write latitude information
                        sVarNameY = 'latitude'
                        a2dVarDataY = oDataGeo.a2dGeoY
                        oVarAttrsY = oVarConventions_Default[sVarNameY]
                        sVarFormatY = oVarConventions_Default[sVarNameY]['Format']
                        oFileDriver.oFileLibrary.write2DVar(oFileData, sVarNameY,
                                                            a2dVarDataY, oVarAttrsY, sVarFormatY,
                                                            sVarDimY=oFileDims['Y']['name'],
                                                            sVarDimX=oFileDims['X']['name'])

                        # Info create file
                        oLogStream.info(' ----> Create file ' + sVarFileName + ' ... OK')
                        # -------------------------------------------------------------------------------------
                    else:
                        # -------------------------------------------------------------------------------------
                        # Info get file
                        oLogStream.info(' ----> Get file ' + sVarFileName + ' previously created ... ')
                        # Get file driver (according with filename extensions
                        [oFileDriver, sFileUnzip, _] = selectFileDriver(sVarFileName, sZipExt_Default)

                        # Open file outcome
                        oFileData = oFileDriver.oFileLibrary.openFile(sFileUnzip, 'a')
                        # Get file dimension(s)
                        oFileDims = oFileDriver.oFileLibrary.getDims(oFileData)

                        # Info get file
                        oLogStream.info(' ----> Get file ' + sVarFileName + ' previously created ... OK')
                        # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Info start saving variable
                    oLogStream.info(' -----> Save variable ' + sVarName + ' ... ')
                    # Check variable in file handle
                    if oFileDriver.oFileLibrary.checkVarName(oFileData, sVarName) is False:

                        # -------------------------------------------------------------------------------------
                        # Get file dimensions
                        sVarDimX = oFileDims['X']['name']
                        sVarDimY = oFileDims['Y']['name']
                        sVarDimT = oFileDims['time']['name']

                        # Get var structure
                        oVarStruct = oVarData[sVarKey]
                        # Define var attribute(s)
                        oVarAttrs = deepcopy(oVarConventions_Default[oVarType[0]])
                        oVarAttrs = updateDictStructure(oVarAttrs, oVarStruct['attributes'])
                        oVarAttrs = updateDictStructure(oVarAttrs, oVarDef['attributes'])
                        oVarAttrs = updateDictStructure(oVarAttrs, oVarCM)

                        # Get variable data
                        oVarResults = oVarStruct['results']
                        # Get variable format
                        if 'Format' in oVarStruct['attributes']:
                            sVarFormat = oVarStruct['attributes']['Format']
                        else:
                            sVarFormat = 'f4'

                        # Check and get library write method
                        if hasattr(oFileDriver.oFileLibrary, sVarMethod):
                            # Get write method
                            oVarMethod = getattr(oFileDriver.oFileLibrary, sVarMethod)

                            # Store variable (2d and 3d dimensions)
                            if oVarType[0] == 'var2d':
                                oVarMethod(oFileData, sVarName, oVarResults, oVarAttrs, sVarFormat,
                                           sVarDimY=sVarDimY, sVarDimX=sVarDimX)
                            elif oVarType[0] == 'var3d':
                                oVarMethod(oFileData, sVarName, oVarResults, oVarAttrs, sVarFormat,
                                           sVarDimT=sVarDimT, sVarDimY=sVarDimY, sVarDimX=sVarDimX)

                            # Info end saving variable
                            oLogStream.info(' -----> Save variable ' + sVarName + ' ... OK ')

                        else:
                            # Exit without saving variable
                            Exc.getExc(' ---> Save variable: ' +
                                       sVarKey + ' ... FAILED! Selected method is not available on io library', 2, 1)
                        # -------------------------------------------------------------------------------------
                    else:
                        # -------------------------------------------------------------------------------------
                        # Info skip saving variable
                        oLogStream.info(' -----> Save variable ' + sVarName +
                                        ' ... SKIPPED! Variable is already saved in selected file ')
                        # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Info start closing and zipping file
                    oLogStream.info(' ----> Close and zip file ' + sVarFileName + ' ... ')
                    # Close file
                    oFileDriver.oFileLibrary.closeFile(oFileData)
                    # Zip file
                    zipFileData(sFileUnzip, sZipExt_Default)
                    # Info end closing and zipping file
                    oLogStream.info(' ----> Close and zip file ' + sVarFileName + ' ... OK')

                    # Info end saving variable
                    oLogStream.info(' ---> Save workspace: ' + sVarKey + ' ... OK')
                    # -------------------------------------------------------------------------------------

                else:
                    # -------------------------------------------------------------------------------------
                    # Exit without saving variable
                    Exc.getExc(' ---> Save workspace: ' + sVarKey + ' ... FAILED! Variable file is not declared', 2, 1)
                    # -------------------------------------------------------------------------------------
            else:
                # -------------------------------------------------------------------------------------
                # Exit without saving variable
                Exc.getExc(' ---> Save workspace: ' + sVarKey + ' ... FAILED! Variable data are null! ', 2, 1)
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Active recursive method
        if self.bVarSubSet:
            self.saveDataProduct(oDataGeo, self.subsetData(oData_Dynamic=self.oVarData, iData_Index=iVarIndex))
        else:
            return None
        # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class to build data product
class DataProductBuilder:

    # -------------------------------------------------------------------------------------
    # Class declaration(s)
    oVarData = DataObj()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, **kwargs):
        self.oVarTime = kwargs['time']
        self.oVarDef = kwargs['settings']['variables']['input']
        self.oVarFile = {'rain_data': kwargs['rain_data_file']}

        self.__defineVar()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define data variable
    def __defineVar(self):

        # -------------------------------------------------------------------------------------
        # Define variable(s) workspace by conventions and defined input field(s)
        for sVarKey, oVarValue in self.oVarDef.items():

            self.oVarData[sVarKey] = {}
            sVarID = oVarValue['id']['var_type'][0]

            if 'attributes' in oVarValue:
                oVarAttrs = oVarValue['attributes']
                for sAttrKey, oAttrValue in oVarAttrs.items():
                    if isinstance(oAttrValue, str):
                        if sAttrKey in oVarConventions_Default[sVarID].keys():
                            self.oVarData[sVarKey][sAttrKey] = {}
                            self.oVarData[sVarKey][sAttrKey] = deepcopy(oVarConventions_Default[sVarID][sAttrKey])
                    elif isinstance(oAttrValue, list):
                        if sAttrKey in oVarConventions_Default[sVarID].keys():
                            self.oVarData[sVarKey][sAttrKey] = {}
                            self.oVarData[sVarKey][sAttrKey] = deepcopy(oVarConventions_Default[sVarID][sAttrKey])

        # Update variable workspace
        for sVarKey, oVarValue in self.oVarDef.items():

            sVarID = oVarValue['id']['var_type'][0]

            for sAttrKey, oAttrValue in oVarConventions_Default[sVarID].items():
                self.oVarData[sVarKey][sAttrKey] = {}
                self.oVarData[sVarKey][sAttrKey] = oAttrValue

            if 'attributes' in oVarValue:
                oVarAttrs = oVarValue['attributes']
                for sAttrKey, oAttrValue in oVarAttrs.items():
                    self.oVarData[sVarKey][sAttrKey] = {}
                    self.oVarData[sVarKey][sAttrKey] = oAttrValue
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get data
    def getDataProduct(self, a1dGeoBox):

        # -------------------------------------------------------------------------------------
        # Iterate over file variable(s)
        oVarWS = {}
        for sVarKey, oVarDef in self.oVarDef.items():

            # -------------------------------------------------------------------------------------
            # Get input variable information
            oVarType = oVarDef['id']['var_type']
            oVarName = oVarDef['id']['var_name']
            sVarFile = oVarDef['id']['var_file']
            sVarMethodGet = oVarDef['id']['var_method_get']
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Check file tag in file definition(s)
            oVarGet = {}
            if sVarFile in self.oVarFile:

                # -------------------------------------------------------------------------------------
                # Iterate over time(s)
                for iVarTime, sVarTime in enumerate(self.oVarTime):

                    # -------------------------------------------------------------------------------------
                    # Define time tags
                    oTimeTags = {'$yyyy': sVarTime[0:4],
                                 '$mm': sVarTime[4:6], '$dd': sVarTime[6:8], '$HH': sVarTime[8:10],
                                 '$MM': sVarTime[10:12]}
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Get filename from file definition(s) using file tag in outcome variable(s)
                    sVarFileName = defineString(deepcopy(self.oVarFile[sVarFile]), oTimeTags)
                    # Info start about selected file
                    oLogStream.info(' ---> Get file: ' + sVarFileName + ' (Time: ' + sVarTime + ') ... ')
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check file saved on disk
                    if exists(sVarFileName):

                        # -------------------------------------------------------------------------------------
                        # Get data
                        [oFileHandle, oFileDriver, bFileOpen] = handleFileData(sVarFileName)
                        oFileMsg = oFileHandle[1]
                        oVarAttribute = self.oVarData[sVarKey]
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Check file opening
                        if bFileOpen is True:

                            # -------------------------------------------------------------------------------------
                            # Iterate over data variable(s)
                            for sVarName in oVarName:

                                # -------------------------------------------------------------------------------------
                                # Info start about getting variable
                                oLogStream.info(' ----> Algorithm variable: ' +
                                                sVarKey + ' - Product variable: ' + sVarName + ' ...')

                                # Init variable workspace
                                if sVarName not in oVarGet:
                                    oVarGet[sVarName] = {}
                                    oVarGet[sVarName]['values'] = None
                                    oVarGet[sVarName]['longitude'] = None
                                    oVarGet[sVarName]['latitude'] = None
                                    oVarGet[sVarName]['parameters'] = None
                                    oVarGet[sVarName]['attributes'] = None
                                    oVarGet[sVarName]['times'] = None
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Get variable name, data and attributes
                                sVarName_Msg = oFileMsg.name
                                sVarName_Msg = sVarName_Msg.replace(' ', '_')

                                assert sVarName == sVarName_Msg

                                a1dVarData, a1dVarGeoY, a1dVarGeoX = oFileDriver.oFileLibrary.getVar2D_BOX(
                                    oFileMsg, oGeoBox=a1dGeoBox)

                                oFileParameter = oFileDriver.oFileLibrary.getFileAttr(oFileMsg,
                                                                                      oVarKeyNA=oVarKey_NotValid)
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Save variable data
                                if oVarGet[sVarName]['values'] is None:
                                    a2dVarData_INIT = empty([a1dVarData.shape[0], self.oVarTime.__len__()])
                                    a2dVarData_INIT[:, :] = nan
                                    oVarGet[sVarName]['values'] = deepcopy(a2dVarData_INIT)

                                a2dVarData_DEF = oVarGet[sVarName]['values']
                                a1dVarData = a1dVarData.data
                                a2dVarData_DEF[:, iVarTime] = a1dVarData
                                oVarGet[sVarName]['values'] = a2dVarData_DEF
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Save variable time step(s)
                                if oVarGet[sVarName]['times'] is None:
                                    oVarGet[sVarName]['times'] = []
                                oVarGet[sVarName]['times'].append(sVarTime)
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Save variable longitudes and latitudes
                                if (oVarGet[sVarName]['longitude'] is None) \
                                        and (oVarGet[sVarName]['latitude'] is None):
                                    oVarGet[sVarName]['longitude'] = a1dVarGeoX
                                    oVarGet[sVarName]['latitude'] = a1dVarGeoY
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Update variable parameter(s)
                                if oVarGet[sVarName]['parameters'] is None:
                                    oVarGet[sVarName]['parameters'] = oFileParameter

                                # Update variable attribute(s)
                                if oVarGet[sVarName]['attributes'] is None:
                                    oVarGet[sVarName]['attributes'] = oVarAttribute
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Info end about getting data variable
                                oLogStream.info(' ----> Algorithm variable: ' +
                                                sVarKey + ' - Product variable: ' + sVarName + ' ... OK')
                                # Info end about file
                                oLogStream.info(' ---> Get file: ' + sVarFileName + ' (Time: ' + sVarTime + ') ... OK')
                                # -------------------------------------------------------------------------------------
                        else:
                            # -------------------------------------------------------------------------------------
                            # Exit variable key not in workspace
                            Exc.getExc(' ---> Get file: ' + sVarFileName + ' (Time: ' +
                                       sVarTime + ') ... FAILED! File not correctly open!', 2, 1)
                            # -------------------------------------------------------------------------------------
                    else:
                        # -------------------------------------------------------------------------------------
                        # Exit variable key not in workspace
                        Exc.getExc(' ---> Get file: ' + sVarFileName + ' (Time: ' +
                                   sVarTime + ') ... FAILED! File not found!', 2, 1)
                        # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Save variable workspace
                oVarWS.update(oVarGet)
                # -------------------------------------------------------------------------------------
            else:
                # -------------------------------------------------------------------------------------
                # Exit file not in workspace
                Exc.getExc(' ---> Reference file is wrongly defined! Check settings file!', 2, 1)
                # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Return workspace
        return oVarWS
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
