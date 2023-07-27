#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='FP RUNNER - GROUND NETWORK WS'
script_version="1.0.0"
script_date='2018/09/23'

script_folder='/share/c-hydro/'
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get file information
script_file='/share/c-hydro/fp-master/apps/ground_network/ws/FP_DynamicData_GroundNetwork_WS.py'
setting_file='/share/c-hydro/fp-master/apps/ground_network/ws/fp_configuration_groundnetwork_ws_history_barbados.json'

# Get information (-u to get gmt time)
#time_now=$(date -u +"%Y%m%d%H00")
time_now='201809300000' # DEBUG 
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Add path to pythonpath
export PYTHONPATH="${PYTHONPATH}:$script_folder"

# Export library for flood proofs package(s)
#export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/zlib-1.2.8/lib/
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/zlib-1.2.11/lib/
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/hdf5-1.8.17/lib/
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/netcdf-4.1.2/lib/
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/geos-3.5.0/lib/
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/proj-4.9.2/lib/
#export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/gdal-2.3.0/lib/

# Export binaries for flood proofs package(s)
export PATH=/share/c-hydro/library/hdf5-1.8.17/bin:$PATH
#export PATH=/share/c-hydro/library/zlib-1.2.8/bin:$PATH
export PATH=/share/c-hydro/library/zlib-1.2.11/bin:$PATH
export PATH=/share/c-hydro/library/netcdf-4.1.2/bin:$PATH
export PATH=/share/c-hydro/library/geos-3.5.0/bin:$PATH
export PATH=/share/c-hydro/library/proj-4.9.2/bin:$PATH
#export PATH=/share/c-hydro/library/gdal-2.3.0/bin:$PATH
#-----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info script start
echo " ==================================================================================="
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> START ..."
echo " ==> COMMAND LINE: " python3 $script_file -settingfile $setting_file -time $time_now

# Run python script (using setting and time)
python3 $script_file -settingfile $setting_file -time $time_now

# Info script end
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> ... END"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------

