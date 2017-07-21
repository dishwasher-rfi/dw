#!/bin/bash

#Usage: addmeta.sh hdf_dir meta_file
#
#hdf_dir: folder containing hdf5 files
# meta_file: file contaning metadata 

echo Metadata file: $2
for f in $1/*.hdf5;
do
    echo Processing $f...
    writemetadata.py $f $2
done 
