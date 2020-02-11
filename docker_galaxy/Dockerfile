FROM bgruening/galaxy-stable:18.05
MAINTAINER m.paya@upm.es
USER root

## have a working epic2 tool
ENV GALAXY_CONFIG_TOOL_CONFIG_FILE=config/tool_conf.xml.sample,config/shed_tool_conf.xml,config/my_tools.xml
ADD epic2/epic2 /galaxy-central/tools/epic2
ADD epic2/my_tools.xml /galaxy-central/config
RUN for f in "--upgrade pip" pysam cython conda epic2==0.0.14; do pip install $f; done

## grant admin access to default user
RUN sed 's;.*admin_users:.*;  admin_users: admin@galaxy.org;' /galaxy-central/config/galaxy.yml.sample > /galaxy-central/config/galaxy.yml

## import data
ENV data_path=/galaxy-central/lib/image_data
ADD data ${data_path}

## install tools
RUN install-tools ${data_path}/sys/my_tool_list.yaml

## install workflows
ADD install_workflows_wrapper.sh /usr/bin/install-workflows
RUN chmod +x /usr/bin/install-workflows
RUN install-workflows ${data_path}/workflows

## set export path for export_to_cluster tool
RUN export_prefix=/tool_deps/environment_settings/EXPORT_DIR_PREFIX/earlhaminst/export_to_cluster/9838eed606ad/env.sh && \
    sed -i.bak 's:=;:=/export/analysis;:' "$export_prefix"

# Autostart script that is invoked during container start
CMD ["/usr/bin/startup"]
