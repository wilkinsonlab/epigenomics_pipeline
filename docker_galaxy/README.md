This galaxy instance has tools and workflows aimed at the analysis of epigenomics data, both ChIP-Seq and RNA-Seq. A script is provided to install Brassica genome and run the data analysis from paper (Submitted).

## Instructions
### prepare environment
When running docker-galaxy linking to a local directory, this will be created by docker under root user. Creating the target directory in advance facilitates handling of permissions.
```
dir_name=run_v1  # name for the export directory
mkdir -p ~/DockerFolders/"${dir_name}"
```

### download and activate the container
The docker-galaxy container will be run on daemon mode, mapping an export directory to a local path where results can be easily accessed, and mapping the web page to a local port where the galaxy instance can be viewed.
```
cont_name=run1   # name of container
local_port=8080

docker run \
-d \
-v ~/DockerFolders/"${dir_name}":/export/ \
-p ${local_port}:80 \
--name "${cont_name}" \
mpaya/epigenomics_galaxy:1.0
```

After download, galaxy will be available at `localhost:${local_port}`. This galaxy instance gives admin privileges to the default user, admin@galaxy.org with password `admin`.

### install Brassica genome and run data analysis
Included is a script that will prepare the environment and conduct the data analysis indicated on the paper. If not specified, the default port used is 8080. 
```
cd ~/DockerFolders/"${dir_name}"/galaxy-central/lib/brassica_data/
bash run_analysis.sh ${local_port}
```
