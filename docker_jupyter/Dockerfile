FROM jupyter/datascience-notebook:414b5d749704
MAINTAINER m.paya@upm.es
USER root

## Install system packages
RUN apt-get update && \
    apt-get install zlib1g-dev zip libbz2-dev pkg-config liblzma-dev -y && \
    apt-get autoremove -y

## Install R packages
USER jovyan
RUN echo 'install.packages(c("scales","gridExtra","BiocManager","fields","GGally","stringi"),repos="http://cran.r-project.org" )' | R --no-save
RUN echo 'BiocManager::install(c("GenomicFeatures", "ChIPpeakAnno","ShortRead"),ask = FALSE)' | R --no-save

## Install bash kernel
RUN pip install bash_kernel
RUN python -m bash_kernel.install

## Install Miniconda installer for conda
USER root
RUN mkdir /software 
RUN cd /software && \
    wget https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh && \
    bash Miniconda2-latest-Linux-x86_64.sh -b -p /software/miniconda2
ENV PATH="/software/miniconda2/bin:${PATH}"
ENV CONDA2 /software/miniconda2/bin
RUN ${CONDA2}/conda update -n base -c defaults conda -y && \
    ${CONDA2}/conda init && \
    conda config --set auto_activate_base false
	
## build MAnorm  (1.2.0)
RUN cd /software && \
    git clone https://github.com/shao-lab/MAnorm.git && \
    cd MAnorm && ${CONDA2}/pip install .

## install tools within conda environment
RUN conda create --name deeptools python=3.7 deeptools=3.3.1 -c bioconda
RUN conda create --name samtools python=3.7 samtools=1.9 -c bioconda

## install ngs.plot
COPY data/ngsplot-2.61.tar.gz /software/ngsplot-2.61.tar.gz
RUN cd /software && \
    tar xzf ngsplot-2.61.tar.gz
ENV PATH="/software/ngsplot/bin:${PATH}"
ENV NGSPLOT /software/ngsplot
RUN echo 'install.packages(c("doMC","caTools"),repos="http://cran.r-project.org" )' | R --no-save

## final settings
USER jovyan
ENV NB_USER jovyan
ENV NB_UID 1000
ENV HOME /home/${NB_USER}

USER root
ADD data/notebooks/ ${HOME}/notebooks
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

CMD ["jupyter", "lab", "--ip", "0.0.0.0"]
