ARG BASEIMAGE=ubuntu:18.04
#ARG BASEIMAGE=nvidia/cuda:10.1-cudnn7-runtime-ubuntu18.04

FROM ${BASEIMAGE}

ARG DEPSLIST=requirements.txt
#ARG DEPSLIST=requirements-gpu.txt

ENV PYTHONUNBUFFERED 1

COPY *.pbmm ./
COPY *.scorer ./
COPY setup.py ./
COPY autosub ./autosub

RUN DEBIAN_FRONTEND=noninteractive apt update && \
    apt -y install ffmpeg libsm6 libxext6 python3 python3-pip && \
    apt -y clean && \
	rm -rf /var/lib/apt/lists/*

COPY $DEPSLIST ./requirements.txt

# make sure pip is up-to-date
RUN python3 -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

RUN mkdir audio output

ENTRYPOINT ["python3", "autosub/main.py"]
