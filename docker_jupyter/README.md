# Jupyter Notebooks for Epigenomics Data Analysis
The analysis and interpretation of epigenomics data uses complex pipelines. The Galaxy ToolSuite is rich but limited, restricting the analytical steps up to an intermediate point. In the case of the [galaxy workflows for epigenomics data analysis](https://hub.docker.com/r/mpaya/epigenomics_galaxy), the analysis generates alignments, peaks, density, counts and differential expression results. However, further processing required non-Galaxy tools and custom scripts that were better reported in [Jupyter notebooks](https://hub.docker.com/r/mpaya/epigenomics_jupyter
). In order to finish data analysis and generate some reports and figures, three self-descriptive notebooks are prepared:
* `1-bash_NB.ipynb` runs differential binding analysis with MAnorm and starts preparation of histone modification profiles over genes as heatmaps and metagene plots with ngs.plot.
* `2-R_NB.ipynb` annotates called peaks to genes, and generates some statistics and figures about ChIP-Seq (peak length, annotated peaks, density, differentially marked genes), RNA-Seq results (DEGs, counts) and combined (comparison of degree of differential expression and histone marking per gene). To reduce the code presented in this notebook, many functions were exported to `functions.R`.
* `3-bash_NB.ipynb` creates two gene plots: one separating genes by degree of RNA-Seq transcript level, and another with the histone mark profile after removing rows of very low or no expression (filtering done in the R notebook with the results from the heatmap in notebook 1).

These notebooks read genomic data from a test directory located at `$local_path/analysis/lib/`. This location is made readable by Jupyter when docker is run (see Instructions below), and custom files may be copied to this destination. The final paths may be modified manually in the notebooks. Current notebooks indicate the following files:
* `genes.annot`, which contains functional descriptions for each gene. The default format expects it to contain a header and the gene names on the first column.
* `genes.gff` with annotations in gff format.
* `genes.bed` with 4 columns (chr start end name).


## Instructions
### Prepare environment
A container is going to be prepared from the docker image stored at `mpaya/epigenomics_jupyter`. Three variables are used to specify some options.
* The epigenomics pipeline uses local files to continue data analysis, thus this container needs access to the local system; this is achieved by mapping an internal `work` location to a user's local path where the galaxy epigenomics pipeline was previously run. 
* A name can be given to this container to facilitate later recognition with `docker ps`.
* To visualize the web interface of Jupyter, a port to connect the Jupyter session started within the container to a local host needs to be specified. The default port used by Jupyter is 8888, and the same is selected in this example for the local port. If using another local instance of Jupyter, modify the port to avoid clashes.
```bash
local_path=~/DockerFolders/run_v1   # name for the export directory
jup_name=nb1                        # name of container
jup_port=8888                       # local port where Jupyter is run
```

### Download and activate the container
A container for the docker image is run specifying the base directory where the results from the analysis with Galaxy were exported. This container does not download further files into this location.
```bash
docker run \
-p $jup_port:8888 \
--name $jup_name \
-v "${local_path}"/analysis:/home/jovyan/work \
mpaya/epigenomics_jupyter:2.5
```
The first time a container is run, a link with the path and a token can be used to open the web interface of Jupyter, modifying the port as needed. The following times, the token must be listed as explained below.

On the left side of Jupyter Lab is the file system navigator. On `work`,  `lib` and `galaxy-res` are accessed by the notebooks to continue the analysis of these results. Navigate to `notebooks` and open them. By order, they may be run with the functionality `Kernel / Restart Kernel and Run All Cells`. Results from these steps are stored at `"${local_path}"/analysis/jupyter-res`.

### Retrieve token of running notebook
This step is required since a new token is generated each time the container is started, or when accessing Jupyter from a remote terminal.
```bash
## start notebook
docker start "${jup_name}"

## run interactive session
docker exec -it "${jup_name}" bash
jupyter notebook list
```

### Save notebooks
Notebooks that are provided in this image belong within the container, and modifications remain local to this image. Two options to save them locally are to download the notebooks to a local folder or to move them to a location within `~/work`. e.g. Select 'Save Notebook As...' and change 'notebooks' for 'work' on the pop7up window for them to be saved with the rest of results.

### Stop container when finished
Running Jupyter session may be stopped from the terminal where it was originally run with `CTRL+C`, if running in interactive mode, or from the terminal.
```
docker stop "${jup_name}"
```

### Cleanup
After data analysis has finished, downloaded docker image and folders linking to the docker container may be deleted.
```bash
# copy results to a diferent destination
my_dest="${local_path}"/test_run
mkdir -p my_dest
cp -r "${local_path}"/analysis/jupyter-res $my_dest

# delete results
sudo rm -rf ~/DockerFolders/"${dir_name}"/analysis/jupyter-res
```

#### Full cleanup
When finished completely with this pipeline, both the container and docker image can be deleted to free disk space.
```bash
# remove container
docker rm "${jup_name}"

# remove docker image
img=$(docker images | grep 'mpaya/epigenomics_jupyter' | awk '{print $3}')
docker rmi ${img}
```

