#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import wave
import sys
import json
import numpy as np
import subprocess
from tqdm import tqdm
from deepspeech import Model, version 
from timeit import default_timer as timer
from segment_audio import silenceRemoval
#tqdm(enumerate(segmentLimits), ascii ="123456789$")
import re
def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)

def extract_audio(video_file, audio_file_name):
    command = "ffmpeg -hide_banner -loglevel warning -i {} -b:a 192k -ac 1 -ar 16000 -vn {}".format(video_file, os.path.join(os.getcwd(), "audio", audio_file_name))
    try:
        ret = subprocess.call(command, shell=True)
    except Exception as e:
        print("Error: ", str(e))
    print("Extracted audio to audio/{}".format(audio_file_name))
        


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

def ds_process_audio(ds, audio_segment):    
    audio_file = os.path.join(os.getcwd(), "audio", audio_segment)
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
    
    #print("\nRunning inference:", file=sys.stderr)
    #inference_start = timer()


    print(ds.stt(audio))

    #inference_end = timer() - inference_start
    #print("Inference took %0.3fs for %0.3fs audio file" %
    #        (inference_end, audio_length), file=sys.stderr)


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
    audio_file_name = video_file.split("/")[-1].split(".")[0] + ".wav"
    extract_audio(video_file, audio_file_name)
    
    ds = Model(ds_model)
    ds.enableExternalScorer(ds_scorer)
    
    print("Silence Removal")
    silenceRemoval(os.path.join(os.getcwd(), "audio", audio_file_name))
    
    for file in tqdm(sorted_alphanumeric(os.listdir(os.path.join(os.getcwd(), "audio")))):
        if file is not audio_file_name:
            ds_process_audio(ds, file)
    
    
    
    
if __name__ == "__main__":
    main()