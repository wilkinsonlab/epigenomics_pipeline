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

ADD data /data

# Autostart script that is invoked during container start
CMD ["/usr/bin/startup"]

