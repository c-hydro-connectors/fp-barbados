"""
Library Features:

Name:          lib_default_settings
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
# Nothing to do here
#######################################################################################

# -------------------------------------------------------------------------------------
# Settings general info
GeneralInfo = dict(
    Conventions='CF-1.6',
    title='HMC_DataTools_1.0.0 Run Manager',
    institution='CIMA Research Foundation - www.cimafoundation.org',
    website='http://continuum.cimafoundation.org',
    source='HMC_DataTools_1.0.0 Run Manager',
    history='Python Module - HMC_DataTools_1.0.0 Run Manager Module',
    references='http://cf-pcmdi.llnl.gov/ ; http://cf-pcmdi.llnl.gov/documents/cf-standard-names/ecmwf-grib-mapping',
    comment='Author(s): Fabio Delogu ; Simone Gabellani ; Francesco Silvestro',
    email='fabio.delogu@cimafoundation.org; '
          'simone.gabellani@cimafoundation.org; '
          'francesco.silvestro@cimafoundation.org',
    project='HMC_DataTools_1.0.0 - Hydrological Model Continuum',
    algorithm='HMC_DataTools_1.0.0 Run Manager - Version 2.0.6 (20161114)',
    model='HMC_DataTools_1.0.0 - Version 2.0.6 (20161114)',
)

# Settings parameters info
ParamsInfo = dict(
    Run_Params={
        'RunDomain': '$DOMAIN',
        'RunName': '$RUN',
        'RunMode': {'EnsMode': False,
                    'EnsVar':
                        {'VarName': '',
                         'VarMin': 0,
                         'VarMax': 0,
                         'VarStep': 0},
                    },
    },

    Run_VarExec={
        'RunModelExec': 'HMC_Model_V2_$RUN.x',
        'RunModelNamelist': '$DOMAIN.info.txt',
        'RunModelCLine': '$UC $UH $CT $CF $DOMAIN $CPI $RF $VMAX $SLOPEMAX',
    },

    Run_Log={
        'FileLog': 'log.txt'
    },

    Run_VarFile={
        'FileVarStatic': 'hmc_model_run-manager_varstatic_default.config',
        'FileVarDynamic': 'hmc_model_run-manager_vardynamic_default.config',
    },

    Run_Path={
        'PathTemp': '/Temp',
        'PathCache': '/Cache',
        'PathExec': '/Exec',
        'PathLibrary': '/Library',
        'PathInfo': '/Info',
    },

    Time_Params={
        'TimeNow': '197805221255',
        'TimeDelta': 0,
        'TimeStepObs': 0,
        'TimeStepFor': 0,
        'TimeStepCheck': 0,
        'TimeRestart': {'RestartStep': 0, 'RestartHH': '00'},
        'TimeWorldRef': {'RefType': 'gmt', 'RefLoad': 0, 'RefSave': 0},
        'TimeTcMax': -9999,
    },

    HMC_Params={
        'Ct': -9999,
        'Cf': -9999,
        'Uc': -9999,
        'Uh': -9999,
        'CPI': -9999,
        'Rf': -9999,
        'VMax': -9999,
        'SlopeMax': -9999,
    },

    HMC_Flag={
        'Flag_OS': -9999,
        'Flag_Restart': -9999,
        'Flag_FlowDeep': -9999,
        'Flag_Uc': -9999,
        'Flag_DtPhysConv': -9999,
        'Flag_Snow': -9999,
        'Flag_Snow_Assim': -9999,
        'Flag_DebugSet': -9999,
        'Flag_DebugLevel': -9999,
        'Flag_LAI': -9999,
        'Flag_Albedo': -9999,
    },

    HMC_Dt={
        'Dt_Model': -9999,
        'Dt_PhysConv': -9999,
    },

    HMC_Data={
        'ForcingGridSwitch': -9999,
        'ForcingScaleFactor': -9999,
        'ForcingGeo': [-9999.0, -9999.0],
        'ForcingRes': [-9999.0, -9999.0],
        'ForcingDims': [-9999, -9999],
        'ForcingDataThr': 90,
    },

)

# Settings geographical info
GeoSystemInfo = dict(
    epsg_code=4326,
    grid_mapping_name='latitude_longitude',
    longitude_of_prime_meridian=0.0,
    semi_major_axis=6378137.0,
    inverse_flattening=298.257223563,
)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Resume dictionary
FileSettings = dict(GeneralInfo=GeneralInfo, ParamsInfo=ParamsInfo, GeoSystemInfo=GeoSystemInfo)
# -------------------------------------------------------------------------------------
