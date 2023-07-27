#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='FP RUNNER - GROUND NETWORK WS'
script_version="1.0.0"
script_date='2018/09/23'

script_folder='/home/hsaf/hsaf_op_chain/'
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get file information
script_file='/home/hsaf/hsaf_op_chain/apps/ground_network/ws/FP_DynamicData_GroundNetwork_WS.py'
setting_file='/home/hsaf/hsaf_op_chain/apps/ground_network/ws/fp_configuration_groundnetwork_ws_realtime.json'

# Get information (-u to get gmt time)
time_now=$(date -u +"%Y%m%d%H00")
# time_now='201807230000' # DEBUG 
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Add path to pythonpath
export PYTHONPATH="${PYTHONPATH}:$script_folder"
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

