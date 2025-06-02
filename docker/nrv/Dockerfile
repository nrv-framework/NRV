FROM ubuntu:22.04

RUN apt-get update && apt-get install -y wget bash bzip2 && rm -rf /var/lib/apt/lists/*

#install mamba
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    sh /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

RUN apt-get update && apt-get install -y \
    build-essential libglu1-mesa libxi-dev libxmu-dev libglu1-mesa-dev libxrender1 libxcursor1 libxft2 libxinerama1 make libx11-dev git bison flex automake libtool libxext-dev libncurses-dev xfonts-100dpi cython3 libopenmpi-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
    
ENV PATH=/opt/conda/bin:$PATH

#install mamba
RUN conda install -y -n base -c conda-forge mamba

#install external dependencies #todo: create a yml file 
RUN mamba install -y -c conda-forge \
    python=3.12 \
    fenics-dolfinx=0.9.0 \
    mpich \
    python-gmsh \
    ipykernel \
    python=3.12  \
    #mpg \
    sysroot_linux-64=2.17  && \ 
    mamba clean --all --yes

#install nrv-py through pip
RUN pip install nrv-py

#run it to compile neuron's mod files
RUN python3 -c "import nrv"
