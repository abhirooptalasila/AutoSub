#!/bin/bash
cd "$(dirname "$(readlink -f "$0")")"
cd ..
docker build --build-arg BASEIMAGE=nvidia/cuda:10.1-cudnn7-runtime-ubuntu18.04 --build-arg DEPSLIST=requirements-gpu.txt -t autosub-base . && docker run --gpus all --name autosub-base autosub-base || docker commit autosub-base autosub-instance && docker container rm autosub-base

