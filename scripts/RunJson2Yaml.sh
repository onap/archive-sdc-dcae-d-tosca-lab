#!/bin/bash

set -x
# The script should immediately exit if any command in the script fails.
# set -e
# This is the path for the json spac folder
file_path="../app/data/json-spac"

for f in $file_path/*
do
    filename=$(basename $f)
    name=$(echo $filename | cut -f 1 -d '.')
    
    echo $filename $name
    python ../app/model_create.py -i $f -o ../app/data/tosca_model/$name/ --name=$name -t ../app/data/import_file.yaml -m ../app/data/meta_model/meta_tosca_schema.yaml
    echo "-------------------"
done
