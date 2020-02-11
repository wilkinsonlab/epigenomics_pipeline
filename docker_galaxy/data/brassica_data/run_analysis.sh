#!/bin/bash
set -e
cd $(dirname $0)

PORT=8080
if [ ! -z $1 ]
then
    PORT=$1
fi
echo "Operating on localhost:$PORT"

## create directories to save results
GALAXY_RES=../../../../bra_analysis/galaxy-res && \
    mkdir -m 777 -p $GALAXY_RES/{chipseq1,chipseq2,rnaseq}

## copy genomic data for jupyter
g_dir=$(dirname $GALAXY_RES)/lib/brapa_genome
mkdir -p ${g_dir} && cp ./files/*.{txt,bed,gff} ${g_dir}
cp -r brapa_nb $(dirname $GALAXY_RES) 

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

## install genome
# config file 1 contains instructions to use either local or web genome sources
echo "Installing and indexing B.rapa genome"
run-data-managers -g "http://localhost:"$PORT -a admin --config ./scripts/manager_data1.yaml
run-data-managers -g "http://localhost:"$PORT -a admin --config ./scripts/manager_data2.yaml

## install workflows
workflow-install -g "http://localhost:"$PORT -u admin@galaxy.org \
    -p admin -a admin -w ./workflows

## run analysis
echo "=== running data analysis ==="
python ./scripts/data_analysis.py $PORT
