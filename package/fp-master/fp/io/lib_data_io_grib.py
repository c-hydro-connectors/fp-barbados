"""
Library Features:

Name:          lib_data_io_grib
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170512'
Version:       '2.0.1'
"""
#################################################################################
# Library
import logging
import pygrib
import numpy as np

from fp.default.lib_default_args import sLoggerName
from fp.driver.configuration.drv_configuration_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)
#################################################################################

# --------------------------------------------------------------------------------
# Method to open grib file
def openFile(sFileName, sFileMode='r'):

    # Open file
    try:

        if sFileMode == 'r':
            oFile = pygrib.open(sFileName)
            return oFile
        else:
            Exc.getExc(' -----> WARNING: open file in write/append mode not available (lib_data_io_grib)', 2, 1)
            return None

    except IOError as oError:
        Exc.getExc(' -----> ERROR: in open file (lib_data_io_grib)' + ' [' + str(oError) + ']', 1, 1)

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to close grib file
def closeFile(oFile):
    pass
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to check messages in file
def checkFileMessage(oFile=None, iAttMessage=0):
    if oFile:
        iFileMessages = oFile.messages

        if iAttMessage == iFileMessages:
            bFileCheck = True
        else:
            bFileCheck = False
    else:
        bFileCheck = False
    return bFileCheck
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to get file messages
def getFileMessage(oFile):

    try:
        iFM = oFile.messages
        if iFM == 0:
            a1iFM = None
            Exc.getExc(' -----> WARNING: no message in GRIB file! Check your input file!', 2, 1)
        else:
            a1iFM = np.linspace(1, iFM, iFM, endpoint=True)

    except BaseException:

        a1iFM = None
        Exc.getExc(' -----> WARNING: no message in GRIB file! Check your input file!', 2, 1)

    return a1iFM

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to get 2d variable data using a box
def getVar2D_BOX(oFile, iIndex=None,
                 oGeoBox=None):

    if oGeoBox is None:
        oGeoBox = [-90, 90, -180, 180]

    if iIndex is None:
        oVarHandle = oFile
    else:
        oVarHandle = oFile[iIndex]
    a2dVarData, a2dVarLat, a2dVarLon = oVarHandle.data(lat1=oGeoBox[3], lat2=oGeoBox[1],
                                                       lon1=oGeoBox[0], lon2=oGeoBox[2])
    return a2dVarData, a2dVarLat, a2dVarLon
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to get 2d variable all domain
def getVar2D_ALL(oFile, iIndex=None):

    # Check method
    try:

        if iIndex:
            # Read variable using Data index
            oVar = oFile[iIndex]
        else:
            oVar = oFile

        a2dVarData_Masked = oVar.values
        a2dVarData = a2dVarData_Masked.data

        return a2dVarData

    except BaseException:

        # Exit status with error
        Exc.getExc(' -----> WARNING: in getting 2d variable function (lib_data_io_grib)', 2, 1)

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to read time variable
def getVarTime(oFile):

    # Get file message(s)
    iFM = oFile.messages
    a1iFM = np.linspace(1, iFM, iFM, endpoint=True)

    # Cycle(s) over message(s)
    a1oTime = {}
    for iMS_STEP, iMS_IDX in enumerate(a1iFM):

        # Cast index to integer format
        iMS_IDX = int(iMS_IDX)

        # Get variable data
        oVar = oFile[iMS_IDX]

        # Get time information
        sFM_Year = str(oVar['year']).zfill(4)
        sFM_Month = str(oVar['month']).zfill(2)
        sFM_Day = str(oVar['day']).zfill(2)
        sFM_HH = str(oVar['hour']).zfill(2)
        sFM_MM = str(oVar['minute']).zfill(2)
        iFM_UTR = int(oVar['unitOfTimeRange'])
        iFM_P1 = int(oVar['P1'])
        iFM_P2 = int(oVar['P2'])
        iFM_TRI = int(oVar['timeRangeIndicator'])
        oTimeAnalysis = oVar.analDate
        oTimeValid = oVar.validDate

        # Get variable name
        sVarName = oVar.name
        sVarName = sVarName.encode('UTF-8')
        sVarName = sVarName.replace(' ', '_').lower()

        # Define variable in dictionary
        if sVarName not in a1oTime:
            a1oTime[sVarName] = {}
        else:
            pass

        # Define dictionary for each step
        oTime = {'Year': sFM_Year, 'Month': sFM_Month, 'Day': sFM_Day, 'Hour': sFM_HH, 'Minute': sFM_MM,
                 'TimeRangeUnit': iFM_UTR, 'TimeRangeIndicator': iFM_TRI,
                 'P1': iFM_P1, 'P2': iFM_P2,
                 'TimeAnalysis': oTimeAnalysis, 'TimeValidation': oTimeValid}

        # Store time information
        a1oTime[sVarName][iMS_IDX] = oTime

    # Return variable(s)
    return a1oTime

# -------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to get data variable
def getVarData(oFile, oGeoData=None):

    # Get file message(s)
    iFM = oFile.messages
    a1iFM = np.linspace(1, iFM, iFM, endpoint=True)

    # Cycle(s) over message(s)
    a1oVar = {}
    for iMS_STEP, iMS_IDX in enumerate(a1iFM):

        # Cast index to integer format
        iMS_IDX = int(iMS_IDX)

        # Get variable data
        oVar = oFile[iMS_IDX]
        oVarData = oVar.values
        # Get variable name
        sVarName = oVar.name
        sVarName = sVarName.encode('UTF-8')
        sVarName = sVarName.replace(' ', '_').lower()

        # Define variable in dictionary
        if sVarName not in a1oVar:
            a1oVar[sVarName] = {}
        else:
            pass

        # Store variable data
        if oGeoData is None:
            a1oVar[sVarName][iMS_IDX] = oVarData
        else:
            if oGeoData['CorrOrient'] is True:
                a1oVar[sVarName][iMS_IDX] = np.flipud(oVarData)
            else:
                a1oVar[sVarName][iMS_IDX] = oVarData

    # Return variable(s)
    return a1oVar

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to get geographical variable
def getVarGeo(oFile, iIndex=1):

    # Get geographical information
    try:

        # Get geographical data
        [a2dGeoY, a2dGeoX] = oFile[iIndex].latlons()
        # Check geographical orientation
        [a2dVarGeoX, a2dVarGeoY, bVarCorrOrient] = checkVarOrient(a2dGeoX, a2dGeoY)

        # Store geographical information
        a1oVarGeo = {'Longitude': a2dGeoX, 'Latitude': a2dGeoY, 'CorrOrient': bVarCorrOrient}

    except BaseException:

        Exc.getExc(' -----> WARNING: error in extracting file geographical data! Check input file!', 2, 1)
        a1oVarGeo = None

    # Return variable(s)
    return a1oVarGeo

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to check variable(s) orientation (O-E, S-N)
def checkVarOrient(a2dVarGeoX, a2dVarGeoY):

    dVarGeoY_LL = a2dVarGeoY[a2dVarGeoY.shape[0] - 1, 0]
    dVarGeoY_UL = a2dVarGeoY[0, 0]
    # dVarGeoY_UR = a2dVarGeoY[0, a2dVarGeoY.shape[1] - 1]
    # dVarGeoY_LR = a2dVarGeoY[a2dVarGeoY.shape[0] - 1, a2dVarGeoY.shape[1] - 1]

    # Debug
    # print(dVarGeoY_LL, dVarGeoY_UL, dVarGeoY_UR, dVarGeoY_LR)
    # plt.figure(1); plt.imshow(a2dVarGeoY); plt.colorbar(); plt.show()

    if dVarGeoY_LL > dVarGeoY_UL:
        a2dVarGeoY = np.flipud(a2dVarGeoY)
        bVarCorrOrient = True
    else:
        bVarCorrOrient = False

    return a2dVarGeoX, a2dVarGeoY, bVarCorrOrient

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to print file attributes
def printFileAttrs(oFile):
    for oData in oFile:
        print(oData.typeOfLevel, oData.level, oData.name, oData.validDate, oData.analDate, oData.forecastTime)
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to get file attributes
def getFileAttr(oFile, iIndex=None, oVarKeyNA=None):

    # Default argument
    if oVarKeyNA is None:
        oVarKeyNA = ['distinctLatitudes', 'distinctLongitudes',
                  'values', 'latLonValues',
                  'latitudes', 'longitudes']

    if iIndex is None:
        oVarHandle = oFile
    else:
        oVarHandle = oFile[iIndex]

    # Attributes
    oVarAttrs = {}
    for sVarKey in oVarHandle.keys():

        sVarKey = sVarKey.strip().encode('UTF-8')
        sVarKey = sVarKey.decode('utf-8')

        if sVarKey not in oVarKeyNA:

            try:
                if sVarKey == 'validDate':
                    oVarValue = oVarHandle.validDate
                elif sVarKey == 'analDate':
                    oVarValue = oVarHandle.analDate
                else:
                    oVarValue = oVarHandle[sVarKey]
                oVarAttrs.update({sVarKey: oVarValue})
            except BaseException:
                Exc.getExc(' -----> WARNING: file key ' +
                           sVarKey + ' not correctly retrieved Check input file!', 2, 1)
        else:
            pass

    return oVarAttrs

# --------------------------------------------------------------------------------
