## Instructions for Jupyter notebooks
A container with steps to finalize data analysis is run mapping the directory containing the analysis results from Galaxy to an internal folder. Thus, results after Galaxy serve as input for Jupyter. Required annotation files are provided in the container.

### prepare environment
```bash
dir_name=run_v1  # name for the export directory
cont_name=nb1   # name of container
```

### download and activate the container
```
docker run \
-p 8877:8888 \
--name "${cont_name}" \
-v ~/DockerFolders/"${dir_name}"/analysis:/home/jovyan/work \
mpaya/jupyter:1.0
```

### retrieve token of running notebook
This step is required since a new token is generated each time the container is started (`docker start ${cont_name}"`), in case the window does not autolaunch or on a remote terminal.
```
docker exec -it "${cont_name}" bash
jupyter notebook list
```

The notebooks and galaxy results are on their own folders. 
* Open and run the bash notebook (except last section)
* Open and run the R notebook
* Run last section of bash notebook

### save notebooks
Initially, notebooks are on a folder inside the container. To save it to your local system, select 'Save Notebook As...' and change 'notebooks' for 'work' and it'll be saved with the rest of results.

### stop container when finished
```
docker stop "${cont_name}"
```

### Cleanup
```bash
# remove container
docker rm "${cont_name}"

# remove docker image
img=$(docker images | grep 'mpaya/jupyter' | awk '{print $3}')
docker rmi ${img}

# delete results
sudo rm -rf ~/DockerFolders/"${dir_name}"/analysis/jupyter-res
```

