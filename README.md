[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3298029.svg)](https://doi.org/10.5281/zenodo.3298029)

[__biotools:Epigenomics_Workflow_on_Galaxy_and_Jupyter__](https://bio.tools/Epigenomics_Workflow_on_Galaxy_and_Jupyter)

[__Epigenomics Workflow on Galaxy and Jupyter, RRID:SCR_017544__](https://scicrunch.org/browse/resourcedashboard)

# Epigenomics Workflow on Galaxy and Jupyter

Over the last decade, extensive epigenomics data is being generated. Data analysis may be challenging, and usually requires bioinformatics knowledge. Here, we present a 2-step full pipeline for combined ChIP-Seq and RNA-Seq data analysis.

## Contents

Two Docker images were prepared to run the analysis in a coordinated way. 
* First, a container running Galaxy will run the bulk analysis of ChIP-Seq and RNA-Seq data. The workflows are designed to use local read data or from SRA and to export results locally. Major steps in these workflows are:
    * Trimming with Trimmomatic
    * Mapping with Bowtie2
    * __ChIP-Seq__:
        * Alignment filtering and deduplication
        * Generation of BigWig files
        * Peak calling with MACS2 and epic2
    * __RNA-Seq__:
        * Read counting
        * Differential expression analysis with DESeq2
* The second container running Jupyter will use the files generated by Galaxy and finish data analysis. Two notebooks are provided with a preview of results from each command cell. They run:
    * __ChIP-Seq__:
        * Differential binding with MAnorm
        * Peak annotation
        * Metagene/heatmap plots of read distribution on genes
    * __Complete dataset__:
        * Functional annotation of results
        * Combination of ChIP-Seq and RNA-Seq results
        * Generation of tables and figures

Additionally, a script is provided to specifically run data analysis on a _Brassica_ dataset. In such case, Galaxy will download the raw sequencing files from SRA and run the analysis.

## Usage

### Docker commands
To use the images, Docker needs to be installed in the system ([link to documentation](https://docs.docker.com/install/)). Basic docker commands are:
* `docker images`: show all downloaded/built images.
* `docker run`: download (if needed) and run a docker image. A container is launched as an instance of that image. Multiple options are available to handle the interaction between local system and container.
* `docker ps -a`: list all containers.
* `docker stop <my_container>`: stop running container.
* `docker start <my_container>`: start a stopped container.
* `docker exec -it <my_container> bash`: access a container from a terminal.
* `docker rm <my_container>`: delete a stopped container.
* `docker rmi <image_id>`: delete a docker image.


### Galaxy in Docker
The epigenomics Galaxy image is based on `bgruening/galaxy-stable` ([link](https://github.com/bgruening/docker-galaxy-stable)). The key additions are:
* The default user has administrative privileges 
* Tools to run the epigenomics analysis are pre-installed
* Workflows are provided to run ChIP-Seq and RNA-Seq data analysis
* Accessory files to run _Brassica rapa_ data analysis

The workflows are designed to start from `.fastq` files or two-column text files indicating SRA accession numbers on the first column and file names on the second column. The default workflows use paired-end reads for ChIP-Seq data and single-end reads for RNA-Seq data. They can be customized to modify this behavior.

#### Quick start
Initialize the container.
```bash
## prepare local directory to contain galaxy
local_path=~/DockerFolders/run_v1  # name for the export directory
mkdir -p "${local_path}"

## run the container
cont_name=run1
port=8080

docker run \
-d \
-v "${local_path}":/export/ \
-p $port:80 \
--name "${cont_name}" \
mpaya/epigenomics_galaxy:2.5

## after download, open web browser
xdg-open http://localhost:$port/
```
Run test (may take 10-15 min)
```bash
bash ${local_path}/galaxy-central/lib/image_data/run_test.sh $port
```
Or create the filesystem tree for the Galaxy export tool before running any workflows.
```
galaxy_res="${local_path}"/analysis/galaxy-res
mkdir -m 777 -p $galaxy_res/{chipseq1,chipseq2,rnaseq}
```

### Jupyter in Docker
The epigenomics Jupyter image is based on `jupyter/datascience-notebook` ([link](https://jupyter-docker-stacks.readthedocs.io/en/latest/index.html)). It contains:
* Kernels
    * Python
    * R
    * bash
    * Julia
* Software
    * R and Python libraries for data analysis
    * MAnorm
    * ngs.plot
    * Miniconda 2 and 3
* Notebooks
    * Two bash notebooks for differential binding analysis and ChIP-Seq data plotting
    * An R notebook for the annotation and visualization of results

#### Quick start
Running this container for the first time on a local machine automatically opens Jupyter in a web browser. In Jupyter, the export folder is `~/work`. To continue with the data analysis from Galaxy, `~/work` is mapped to the `analysis` folder where the workflows have exported the results.
```bash
local_path=~/DockerFolders/run_v1
analysis_dir="${local_path}"/analysis
jup_name=nb1
jup_port=8888

docker run \
-p $jup_port:8888 \
--name $jup_name \
-v "${analysis_dir}":/home/jovyan/work \
mpaya/epigenomics_jupyter:2.5
```
After running the three notebooks in consecutive order, results will be available at `$analysis_dir/jupyter-res`.

## Output
Results are stored on the folder first created when running Galaxy, in this example `~/DockerFolders/run_v1/analysis`. In summary, results consist of:
* Galaxy
   * Basic read statistics (MultiQC)
   * Alignment files (.bam)
   * Track files (.bigwig)
   * ChIP-Seq peaks (.bed)
   * RNA-Seq results (counts and DEGs)
* Jupyter
   * Differentially bound peaks (table from MAnorm)
   * Annotated peaks
   * Metagene plots and heatmaps
   * Other figures and tables

