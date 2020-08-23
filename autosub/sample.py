#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sample script to generate subs for video files

Dependencies: 
    DeepSpeech -> 0.8.2             # pip3 install deepspeech==0.8.2
    FFMPEG -> 4.1.4                  # sudo apt install ffmpeg
    Sox - > 14.4.2                    # sudo apt install sox

After installing DeepSpeech, download model and scorer files into the same directory
    Model (~180 MB): https://github.com/mozilla/DeepSpeech/releases/download/v0.8.2/deepspeech-0.8.2-models.pbmm
    Scorer (~900 MB) :https://github.com/mozilla/DeepSpeech/releases/download/v0.8.2/deepspeech-0.8.2-models.scorer
    
How to run:


Author: Abhiroop Talasila 
Date: 13th July 2020
E-mail: abhiroop.talasila@gmail.com
"""


import os
import glob
import wave
import sys
import json
import numpy as np
import subprocess
from deepspeech import Model, version 
from timeit import default_timer as timer

def extract_audio(video_file, video_file_name):
    command = "ffmpeg -hide_banner -loglevel warning -i {} -b:a 192k -ac 1 -ar 16000 -vn {}".format(video_file, os.path.join(os.getcwd(), "audio", video_file_name))
    try:
        ret = subprocess.call(command, shell=True)
    except Exception as e:
        print("Error: ", str(e))
    print("Extracted audio to audio/{}".format(video_file_name))
        


def convert_samplerate(audio_path, desired_sample_rate):
    sox_cmd = "sox {} --type raw --bits 16 --channels 1 --rate {} --encoding signed-integer --endian little --compression 0.0 --no-dither - ".format(
        quote(audio_path), desired_sample_rate)
    try:
        output = subprocess.check_output(
            shlex.split(sox_cmd), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("SoX returned non-zero status: {}".format(e.stderr))
    except OSError as e:
        raise OSError(e.errno, "SoX not found, use {}hz files or install it: {}".format(
            desired_sample_rate, e.strerror))

    return np.frombuffer(output, np.int16)

def ds_process_audio(ds_model, ds_scorer, video_file_name):
    ds = Model(ds_model)
    ds.enableExternalScorer(ds_scorer)
    
    audio_file = os.path.join(os.getcwd(), "audio", video_file_name)
    fin = wave.open(audio_file, 'rb')
    fs_orig = fin.getframerate()
    desired_sample_rate = ds.sampleRate()
    
    # Change sampling rate to required rate i.e 16000
    if fs_orig != desired_sample_rate:
        print("Warning: original sample rate ({}) is different than {}hz. Resampling might produce erratic speech recognition".format(fs_orig, desired_sample_rate), file=sys.stderr)
        audio = convert_samplerate(audio_file, desired_sample_rate)
    else:
        audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)

    audio_length = fin.getnframes() * (1/fs_orig)
    fin.close()
    
    print("\nRunning inference:", file=sys.stderr)
    inference_start = timer()

    # If JSON output is needed
    #if args.json:
    #print(metadata_json_output(ds.sttWithMetadata(audio, 3)))
    #else:
    print(ds.stt(audio))

    inference_end = timer() - inference_start
    print("Inference took %0.3fs for %0.3fs audio file" %
            (inference_end, audio_length), file=sys.stderr)


def main():
    print("AutoSub v0.1")
    print("Looking for DeepSpeech model and scorer files")
    
    for file in os.listdir():
        if file.endswith(".scorer"):
            print("Found: ", file)
            ds_scorer = os.path.join(os.getcwd(), file)
        if file.endswith(".pbmm"):
            print("Found: ", file)
            ds_model = os.path.join(os.getcwd(), file)
    
    try:
        ds_scorer
    except:
        print("Scorer file not found. Please enter absolute path:")
        ds_scorer = str(input(">>> "))
        if not ds_scorer.endswith(".scorer"):
            print("Invalid scorer file. Exiting")
            exit(1)
    try:
        ds_model
    except:
        print("Model file not found. Please enter absolute path:")
        ds_model = str(input(">>> "))
        if not ds_model.endswith(".model"):
            print("Invalid model file. Exiting")
            exit(1)
    
    print("Input Video file: ")
    video_file = str(input())
    video_file_name = video_file.split("/")[-1].split(".")[0] + ".wav"
    extract_audio(video_file, video_file_name)
    
    ds_process_audio(ds_model, ds_scorer, video_file_name)
    
    
if __name__ == "__main__":
    main()