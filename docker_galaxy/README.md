# Galaxy Workflows for Epigenomics Data Analysis
This galaxy instance has installed tools and workflows aimed at the analysis of epigenomics data from both ChIP-Seq and RNA-Seq experiments. It is provided in a [Docker image](https://hub.docker.com/r/mpaya/epigenomics_galaxy) to facilitate download of a container with the full installation of Galaxy and required tools to execute the workflows. Data analysis is followed by the processes described in the notebooks provided with the image [`mpaya/epigenomics_jupyter`](https://hub.docker.com/r/mpaya/epigenomics_jupyter).

These containers were prepared to document and reproduce the data analysis performed on _Brassica rapa_ from our paper.
* Payá-Milans, M., Poza-Viejo, L., Martín-Uriz, P. S., Lara-Astiaso, D., Wilkinson, M. D., & Crevillén, P. (2019). [**Genome-wide analysis of the H3K27me3 epigenome and transcriptome in _Brassica rapa_.**](https://academic.oup.com/gigascience/article/8/12/giz147/5652252) GigaScience, 8(12). doi: [10.1093/gigascience/giz147](https://doi.org/10.1093/gigascience/giz147)

## Instructions
### Prepare the environment
When running docker-galaxy linking to a local directory, this will be created by docker under root user. Creating the target directory in advance facilitates handling of permissions.
```bash
local_path=~/DockerFolders/run_v1  # name for the export directory
mkdir -p "${local_path}"
```
The workflows contain a tool to export some of the results to this path. Since Galaxy is unable to create these export folders, they are created manually with permissions to allow all users to write on them (both Galaxy and Jupyter containers use custom users to write data). This file system is also recreated when running the test script.
```bash
galaxy_res="${local_path}"/analysis/galaxy-res
mkdir -m 777 -p $galaxy_res/{chipseq1,chipseq2,rnaseq}
```
The modification of this path should be followed by the modification of the export path on the workflows, to ensure proper download of Galaxy results, and on the Jupyter notebooks, to find them.

### Download and activate the container
The docker-galaxy container will be run on daemon mode, mapping an export directory to a local path where results can be easily accessed, and mapping the web page (accessed in port 80 within the container) to a local port where the galaxy instance can be viewed.
```bash
cont_name=run1
port=8080

docker run \
-d \
-v "${local_path}":/export/ \
-p $port:80 \
--name "${cont_name}" \
mpaya/epigenomics_galaxy:2.5
```

Download will take several minutes to prepare the galaxy instance on the specified local directory, requiring 16 Gb storage (run disk usage with sudo). When it's ready, galaxy will be available at `localhost:${port}`. 
```
xdg-open http://localhost:$port/
```
This galaxy instance can be accessed with admin privileges. 
* Default user: `admin@galaxy.org`
* Password: `admin`

### Run test
Some test data is prepared to confirm that the workflows work as expected. These data consist of PE ChIP-Seq and SE RNA-Seq reads in `.fastq` format, and some genomic resources (sequence in fasta format, gene annotations in gff and bed formats, functional annotations as table). A script is prepared to run Galaxy commands using the API, installing bioblend and ephemeris python packages if needed and using them to install the test genome and run the workflows with the test data from a python script. This test may take 10-15 min depending on resources.
```bash
bash ${local_path}/galaxy-central/lib/image_data/run_test.sh $port
```
The results are exported to `${local_path}/analysis/galaxy-res`. If not specified, the default port used is 8080. 

### Install _Brassica rapa_ genome and run data analysis
The original purpose of preparing this container was to report the methodology followed on our research, where we were searching for genes changing histone methylation for H3K27me3 and gene expression. Thus, we included is a script that prepares the environment and reproduces the data analysis indicated on our paper. The following command installs the _B. rapa chiifu_ v3.0 genome and workflows to download our _B. rapa_ reads from SRA archive and execute the analysis, including the version of epic2 0.0.14, originally used on the paper. 
```bash
bash ${local_path}/galaxy-central/lib/image_data/brassica_data/run_analysis.sh $port
```
The results are exported to `${local_path}/bra_analysis/galaxy-res`. If not specified, the default port used is 8080. 

### Cleanup
Galaxy exports each file with the name preceded by the history element number. i.e. if a same workflow is run twice, results will stack instead of overwrite, and won't be properly processed on Jupyter. This may be avoided by running a Galaxy instance each time on a different location, or modyfing the export folder in the workflows each time. Here we propose copying files to a different location and re-building the export folders. 
```bash
## preparation for next analysis
# copy results to a diferent destination
my_dest="${local_path}"/test_run
mkdir my_dest
cp -r "${local_path}"/analysis/galaxy-res $my_dest

# delete current Galaxy results after inspection
rm -fr "${local_path}"/analysis/galaxy-res

# prepare fresh file system 
galaxy_res="${local_path}"/analysis/galaxy-res
mkdir -m 777 -p $galaxy_res/{chipseq1,chipseq2,rnaseq}
```

#### Full cleanup
When finished completely with this pipeline, both the container and docker image can be deleted to free disk space.
```bash
# remove container
docker rm "${cont_name}"

# remove docker image
img=$(docker images | grep 'mpaya/epigenomics_galaxy' | awk '{print $3}')
docker rmi ${img}
```

# Workflows
On the analysis of next generation data, several software options are available, as well as treatment or processing of data. On the next workflows, we decided to trim reads with Trimmomatic and align with Bowtie2, tools already available in Galaxy. On the next sections, the approach taken for the analysis of each type of data is indicated. Workflows are also prepared to use SRA identifiers or raw reads as input. Outputs are automatically downloaded locally to `/export/analysis/galaxy-res/`, where `/export` is a local directory within the Galaxy container that is mapped to a user directory as explained previously.

## ChIP-Seq
This workflow is designed to find broad regions on the histone mark profile revealed by aligned PE reads. The input are paired-end reads, either downloaded from SRA or manually uploaded, distributed on two collections: forward and reverse. 

Initially, Trimmomatic performs adapter removal from TruSeq3 list, quality filtering by sliding window with required average quality of 15 over 4 bases, and requiring a minimum length of 20 bp. FastQC reports are produced from raw and trimmed reads. Trimmed reads are input to Bowtie2, with default settings except disable no-mixed and no-discordant behaviors, auto-assign read groups to Picard style, and very-sensitive end-to-end analysis mode. Aligned reads are then subjected to 3-step filtering. First, Samtools performs soft filtering keeping mapped reads with MAPQ above 1, and removing unmapped, unmated, secondary and duplicate reads. After soft filtering, duplicates are marked with Picard without removal. Finally, a second Samtools filtering step removes the marked duplicates. BAM files generated after mapping, first and last filtering steps are analyzed with Collect Alignment Summary Metrics from Picard, and processed to concatenate all outputs.
* Files with marked duplicates are merged separately by ChIP/INPUT samples to be used as input to MAnorm. 
* Files with removed duplicates are used to calculate coverage on bigwig files both on separate and merged samples. These also serve as input on peak calling.

Peak calling is performed with two methods: MACS2 and epic2. 
* On MACS2 most options are left as default. Effective genome size is set to 1 Gb, this value needs to be adjusted to the genome being used. Composite broad regions is selected, with cutoff 0.1.
* On epic2, The genome being used is test_genome, adjust genome information as suited. 

Requirements: 
* Filter list: list with names of ChIP samples (as opposed to input).

### ChIP-Seq analysis from fastq
This workflow requires fastq reads uploaded as fastqsanger and arranged in two collections, one with forward and the other with reverse reads. The names of the samples in both collections must be the same and must match those on the filter list with ChIP samples. 

### ChIP-Seq analysis from SRA
On this workflow, the input read data is downloaded from SRA archive with fastq dump and prepared to run the rest of the workflow. Sample names in the SRA list and filter list must match.

Requirements: 
* List of SRA identifiers in two columns; the first column has SRA ids, the second column has sample names. Used when invoking 'Get SRA PE'.

### Get SRA PE
In this workflow, the first column of the SRA list is cut and used as input for the tool Download Reads. The output are files named as 'SRA_ID:forward' or 'SRA_ID:reverse'. To match these files, a suffix is added to the names in the list of SRA ids; this modified list is later used to filter the reads as forward and reverse, and also to rename samples by the names on the second column. At the end, reads are grouped on "forward" and "reverse" collections.

### Galaxy tools that require user input
* Bowtie2
** Reference genome
* 3 X Collect Alignment Summary Metrics
** Reference genome
* epic2
** Reference genome
** Effective genome fraction 
** Gap size
* MACS2
** Effective genome size
** Composite broad regions
* 3 X bamCoverage
** Effective genome size


## RNA-Seq
This workflow was designed to analyze single-end RNA-Seq reads from a stranded experiment. The first step is trimming with Trimmomatic, removing adapters with TruSeq3 file, keeping a minimum quality 20 each 4 bases, and discarding reads below 20 bp. Quality control of reads before and after trimming is done with FastQC. Alignment with Bowtie2 of trimmed reads has predetermined test reference genome, read groups set with Picard style, 1 mismatch allowed in seed alignment, and end to end mode. Summary metrics on read alignments were collected with Picard. Read counts on genes were obtained with HTSeq, with the parameters (i) mode intersection (nonempty), (ii) stranded and (iii) minimum quality 10. Using a custom file with samples from one treatment co compare, counts results were separated and differential expression between conditions estimated with DESeq2. Factor and factor level may be adapted to user's data.

Requirements: 
* Filter list: list with names of treatment samples (as opposed to control).

### RNA-Seq analysis from fastq
This workflow requires fastq reads uploaded as fastqsanger arranged in a collection. The names of the samples in the collection must match those on the filter list with treatment samples. 

### RNA-Seq analysis from SRA
This workflow uses SRA identifiers to download single-end reads. 

Requirements: 
* List of SRA identifiers in two columns; the first column has SRA ids, the second column has sample names. Used when invoking 'Get SRA SE'.

### Get SRA SE
Fastq reads are downloaded from NCBI using the SRA identifiers on the list, which is also used to rename the collection items to their corresponding sample names.

### Galaxy tools that require user input
* Bowtie2
** Reference genome
* Collect Alignment Summary Metrics
** Reference genome
* htseq-count (default Yes)
** Strandedness
* DESeq2
** Factor names


## Modification of the export directory on workflows.
By default, the tool 'Export datasets to cluster' points to `/export/analysis/galaxy-res/chipseq1` / `chipseq2`, or `/export/analysis/galaxy-res/rnaseq`, by experiment, to save some results produced by the workflows. The paths can be modified manually, taking into account that this path has to be local to the Galaxy container, i.e. starting by `/export` which would correspond to `$local_path` when running the container. Besides manually modifying this path using the Galaxy GUI, two options for the command line are:

* Modify the path on a `.ga` workflow file and upload to galaxy
* Change the path on `Export datasets to cluster` tool using the Galaxy API.

### Bash solution
Path may be modified with simple substitution command. 
```bash
wf_dir=$local_path/galaxy-central/lib/image_data/workflows
w1=Galaxy-Workflow-ChIP-Seq_analysis_from_fastq.ga
w2=Galaxy-Workflow-RNA-Seq_analysis_from_fastq.ga

sed 's;xy-res/;xy-res/chipseq1;g' $wf_dir/$w1 > $wf_dir/ChIP-Seq_analysis_from_fastq-1.ga
sed 's;xy-res/;xy-res/chipseq2;g' $wf_dir/$w1 > $wf_dir/ChIP-Seq_analysis_from_fastq-2.ga
sed 's;xy-res;xy-res/rnaseq;g' $wf_dir/$w2 > $wf_dir/RNA-Seq_analysis_from_fastq.ga
```
The resulting workflows have to be manually uploaded to Galaxy via the GUI or installed with ephemeris.
```bash
workflow-install -g "http://localhost:"$port -u admin@galaxy.org \
    -p admin -a admin -w $wf_dir
```

### Python bioblend solution
Here is an example code that was used to prepare the _B. rapa_ workflows, finding the installed workflow to modify, changing the `analysis` folder to `bra_analysis` and uploading the modified ones.
```
#!/usr/bin/env python
from bioblend import galaxy
import re
import sys

## get port and galaxy instance
if len(sys.argv) > 1:
    port = sys.argv[1]
else:
    port = '8080'
gi = galaxy.GalaxyInstance(url='http://localhost:' + port, key='admin')

# get workflow and prepare to modify
print("preparing workflows")
wf1 = gi.workflows.get_workflows(name='B rapa ChIP-Seq analysis')[0]

ew11 = gi.workflows.export_workflow_dict(wf1['id'])
ew12 = gi.workflows.export_workflow_dict(wf1['id'])

ew11['name'] = u'Brapa ChIP-Seq analysis leaf'
ew12['name'] = u'Brapa ChIP-Seq analysis infl'

## modify export folder for chipseq
for i in range(1,len(ew11['steps'])):
    try:
        if re.search("export", ew11['steps'][str(i)]['tool_id']):
            ew11['steps'][str(i)]['tool_state'] = re.sub("analysis",
                "bra_analysis",ew11['steps'][str(i)]['tool_state'])
            ew12['steps'][str(i)]['tool_state'] = re.sub("analysis",
                "bra_analysis",ew12['steps'][str(i)]['tool_state'])
            ew12['steps'][str(i)]['tool_state'] = re.sub(
                "seq1","seq2",ew12['steps'][str(i)]['tool_state'])
    except:
            continue

## import modified workflows back to Galaxy
print("uploading workflows")
iw11 = gi.workflows.import_workflow_dict(ew11)
iw12 = gi.workflows.import_workflow_dict(ew12)
```
