FROM ghcr.io/mochi-hpc/mochi-spack-buildcache:mofka-0.6.2-juktd5mx7a2mycmnsdc3mm4lb4cnqxdj.spack

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y git

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

# copied from https://stackoverflow.com/questions/58269375/how-to-install-packages-with-miniconda-in-dockerfile
# Install wget to fetch Miniconda
RUN apt-get update && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install parsl

COPY parsl_stream.py .
COPY mofka_config.json .
COPY launch_mofka.sh .

ENTRYPOINT ["python", "parsl_stream.py"]