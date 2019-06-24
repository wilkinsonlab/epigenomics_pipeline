FROM jupyter/datascience-notebook:abdb27a6dfbb
MAINTAINER m.paya@upm.es
USER root
# USER jovyan

## Load data
ADD data/ /data/

## Install R packages
RUN apt-get update && \
    apt-get install zlib1g-dev zip && \
    apt-get autoremove -y
RUN echo 'install.packages(c("scales","gridExtra","BiocManager"),repos="http://cran.r-project.org" )' | R --no-save
RUN echo 'BiocManager::install(c("GenomicFeatures", "ChIPpeakAnno","ShortRead"),ask = FALSE)' | R --no-save

## Install bash kernel
RUN pip install bash_kernel
RUN python -m bash_kernel.install

## Install additional software
RUN mkdir /software && cd /software && \
    wget https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh && \
    bash Miniconda2-latest-Linux-x86_64.sh -b -p /software/miniconda2
ENV PATH="/software/miniconda2/bin:${PATH}"
ENV CONDA2 /software/miniconda2/bin

## build MAnorm  (1.2.0)
RUN cd /software && \
    git clone https://github.com/shao-lab/MAnorm.git && \
    cd MAnorm && ${CONDA2}/pip install . && cd ..

# install ngs.plot
RUN cd /software && \
    mv /data/ngsplot-2.61.tar.gz . && \
    tar xzf ngsplot-2.61.tar.gz
ENV PATH="/software/ngsplot/bin:${PATH}"
ENV NGSPLOT /software/ngsplot
RUN echo 'install.packages(c("utils","doMC","caTools"),repos="http://cran.r-project.org" )' | R --no-save


USER jovyan

ENV NB_USER jovyan
ENV NB_UID 1000
ENV HOME /home/${NB_USER}

USER root
RUN mv /data/notebooks/ ${HOME}/notebooks
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

CMD ["jupyter", "lab", "--ip", "0.0.0.0"]
