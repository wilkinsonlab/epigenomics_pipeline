# prepare galaxy instance
## install tools with playbook
cd /ansible
git clone https://github.com/afgane/galaxy-tools-playbook.git
cd galaxy-tools-playbook
ansible-galaxy install -f -r requirements_roles.yml -p roles
mv /data/sys/my_tool_list.yaml files/
sed 's;sample_tool;my_tool;' tools.yml > my_tools.yml
ansible-playbook my_tools.yml -i "localhost," --extra-vars galaxy_tools_api_key=admin

### set export path for export_to_cluster tool
export_prefix=/tool_deps/environment_settings/EXPORT_DIR_PREFIX/earlhaminst/export_to_cluster/9838eed606ad/env.sh
sed -i.bak 's:=;:=/export/analysis;:' "$export_prefix"

## download and index genome
run-data-managers -u admin@galaxy.org -p admin -a admin --config /data/sys/manager_data.yaml


# prepare and run analysis
## create the directory to save results
GALAXY_RESULTS=/export/analysis/galaxy-res
mkdir -p $GALAXY_RESULTS/{chipseq1,chipseq2,rnaseq}
chmod -R a+w $GALAXY_RESULTS

## install workflows
workflow-install -u admin@galaxy.org -p admin -a admin -w /data/workflows

## run the data analysis
python /data/sys/brapa_analysis.py
