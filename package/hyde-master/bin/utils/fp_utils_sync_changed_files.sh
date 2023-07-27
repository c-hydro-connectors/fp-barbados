#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='FP UTILS - SYNC CHANGED FILE(S)'
script_version="1.0.0"
script_date='2018/10/16'
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Days period
declare -a list_days=(1 1 3 3 3)
# Declare folder(s) list
declare -a list_folders=(
    "/home/hsaf/hsaf_datasets/dynamic/outcome/h03b/" 
    "/home/hsaf/hsaf_datasets/dynamic/outcome/h05b/" 
    "/home/hsaf/hsaf_datasets/dynamic/outcome/h10/"
    "/home/hsaf/hsaf_datasets/dynamic/outcome/h12/"
    "/home/hsaf/hsaf_datasets/dynamic/outcome/h13/"
)

# Declare filename(s) list
declare -a list_filename=(   
    "/home/hsaf/hsaf_datasets/dynamic/ancillary/sync_file/hsaf_h03b_list.txt" 
    "/home/hsaf/hsaf_datasets/dynamic/ancillary/sync_file/hsaf_h05b_list.txt" 
    "/home/hsaf/hsaf_datasets/dynamic/ancillary/sync_file/hsaf_h10_list.txt" 
    "/home/hsaf/hsaf_datasets/dynamic/ancillary/sync_file/hsaf_h12_list.txt" 
    "/home/hsaf/hsaf_datasets/dynamic/ancillary/sync_file/hsaf_h13_list.txt" 
)
#-----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
# Info script start
echo " ==================================================================================="
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> START ..."

# Iterate over folder(s) and filename(s)
for index in ${!list_folders[*]}; do 
    echo " ===> Step: " $index " ... "
    echo " ===> Analyze folder: "${list_folders[$index]} 
    echo " ===> List changed file(s): "${list_filename[$index]}
    
    # Create destination folder of file list
    dir=$(dirname "${list_filename[$index]}")
    mkdir -p $dir
    
    # Change file list with updated information
    rm -f ${list_filename[$index]}
    find  ${list_folders[$index]} -mtime -${list_days[$index]}  -type f >> ${list_filename[$index]}
    #find  ${list_folders[$index]} -mmin -120  -type f >> ${list_filename[$index]}
    

    echo " ===> Step: " $index " ... DONE"
done

#find  h03b/ -mtime -1  -type f >>

# Info script end
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> ... END"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------
