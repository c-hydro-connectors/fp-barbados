"""
Library Features:

Name:          lib_time
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging

import numpy as np
import datetime
from copy import deepcopy

from fp.default.lib_default_args import sLoggerName, sTimeFormat

from fp.utils.lib_utils_apps_time import getTimeNow

from fp.driver.configuration.drv_configuration_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# --------------------------------------------------------------------------------
# Method to update Data time workspace
def updateTimeData(oData, oDictUpd={}):

    for sDictKey, oDictValue in iter(oDictUpd.items()):

        if sDictKey in oData.keys():
            oData[sDictKey] = oDictValue
        else:
            pass
    return oData

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to compute arrival time (reference to a given hour)
def computeTimeArrival(sTime, iArrDay=1, a1oArrHour=['00', '12']):

    # Check list Data
    if a1oArrHour:

        oTime = datetime.datetime.strptime(sTime, sTimeFormat)

        oTimeRaw_TO = deepcopy(oTime)
        oTimeRaw_FROM = oTimeRaw_TO + datetime.timedelta(seconds=86400 * -iArrDay)

        oTimeRaw = oTimeRaw_FROM
        oTimeDelta = datetime.timedelta(seconds=86400)

        a1oTimeRaw = []
        while oTimeRaw <= oTimeRaw_TO:
            a1oTimeRaw.append(oTimeRaw.strftime(sTimeFormat))
            oTimeRaw += oTimeDelta

        a1oTimeArr_All = []
        for sTimeRaw in a1oTimeRaw:
            for sHourArr in a1oArrHour:
                oTimeRaw = datetime.datetime.strptime(sTimeRaw, sTimeFormat)
                oTimeArr = oTimeRaw.replace(hour=int(sHourArr), minute=0, second=0, microsecond=0)
                a1oTimeArr_All.append(oTimeArr.strftime(sTimeFormat))

        a1oTimeArr = []
        for sTimeArr in a1oTimeArr_All:
            oTimeArr = datetime.datetime.strptime(sTimeArr, sTimeFormat)

            if oTimeArr <= oTimeRaw_TO:
                a1oTimeArr.append(oTimeArr.strftime(sTimeFormat))
            else:
                pass

        a1oTimeArr = sorted(a1oTimeArr)

    else:
        a1oTimeArr = [sTime]

    return a1oTimeArr

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to get running time
def getTimeRun(sTimeNow='', sTimeArg='', sTimeType='GMT'):

    if not sTimeNow == '':
        [sTimeNow, sTimeNowFormat] = getTimeNow(sTimeNow, sTimeType)
        oTimeNow = datetime.datetime.strptime(sTimeNow, sTimeNowFormat)
    else:
        oTimeNow = None
    if not sTimeArg == '':
        [sTimeArg, sTimeArgFormat] = getTimeNow(sTimeArg, sTimeType)
        oTimeArg = datetime.datetime.strptime(sTimeArg, sTimeArgFormat)
    else:
        oTimeArg = None

    if oTimeArg:
        sTimeRun = oTimeArg.strftime(sTimeArgFormat)
    else:
        sTimeRun = oTimeNow.strftime(sTimeNowFormat)

    return sTimeRun
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to compute date(s) between two time(s)
def computeDateRange(oDate1, oDate2):
    for iN in range(int((oDate2 - oDate1).days) + 1):
        yield oDate1 + datetime.timedelta(iN)
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to convert time list to date-time objects
def convertTimeList2Obj(a1oTimeList):
    return [datetime.datetime.strptime(sTime, sTimeFormat) for sTime in a1oTimeList]
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to get restart time
def computeTimeRestart(sTime, oTimeRestartHH=['00'], iTimeStep=3600, iTimePeriod=0):

    # Check time restart definition
    if oTimeRestartHH is None:
        bTimeRoundHH = False
    else:
        bTimeRoundHH = True

    # Sort time restart list
    if bTimeRoundHH:
        if isinstance(oTimeRestartHH, str):
            oTimeRestartHH = [oTimeRestartHH]
        oTimeRestartHH.sort()

    # Compute time restart
    # sTimeFormat = defineTimeFormat(sTime)
    oTime = datetime.datetime.strptime(sTime, sTimeFormat)
    oTime = oTime.replace(minute=0, second=0)

    oTimeRaw_From = oTime - datetime.timedelta(seconds=int(iTimePeriod * iTimeStep))
    oTimeRaw_To = oTime + datetime.timedelta(seconds=int(iTimePeriod * iTimeStep))

    oTimeRaw_From = oTimeRaw_From.replace(hour=0, minute=0)
    oTimeRaw_To = oTimeRaw_To.replace(hour=23, minute=0)

    a1oTimeRaw = []
    if bTimeRoundHH:
        for oTimeRaw_Step in computeDateRange(oTimeRaw_From, oTimeRaw_To):
            for sTimeRestartHH in oTimeRestartHH:
                oTimeRaw_Step = oTimeRaw_Step.replace(hour=int(sTimeRestartHH))
                a1oTimeRaw.append(oTimeRaw_Step.strftime(sTimeFormat))
        a1oTimeRaw = convertTimeList2Obj(a1oTimeRaw)
    else:
        a1oTimeRaw = computeDateRange(oTimeRaw_From, oTimeRaw_To)

    a1oTimeFilter = []
    for oTimeFilter in a1oTimeRaw:
        if oTimeFilter <= oTime:
            a1oTimeFilter.append(oTimeFilter)

    a1oTimeFilter.append(oTime)
    for iTimeID, oTimeFilter in enumerate(reversed(a1oTimeFilter)):

        if iTimeID == iTimePeriod:
            oTimeRestart = oTimeFilter
            break
        else:
            oTimeRestart = None

    if oTimeRestart:
        sTimeRestart = oTimeRestart.strftime(sTimeFormat)
    else:
        sTimeRestart = None

    return sTimeRestart

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to define corrivation time
def computeTimeCorrivation(a2dGeoZ, a2dGeoX, a2dGeoY, dGeoXCSize, dGeoYCSize, dGeoNoData=np.nan):

    # -------------------------------------------------------------------------------------
    # Dynamic values
    dR = 6378388  # (Radius)
    dE = 0.00672267  # (Ellipsoid)

    # dx = (R * cos(lat)) / (sqrt(1 - e2 * sqr(sin(lat)))) * PI / 180
    a2dDX = (dR * np.cos(a2dGeoY * np.pi / 180)) / (np.sqrt(1 - dE * np.sqrt(np.sin(a2dGeoY * np.pi / 180)))) * np.pi / 180
    # dy = (R * (1 - e2)) / pow((1 - e2 * sqr(sin(lat))),1.5) * PI / 180
    a2dDY = (dR * (1 - dE)) / np.power((1 - dE * np.sqrt(np.sin(a2dGeoY / 180))), 1.5) * np.pi / 180

    # a2dGeoAreaKm = ((a2dDX / (1 / dGeoXCSize)) * (a2dDY / (1 / dGeoYCSize))) / 1000000  # [km^2]
    a2dGeoAreaM = ((a2dDX / (1 / dGeoXCSize)) * (a2dDY / (1 / dGeoYCSize)))  # [m^2]

    # Area, Mean Dx and Dy values (meters)
    dGeoDxMean = np.sqrt(np.nanmean(a2dGeoAreaM))
    dGeoDyMean = np.sqrt(np.nanmean(a2dGeoAreaM))

    # Compute domain pixels and area
    iGeoPixels = np.sum(np.isfinite(a2dGeoZ))
    dGeoArea = float(iGeoPixels) * dGeoDxMean * dGeoDyMean / 1000000

    # Debug
    # plt.figure(1)
    # plt.imshow(a2dGeoZ); plt.colorbar()
    # plt.show()

    # Concentration time [hour]
    iGeoTc = np.int(0.27 * np.sqrt(0.6 * dGeoArea) + 0.25)

    return iGeoTc

    # -------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
