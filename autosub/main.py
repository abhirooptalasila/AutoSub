#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import wave
from . import logger
import argparse

import numpy as np
from tqdm import tqdm

from .utils import *
from .writeToFile import write_to_file
from .audioProcessing import extract_audio
from .segmentAudio import remove_silent_segments

_logger = logger.setup_applevel_logger(__name__)

# Line count for SRT file
line_count = 1


def ds_process_audio(ds, audio_file, output_file_handle_dict, split_duration):
    """sttWithMetadata() will run DeepSpeech inference on each audio file 
    generated after remove_silent_segments. These files contain start and end 
    timings in their title which we use in srt file. 

    Args:
        ds : DeepSpeech Model
        audio_file : audio file
        output_file_handle_dict : Mapping of subtitle format (eg, 'srt') to open file_handle
        split_duration: for long audio segments, split the subtitle based on this number of seconds
    """

    global line_count
    fin = wave.open(audio_file, 'rb')
    audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)
    fin.close()

    metadata = ds.sttWithMetadata(audio)
    limits = audio_file.split(os.sep)[-1][:-4].split("_")[-1].split("-")

    # Run-on sentences are inferred as a single block, so write the sentence out as multiple separate lines
    # based on a user-provided split duration.
    current_token_index = 0
    split_start_index = 0
    previous_end_time = 0
    # timestamps of word boundaries
    cues = [float(limits[0])]
    num_tokens = len(metadata.transcripts[0].tokens)
    # Walk over each character in the current audio segment's inferred text
    while current_token_index < num_tokens:
        token = metadata.transcripts[0].tokens[current_token_index]
        # If at a word boundary, get the timestamp for VTT cue data
        if token.text == " ":
            cues += [float(limits[0]) + token.start_time]
        # time duration is exceeded and at the next word boundary
        needs_split = ((token.start_time - previous_end_time) > split_duration) and token.text == " "
        is_final_character = current_token_index + 1 == num_tokens
        # Write out the line
        if needs_split or is_final_character:
            # Determine the timestamps
            split_limits = [float(limits[0]) + previous_end_time, float(limits[0]) + token.start_time]
            # Convert character list to string. Upper bound has plus 1 as python list slices are [inclusive, exclusive]
            split_inferred_text = ''.join(
                [x.text for x in metadata.transcripts[0].tokens[split_start_index:current_token_index + 1]])
            write_to_file(output_file_handle_dict, split_inferred_text, line_count, split_limits, cues)
            # Reset and update indexes for the next subtitle split
            previous_end_time = token.start_time
            split_start_index = current_token_index + 1
            cues = [float(limits[0])]
            line_count += 1
        current_token_index += 1

    if "txt" in output_file_handle_dict.keys():
        output_file_handle_dict["txt"].write("\n\n")


def main():
    global line_count
    supported_output_formats = ["srt", "vtt", "txt"]
    supported_engines = ["ds", "stt"]

    parser = argparse.ArgumentParser(description="AutoSub")
    parser.add_argument("--format", choices=supported_output_formats, nargs="+",
                        help="Create only certain output formats rather than all formats",
                        default=supported_output_formats)
    parser.add_argument("--split-duration", dest="split_duration", type=float, default=5,
                        help="Split run-on sentences exceededing this duration (in seconds) into multiple subtitles")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true",
                        help="Perform dry-run to verify options prior to running. Also useful to instantiate \
                            cuda/tensorflow cache prior to running multiple times")
    parser.add_argument("--engine", choices=supported_engines, nargs="?", default="stt",
                        help="Select either DeepSpeech or Coqui STT for inference. Latter is default")
    parser.add_argument("--file", required=False, help="Input video file")
    parser.add_argument("--model", required=False, help="Input *.pbmm model file")
    parser.add_argument("--scorer", required=False, help="Input *.scorer file")
    
    args = parser.parse_args()
    
    #print(sys.argv[0:])
    _logger.info(f"ARGS: {args}")

    ds_model = get_model(args, "model")
    ds_scorer = get_model(args, "scorer")

    if args.dry_run:
        create_model(args.engine, ds_model, ds_scorer) 
        if args.file is not None:
            if not os.path.isfile(args.file):
                _logger.warn(f"Invalid file: {args.file}")
        sys.exit(0)

    if args.file is not None:
        if os.path.isfile(args.file):
            input_file = args.file
            _logger.info(f"Input file: {args.file}")
        else:
            _logger.error(f"Invalid file: {args.file}")
            sys.exit(1)
    else:
        _logger.error("One or more of --file or --dry-run are required")
        sys.exit(1)

    base_directory = os.getcwd()
    output_directory = os.path.join(base_directory, "output")
    audio_directory = os.path.join(base_directory, "audio")
    video_prefix = os.path.splitext(os.path.basename(input_file))[0]
    audio_file_name = os.path.join(audio_directory, video_prefix + ".wav")
    
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(audio_directory, exist_ok=True)
    output_file_handle_dict = {}

    for format in args.format:
        output_filename = os.path.join(output_directory, video_prefix + "." + format)
        # print("Creating file: " + output_filename)
        output_file_handle_dict[format] = open(output_filename, "w")
        # For VTT format, write header
        if format == "vtt":
            output_file_handle_dict[format].write("WEBVTT\n")
            output_file_handle_dict[format].write("Kind: captions\n\n")

    clean_folder(audio_directory)
    extract_audio(input_file, audio_file_name)

    _logger.info("Splitting on silent parts in audio file")
    remove_silent_segments(audio_file_name)

    audiofiles = [file for file in os.listdir(audio_directory) if file.startswith(video_prefix)]
    audiofiles = sort_alphanumeric(audiofiles)
    audiofiles.remove(os.path.basename(audio_file_name))

    _logger.info("Running inference...")
    ds = create_model(args.engine, ds_model, ds_scorer) 

    for filename in tqdm(audiofiles):
        audio_segment_path = os.path.join(audio_directory, filename)
        ds_process_audio(ds, audio_segment_path, output_file_handle_dict, split_duration=args.split_duration)

    for format in output_file_handle_dict:
        file_handle = output_file_handle_dict[format]
        _logger.info(f"{format.upper()}, file saved to, {file_handle.name}")
        file_handle.close()


if __name__ == "__main__":
    main()
