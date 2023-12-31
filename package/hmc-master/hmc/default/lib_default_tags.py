"""
Library Features:

Name:          lib_default_tags
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
# Nothing to do here
#######################################################################################

# -------------------------------------------------------------------------------------
# Algorithm tags Data structure (undefined value is None)
ConfigTags = dict(Uc={'$UC': None},
                  Uh={'$UH': None},
                  Ct={'$CT': None},
                  Cf={'$CF': None},
                  CPI={'$CPI': None},
                  WTableHbr={'$WTABLEHBR': None},
                  SlopeMax={'$SLOPEMAX': None},
                  KSatRatio={'$KSATRATIO': None},
                  RunDomain={'$DOMAIN': None},
                  RunName={'$RUN': None},
                  RunMode={'$MODE': None},)

StaticTags = dict(VarName={'$VAR': None},)

DynamicTags = dict(Year={'$yyyy': None},
                   Month={'$mm': None},
                   Day={'$dd': None},
                   Hour={'$HH': None},
                   Minute={'$MM': None},
                   VarName={'$VAR': None},
                   RunMode={'$MODE': None},)
# -------------------------------------------------------------------------------------
