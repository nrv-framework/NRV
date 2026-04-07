FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH=/opt/conda/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    bash \
    bzip2 \
    ca-certificates \
    build-essential \
    libglu1-mesa \
    libxi-dev \
    libxmu-dev \
    libglu1-mesa-dev \
    libxrender1 \
    libxcursor1 \
    libxft2 \
    libxinerama1 \
    make \
    libx11-dev \
    git \
    bison \
    flex \
    automake \
    libtool \
    libxext-dev \
    libncurses-dev \
    xfonts-100dpi \
    cython3 \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

ARG TARGETARCH

RUN case "${TARGETARCH}" in \
        "amd64")  MINIFORGE_ARCH="x86_64" ;; \
        "arm64")  MINIFORGE_ARCH="aarch64" ;; \
        *) echo "Unsupported TARGETARCH=${TARGETARCH}" && exit 1 ;; \
    esac && \
    wget --quiet "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-${MINIFORGE_ARCH}.sh" -O /tmp/miniforge.sh && \
    bash /tmp/miniforge.sh -b -p /opt/conda && \
    rm -f /tmp/miniforge.sh && \
    conda config --system --set channel_priority strict && \
    conda clean --all --yes

COPY docker/nrv/environment.yml /tmp/environment.yml
RUN mamba env update -n base -f /tmp/environment.yml && \
    mamba clean --all --yes
RUN python -c "import nrv"