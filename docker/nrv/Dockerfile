FROM mambaorg/micromamba:latest



# Crée un environnement conda
RUN mamba create -n nrv_env python=3.12

# Active l’environnement et installe des packages
RUN mamba run -n nrv_env  mamba install -c conda-forge fenics-dolfinx "libblas=*=*blis" mpich conda-forge::python-gmsh

# Active l’environnement à chaque run (optionnel)
SHELL ["conda", "run", "-n", "nrv_env ", "/bin/bash", "-c"]

RUN pip install nrv-py

#CMD ["python"]


# Install basic packages
#RUN pip install nrv-py

# add environnement variable
#ENV NRVPATH="/usr/local/lib/python3.10/dist-packages/nrv"
#ENV PYTHONPATH="$NRVPATH:$PYTHONPATH"
#ENV PATH="$NRVPATH:$PATH"

# Import a first time nrv to compile mod files
RUN python3 -c "import nrv"