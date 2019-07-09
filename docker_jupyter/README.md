## Instructions for Jupyter notebooks
A container with steps to finalize data analysis is run mapping the directory containing the analysis results from Galaxy to an internal folder. Thus, results after Galaxy serve as input for Jupyter. Required annotation files are provided in the container.

### Prepare environment
Here, the same default port of jupyter is mapped locally. If using another local instance of jupyter, modify the port to avoid clashes.
```bash
dir_name=run_v1  # name for the export directory
cont_name=nb1   # name of container
local_port=8888
```

### Download and activate the container
```bash
docker run \
-p ${local_port}:8888 \
--name "${cont_name}" \
-v ~/DockerFolders/"${dir_name}"/analysis:/home/jovyan/work \
mpaya/epigenomics_jupyter:1.0
```

### Retrieve token of running notebook
This step is required since a new token is generated each time the container is started (`docker start ${cont_name}"`), in case the window does not autolaunch or on a remote terminal.
```
docker exec -it "${cont_name}" bash
jupyter notebook list
```

The notebooks and galaxy results are on their own folders. 
* Open and run the bash notebook (except last section)
* Open and run the R notebook
* Run last section of bash notebook

### Save notebooks
Initially, notebooks are on a folder inside the container. To save it to your local system, select 'Save Notebook As...' and change 'notebooks' for 'work' on the pop7up window for them to be saved with the rest of results.

### Stop container when finished
```
docker stop "${cont_name}"
```

### Cleanup
After data analysis has finished, downloaded docker image and folders linking to the docker container may be deleted.
```bash
# remove container
docker rm "${cont_name}"

# remove docker image
img=$(docker images | grep 'mpaya/epigenomics_jupyter' | awk '{print $3}')
docker rmi ${img}

# delete results
sudo rm -rf ~/DockerFolders/"${dir_name}"/analysis/jupyter-res
```

