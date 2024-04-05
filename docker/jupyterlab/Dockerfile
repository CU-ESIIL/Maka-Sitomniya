FROM jupyter/r-notebook:hub-4.0.1 

USER root

# Set up package manager
RUN apt-get install -y apt-transport-https && \
    apt-get clean && apt-get update && apt-get install -y software-properties-common && \
    add-apt-repository multiverse && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install some base software
RUN apt-get update --yes && \
    apt-get install --yes \
    fonts-dejavu \
    unixodbc \
    unixodbc-dev \
    r-base \
    r-cran-rodbc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add sudo to jovyan user
RUN apt update && \
    apt install -y sudo && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*
    
# This is where we can control which root permissions the jovyan user will have
ARG PRIV_CMDS='/bin/ch*,/bin/cat,/bin/gunzip,/bin/tar,/bin/mkdir,/bin/ps,/bin/mv,/bin/cp,/usr/bin/apt*,/usr/bin/pip*,/bin/yum,/opt,/opt/conda/bin/*,/usr/bin/*'

RUN usermod -aG sudo jovyan && \
    echo "$LOCAL_USER ALL=NOPASSWD: $PRIV_CMDS" >> /etc/sudoers
RUN addgroup jovyan
RUN usermod -aG jovyan jovyan

# Install RStudio
RUN apt-get update && apt-get install --yes gdebi-core && \
    wget https://download2.rstudio.org/server/jammy/amd64/rstudio-server-2023.09.1-494-amd64.deb && \
    gdebi -n rstudio-server-2023.09.1-494-amd64.deb && \
    rm rstudio-server-2023.09.1-494-amd64.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Geospatial libraries
RUN apt-get update && \
    apt install -y \
    gdal-bin \
    lbzip2 \
    libfftw3-dev \
    libgdal-dev \
    libgeos-dev \
    libgsl0-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libhdf4-alt-dev \
    libhdf5-dev \
    libjq-dev \
    libpq-dev \
    libproj-dev \
    libprotobuf-dev \
    libnetcdf-dev \
    libsqlite3-dev \
    libudunits2-dev \
    lsb-release \
    netcdf-bin \
    postgis \
    protobuf-compiler \
    sqlite3 \
    tk-dev \
    libfmt-dev \
    unixodbc-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Fix RStudio / Conda openssl version mismatch
RUN wget https://www.openssl.org/source/openssl-3.2.0.tar.gz && \
    tar xfz openssl-3.2.0.tar.gz && \
    mkdir openssl-build && cd openssl-build && \
    ../openssl-3.2.0/Configure --libdir=/lib/x86_64-linux-gnu/ && \
    make && \
    make install

# Update permissions for /opt/conda
RUN mkdir /usr/local/bin/start-notebook.d && \
    chown -R jovyan:users /opt/conda/share /usr/local/share /usr/local/bin/start-notebook.d 

USER jovyan

# Install jupyterlab and rstudio dependencies
RUN conda install -c conda-forge \ 
    jupyter_client \ 
    jupyter_core \ 
    jupyterlab_server \ 
    jupyter_server \
    r-rgl \
    r-htmlwidgets \
    r-htmltools && \ 
    jupyter lab clean

# reinstall R packages. Here is where you add any new R packages you would like to install 
RUN mamba install --quiet --yes \
    r-base \
    r-tidyverse \
    r-terra \
    r-future \
    r-future.apply \
    r-furrr \
    && \ 
    mamba clean --all -f -y

# Install Jupyter Lab Proxy extensions (cards in Launcher)
RUN pip install jupyter-rsession-proxy jupyter-server-proxy jupyter-shiny-proxy jupyterlab-git 

# Install Mamba Gator package manager
RUN rm -f ~/.jupyter/lab/workspaces/default* && \
    mamba install -y -c conda-forge mamba_gator

# Install and configure jupyter lab 
COPY jupyter_notebook_config.json /opt/conda/etc/jupyter/jupyter_notebook_config.json

# Rebuild the Jupyter Lab with new tools
RUN jupyter lab build

# Build Conda environment. Any packages you would like to install with conda need to be added to the environment.yml file in this Dockerfiles directory
RUN conda update -y conda && \
    conda config --remove channels conda-forge && \
    conda config --add channels conda-forge
WORKDIR /home/jovyan
COPY environment.yml /home/jovyan/ 
RUN mamba env create -f /home/jovyan/environment.yml
RUN . /opt/conda/etc/profile.d/conda.sh && conda deactivate && conda activate custom && python -m ipykernel install --name custom && pip install jupyter_contrib_nbextensions

# Install R packages from CRAN and GitHub
RUN R -e "remotes::install_github('tomroh/ecoregions')"
RUN R -e "install.packages('mblm', repos='http://cran.rstudio.com/')"

# Set any required environment variables 
ENV PROJ_LIB=/opt/conda/envs/custom/share/proj
RUN echo "PROJ_LIB=/opt/conda/envs/custom/share/proj" > /home/jovyan/.Renviron
