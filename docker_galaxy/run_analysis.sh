#!/bin/bash

PORT=8080
if [ ! -z $1 ]
then
    PORT=$1
fi
echo "Operating on localhost:$PORT"

## create directories to save results
GALAXY_RESULTS=../../../analysis/galaxy-res && \
    mkdir -p $GALAXY_RESULTS/{chipseq1,chipseq2,rnaseq}

## prepare python
a=$(pip freeze | grep bioblend)
if [ ! -z $a ]; 
then 
    echo bioblend not installed, installing bioblend
    pip install bioblend
fi

a=$(pip freeze | grep ephemeris)
if [ ! -z $a ]; 
then 
    echo ephemeris not installed, installing ephemeris
    pip install ephemeris
fi

## install genomes
# config file 1 contains instructions to use either local or web genome sources
echo "Installing and indexing B.rapa genome"
run-data-managers -g "http://localhost:"$PORT -a admin --config ./sys/manager_data1.yaml
run-data-managers -g "http://localhost:"$PORT -a admin --config ./sys/manager_data2.yaml

## run analysis
echo "=== running data analysis ==="
python ./sys/data_analysis.py $PORT
