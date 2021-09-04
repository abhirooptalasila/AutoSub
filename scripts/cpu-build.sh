#!/bin/bash
cd "$(dirname "$(readlink -f "$0")")"
cd ..
docker build -t autosub . 
