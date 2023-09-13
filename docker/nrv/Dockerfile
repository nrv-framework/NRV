FROM dolfinx/dolfinx:stable

# Install basic packages
RUN pip install nrv-py

# add environnement variable
ENV NRVPATH="/usr/local/lib/python3.10/dist-packages/nrv" 

# Import a first time nrv to compile mod files
RUN python3 -c "import nrv"