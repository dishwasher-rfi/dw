#!/bin/bash

#Usage: addmeta.sh hdf_dir meta_file
#
#hdf_dir: folder containing hdf5 files
# meta_file: file contaning metadata 

echo Metadata file: $2
echo Processing folder $1

parallel writemetadata.py ::: $1*.hdf5 ::: $2

