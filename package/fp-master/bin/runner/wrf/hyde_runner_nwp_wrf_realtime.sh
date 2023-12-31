#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='HYDE RUNNER - NWP WRF - REALTIME'
script_version="1.5.0"
script_date='2019/10/16'

script_folder='/share/c-hydro/fp-master/'
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get file information
script_file='/share/c-hydro/fp-master/apps/wrf/FP_DynamicData_NWP_WRF_Barbados.py'
setting_file='/share/c-hydro/fp-master/apps/wrf/fp_configuration_nwp_wrf_barbados_realtime.json'

file_lock_start_raw='nwp_dynamicdata_wrf_lock_%YYYY%MM%DD%HH00_realtime_START.txt'
file_lock_end_raw='nwp_dynamicdata_wrf_lock_%YYYY%MM%DD%HH00_realtime_END.txt'

file_list=("wrfout_d02_%YYYY-%MM-%DD_%HH:00:00_PLEV_BIL.nc" )

folder_data_raw='/share/c-hydro/data/dynamic/source/wrf/%YYYY/%MM/%DD/%HH00/'
folder_lock_raw='/share/c-hydro/lock/'

time_n_min=0
time_n_max=36

thr_no_file=5

# Get information (-u to get gmt time)
time_system=$(date +"%Y-%m-%d %H:00")
# time_system=$(date -u +"%Y-%m-%d %H:00")
# time_system='2018-10-05 10.32' # DEBUG 
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Add path to pythonpath
export PYTHONPATH="${PYTHONPATH}:$script_folder"
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Set hour of the model starting from time system
hour_system=$(date +%H -d "$time_system")
if [[ "$hour_system" -ge 12 ]]; then
	time_run=$(date +%Y%m%d1200 -d "$time_system")
	time_now="$(date +%Y-%m-%d -d "$time_system") 12:00"
	time_now=$(date -d "$time_now" +'%Y-%m-%d %H:%M' )
else
	time_run=$(date +%Y%m%d0000 -d "$time_system")
	time_now="$(date +%Y-%m-%d -d "$time_system") 00:00"
	time_now=$(date -d "$time_now" +'%Y-%m-%d %H:%M' )
fi
#-----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info script start
echo " ==================================================================================="
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> START ..."
echo " ==> COMMAND LINE: " python3 $script_file -settingfile $setting_file -time $time_now [time_system $time_system]

# ----------------------------------------------------------------------------------------	
# Get time information
time_exe=$(date)

year=${time_now:0:4}
month=${time_now:5:2}
day=${time_now:8:2}
hour=${time_now:11:2}

# Define path data
folder_data_def=${folder_data_raw/"%YYYY"/$year}
folder_data_def=${folder_data_def/"%MM"/$month}
folder_data_def=${folder_data_def/"%DD"/$day}
folder_data_def=${folder_data_def/"%HH"/$hour}

folder_lock_def=${folder_lock_raw/"%YYYY"/$year}
folder_lock_def=${folder_lock_def/"%MM"/$month}
folder_lock_def=${folder_lock_def/"%DD"/$day}
folder_lock_def=${folder_lock_def/"%HH"/$hour}

# Define locking file(s)
file_lock_start_def=${file_lock_start_raw/"%YYYY"/$year}
file_lock_start_def=${file_lock_start_def/"%MM"/$month}
file_lock_start_def=${file_lock_start_def/"%DD"/$day}
file_lock_start_def=${file_lock_start_def/"%HH"/$hour}

file_lock_end_def=${file_lock_end_raw/"%YYYY"/$year}
file_lock_end_def=${file_lock_end_def/"%MM"/$month}
file_lock_end_def=${file_lock_end_def/"%DD"/$day}
file_lock_end_def=${file_lock_end_def/"%HH"/$hour}
# ----------------------------------------------------------------------------------------	

# ----------------------------------------------------------------------------------------
# Iteration(s) to search input file(s)
count_no_file=0
for file_name_raw in "${file_list[@]}"
do  
    
	for ((i=$time_n_min; i<=$time_n_max; i++)); do      
		
		time_step=$(date -d "$time_now $i hours" '+%Y-%m-%d %H:%M')   

		year_step=${time_step:0:4}
		month_step=${time_step:5:2}
		day_step=${time_step:8:2}
		hour_step=${time_step:11:2}

		file_name_def=${file_name_raw/"%YYYY"/$year_step}
		file_name_def=${file_name_def/"%MM"/$month_step}
		file_name_def=${file_name_def/"%DD"/$day_step}
		file_name_def=${file_name_def/"%HH"/$hour_step}

		path_file_def=$folder_data_def/$file_name_def
	   	
		echo " ===> SEARCH FILE: $path_file_def ... "
		if [ -f $path_file_def ]; then
		   	echo " ===> SEARCH FILE: $path_file_def ... DONE"
		    file_check=true
		else
		    echo " ===> SEARCH FILE: $path_file_def ... FAILED! FILE NOT FOUND!"
			file_check=false
			
		    file_name_previous=${file_name_raw/"%YYYY"/$year_step}
			file_name_previous=${file_name_previous/"%MM"/$month_step}
			file_name_previous=${file_name_previous/"%DD"/$day_step}
			file_name_previous=${file_name_previous/"%HH"/$hour_step_previous}

			path_file_previous=$folder_data_def/$file_name_previous
			
			count_no_file=$[$count_no_file +1]
			
			echo " ====> COUNT FILE NOT FOUND: $count_no_file ... "
			if (( count_no_file >= thr_no_file )); then
				echo " ====> COUNT FILE NOT FOUND: $count_no_file ... RUN BREAK"
				echo " ====> COUNT FILE NOT FOUND: $count_no_file >= TRESHOLD OF NO FILE"
				break
			else
				echo " ====> COUNT FILE NOT FOUND: $count_no_file ... COPY THE PREVIOUS FILE WITH CHANGING THE NAME. RUN CONTINUES"
				cp -v $path_file_previous $path_file_def
			fi
			
		fi
		
		hour_step_previous=$hour_step

	done

done

if $file_check; then
	echo " ===> SEARCH FILE(S) COMPLETED. ALL FILES ARE AVAILABLE"
else
	echo " ===> SEARCH FILE(S) INTERRUPTED. ONE OR MORE FILE(S) IN SEARCHING PERIOD ARE NOT AVAILABLE"
fi
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Run according with file(s) availability
if $file_check; then
	
	# ----------------------------------------------------------------------------------------	
	# Create folder(s)
	if [ ! -d "$folder_data_def" ]; then
		mkdir -p $folder_data_def
	fi
	if [ ! -d "$folder_lock_def" ]; then
		mkdir -p $folder_lock_def
	fi
	# ----------------------------------------------------------------------------------------

    #-----------------------------------------------------------------------------------------
    # Start
    echo " ===> EXECUTE SCRIPT ... "
    path_file_lock_def_start=$folder_lock_def/$file_lock_start_def  
    path_file_lock_def_end=$folder_lock_def/$file_lock_end_def
    #-----------------------------------------------------------------------------------------
    
    #-----------------------------------------------------------------------------------------
    # Run check
    if [ -f $path_file_lock_def_start ] && [ -f $path_file_lock_def_end ]; then
        
        #-----------------------------------------------------------------------------------------
        # Process completed
        echo " ===> EXECUTE SCRIPT ... SKIPPED!"
		echo " ===> ALL DATA HAVE BEEN PROCESSED DURING A PREVIOUSLY RUN"
        #-----------------------------------------------------------------------------------------
    
    elif [ -f $path_file_lock_def_start ] && [ ! -f $path_file_lock_def_end ]; then
        
        #-----------------------------------------------------------------------------------------
        # Process running condition
        echo " ===> EXECUTE SCRIPT ... SKIPPED!"
		echo " ===> SCRIPT STILL RUNNING ... WAIT FOR PROCESS END"
        #-----------------------------------------------------------------------------------------
        
    elif [ ! -f $path_file_lock_def_start ] && [ ! -f $path_file_lock_def_end ]; then
        
        #-----------------------------------------------------------------------------------------
        # Lock File START
        time_step=$(date +"%Y%m%d%H%S")
        echo " ==== SCRIPT START" >> $path_file_lock_def_start
        echo " ==== Script name: $script_name" >> $path_file_lock_def_start
        echo " ==== Script run time: $time_step" >> $path_file_lock_def_start
        echo " ==== Script exe time: $time_exe" >> $path_file_lock_def_start
        echo " ==== Script execution running ..." >> $path_file_lock_def_start
        #-----------------------------------------------------------------------------------------
		
		#-----------------------------------------------------------------------------------------
		# Run python script (using setting and time)
		python3 $script_file -settingfile $setting_file -time $time_run
		#-----------------------------------------------------------------------------------------
        
        #-----------------------------------------------------------------------------------------
        # Lock File END
        time_step=$(date +"%Y%m%d%H%S")
        echo " ==== SCRIPT END" >> $path_file_lock_def_end
        echo " ==== Script name: $script_name" >> $path_file_lock_def_end
        echo " ==== Script run time: $time_step" >> $path_file_lock_def_end
        echo " ==== Script exe time: $time_exe" >> $path_file_lock_def_end
        echo " ==== Script execution finished" >>  $path_file_lock_def_end
        #-----------------------------------------------------------------------------------------
        
        #-----------------------------------------------------------------------------------------
        # Exit
        echo " ===> EXECUTE SCRIPT ... DONE!"
        #-----------------------------------------------------------------------------------------
        
    else
        
        #-----------------------------------------------------------------------------------------
        # Exit unexpected mode
        echo " ===> EXECUTE SCRIPT ... FAILED!"
		echo " ===> SCRIPT ENDED FOR UNKNOWN LOCK CONDITION!"
        #-----------------------------------------------------------------------------------------
        
    fi
    #-----------------------------------------------------------------------------------------

else

    #-----------------------------------------------------------------------------------------
    # Exit
    echo " ===> EXECUTE SCRIPT ... FAILED!"
	echo " ===> SCRIPT INTERRUPTED! ONE OR MORE INPUT FILE(S) ARE UNAVAILABLE!"
    #-----------------------------------------------------------------------------------------
    
fi
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info script end
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> ... END"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------

