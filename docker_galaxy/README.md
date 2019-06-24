

## Instructions
### prepare environment
```
dir_name=run_v1  # name for the export directory
cont_name=run1   # name of container
mkdir -p ~/DockerFolders/"${dir_name}"
```

### download and activate the container
```
docker run \
-d \
-v ~/DockerFolders/"${dir_name}":/export/ \
-p 8080:80 \
--name "${cont_name}" \
mpaya/galaxy:1.0
```

This galaxy instance grants admin access to the default user, admin@galaxy.org.

### open a terminal into the container
```
docker exec -it "${cont_name}" bash
```

### run commands to install tools and run workflows
```
bash /data/run.sh
```

