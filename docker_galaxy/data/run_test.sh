#!/bin/bash
# exit when any command fails
set -e
cd $(dirname $0)

PORT=8080
if [ ! -z $1 ]
then
    PORT=$1
fi
echo "Operating on localhost:$PORT"

## create directories to save results
GALAXY_RES=../../../analysis/galaxy-res && \
    mkdir -m 777 -p $GALAXY_RES/{chipseq1,chipseq2,rnaseq}{,/bam_files}

## prepare python
a=$(pip freeze | grep bioblend)
if [ -z $a ]; 
then 
    echo bioblend not installed, installing bioblend
    pip install bioblend
fi

a=$(pip freeze | grep ephemeris)
if [ -z $a ]; 
then 
    echo ephemeris not installed, installing ephemeris
    pip install ephemeris
fi

## install genomes
# config file 1 contains instructions to use local genome sources
echo "Installing and indexing test genome"
run-data-managers -g "http://localhost:"$PORT -a admin \
   --overwrite --config ./test_data/scripts/manager_data1.yaml
run-data-managers -g "http://localhost:"$PORT -a admin \
   --overwrite --config ./test_data/scripts/manager_data2.yaml

## copy genomic data for jupyter
t_dir=$(dirname $GALAXY_RES)/lib/test_genome
mkdir -p ${t_dir} && cp -r ./test_data/genome/genes* ${t_dir}

## run analysis
echo "=== running data analysis ==="
python ./test_data/scripts/data_analysis.py $PORT
