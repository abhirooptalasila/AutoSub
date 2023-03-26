#!/bin/bash
# Meant to be used inside Docker. It scans the directory /input
# for WAV or MP4 files and executes the python script for each of them.

input_path=/input

shopt -s nullglob # prevent errors if no files are found

#Get model and scorer names from the model directory.
#Ignore if doesn't exist
model=$(find /deepspeech -name '*.pbmm' -print -quit)
scorer=$(find /deepspeech -name '*.scorer' -print -quit)

for file in "$input_path"/*.wav; do
    echo "Processing WAV $file"
    #If model and scorer are not empty, use them
    if [ -n "$model" ] && [ -n "$scorer" ]; then
        python3 -m autosub.main --wav "$file" --model "$model" --scorer "$scorer"
    else
        python3 -m autosub.main --wav "$file"
    fi
done

for file in "$input_path"/*.mp4; do
    echo "Processing MP4 $file"
    #If model and scorer are not empty, use them
    if [ -n "$model" ] && [ -n "$scorer" ]; then
        python3 -m autosub.main --file "$file" --model "$model" --scorer "$scorer"
    else
        python3 -m autosub.main --file "$file"
    fi
done
