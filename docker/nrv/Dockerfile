FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV MAMBA_ROOT_PREFIX=/opt/micromamba
ENV NRV_ENV=/opt/nrv-env
ENV PATH=${NRV_ENV}/bin:${MAMBA_ROOT_PREFIX}/bin:$PATH

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
        "amd64")  MICROMAMBA_ARCH="64" ;; \
        "arm64")  MICROMAMBA_ARCH="aarch64" ;; \
        *) echo "Unsupported TARGETARCH=${TARGETARCH}" && exit 1 ;; \
    esac && \
    wget --quiet -O /tmp/micromamba.tar.bz2 "https://micro.mamba.pm/api/micromamba/linux-${MICROMAMBA_ARCH}/latest" && \
    mkdir -p "${MAMBA_ROOT_PREFIX}/bin" && \
    tar -xjf /tmp/micromamba.tar.bz2 -C "${MAMBA_ROOT_PREFIX}/bin" --strip-components=1 bin/micromamba && \
    rm -f /tmp/micromamba.tar.bz2 && \
    micromamba clean --all --yes

COPY docker/environment.yml /tmp/environment.yml

RUN micromamba create --yes --prefix "${NRV_ENV}" --file /tmp/environment.yml && \
    micromamba clean --all --yes

RUN python -V && \
    python -c "import nrv; print(f'NRV-v{nrv.__version__} import OK')"
