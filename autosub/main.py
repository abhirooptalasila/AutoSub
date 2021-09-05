#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import wave
import shutil
import argparse
import subprocess
import numpy as np
from tqdm import tqdm
from deepspeech import Model, version 
from segmentAudio import silenceRemoval
from audioProcessing import extract_audio, convert_samplerate
from writeToFile import write_to_file

# Line count for SRT file
line_count = 0

def sort_alphanumeric(data):
    """Sort function to sort os.listdir() alphanumerically
    Helps to process audio files sequentially after splitting 

    Args:
        data : file name
    """
    
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)] 
    
    return sorted(data, key = alphanum_key)


def ds_process_audio(ds, audio_file, file_handle, vtt):  
    """Run DeepSpeech inference on each audio file generated after silenceRemoval
    and write to file pointed by file_handle

    Args:
        ds : DeepSpeech Model
        audio_file : audio file
        file_handle : SRT file handle
    """
    
    global line_count
    fin = wave.open(audio_file, 'rb')
    fs_orig = fin.getframerate()
    desired_sample_rate = ds.sampleRate()
    
    # Check if sampling rate is required rate (16000)
    # won't be carried out as FFmpeg already converts to 16kHz
    if fs_orig != desired_sample_rate:
        print("Warning: original sample rate ({}) is different than {}hz. Resampling might \
            produce erratic speech recognition".format(fs_orig, desired_sample_rate), file=sys.stderr)
        audio = convert_samplerate(audio_file, desired_sample_rate)
    else:
        audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)

    fin.close()
    
    # Perform inference on audio segment
    metadata = ds.sttWithMetadata(audio)
    infered_text = ''.join([x.text for x in metadata.transcripts[0].tokens])
    
    # File name contains start and end times in seconds. Extract that
    limits = audio_file.split(os.sep)[-1][:-4].split("_")[-1].split("-")
    
    # Get time cues for each word
    cues = [float(limits[0])] + [x.start_time + float(limits[0]) 
        for x in metadata.transcripts[0].tokens if x.text == " "]

    if len(infered_text) != 0:
        line_count += 1
        write_to_file(file_handle, infered_text, line_count, limits, vtt, cues)


def main():
    global line_count
    print("AutoSub\n")
         
    for x in os.listdir():
        if x.endswith(".pbmm"):
            print("Model: ", os.path.join(os.getcwd(), x))
            ds_model = os.path.join(os.getcwd(), x)
        if x.endswith(".scorer"):
            print("Scorer: ", os.path.join(os.getcwd(), x))
            ds_scorer = os.path.join(os.getcwd(), x)

    # Load DeepSpeech model 
    try:
        ds = Model(ds_model)
    except:
        print("Invalid model file. Exiting\n")
        sys.exit(1)
    
    try:
        ds.enableExternalScorer(ds_scorer)
    except:
        print("Invalid scorer file. Running inference using only model file\n")


    parser = argparse.ArgumentParser(description="AutoSub")
    parser.add_argument('--file', required=True,
                        help='Input video file')
    parser.add_argument('--vtt', dest="vtt", action="store_true",
                        help='Output a vtt file with cue points for individual words instead of a srt file')
    parser.add_argument('--overwrite', dest="overwrite", action="store_true",
                        help='Force Overwrite if SRT or VTT exists?')
    args = parser.parse_args()

    if os.path.isfile(args.file):
        input_file = args.file
        print("\nInput file:", input_file)
    else:
        print(args.file, ": No such file exists")
        sys.exit(1)
    
    base_directory = os.getcwd()
    output_directory = os.path.join(base_directory, "output")
    audio_directory = os.path.join(base_directory, "audio")
    video_file_name = os.path.splitext(os.path.split(input_file)[1])[0]
    audio_file_name = os.path.join(audio_directory, video_file_name + ".wav")
    srt_extension = ".srt" if not args.vtt else ".vtt"
    srt_file_name = os.path.join(output_directory, video_file_name + srt_extension)
    
    if os.path.exists(srt_file_name):
        if args.overwrite:
            try:
                os.remove(srt_file_name)
            except Exception as e:
                sys.exit('ERROR: %s exists and it cannot be deleted. REASON: %s. Please rectify before re-running.' % (srt_file_name, e))
        else:
            sys.exit('ERROR: SRT file %s exists and I do not have permission to overwrite it. Please use --overwrite to proceed.' % (srt_file_name)) 

    # Clean audio/ directory 
    for filename in os.listdir(audio_directory):
        file_path = os.path.join(audio_directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    # Extract audio from input video file
    extract_audio(input_file, audio_file_name)
    
    print("Splitting on silent parts in audio file")
    silenceRemoval(audio_file_name)
    
    # Output SRT or VTT file
    file_handle = open(srt_file_name, "a+")
    file_handle.seek(0)

    if args.vtt:
        file_handle.write("WEBVTT\n")
        file_handle.write("Kind: captions\n\n")
    
    print("\nRunning inference:")

    audiofiles=sort_alphanumeric(os.listdir(audio_directory))
    audiofiles.remove(os.path.split(audio_file_name)[1])

    for file in tqdm(audiofiles):
        ds_process_audio(ds, os.path.join(audio_directory, file), file_handle, args.vtt)

    if not args.vtt:        
        print("\nSRT file saved to", srt_file_name)
    else:
        print("\nVTT file saved to", srt_file_name)
            
    print("\nSRT file saved to", srt_file_name)
    file_handle.close()
        
if __name__ == "__main__":
    main()
