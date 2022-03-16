#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import shlex
from . import logger
import subprocess
import numpy as np
from os.path import basename

try:
    from shlex import quote
except ImportError:
    from pipes import quote

_logger = logger.setup_applevel_logger(__name__)


def extract_audio(input_file, audio_file_name):
    """Extract audio from input video file and save to audio/ in root dir

    Args:
        input_file : input video file
        audio_file_name : save audio WAV file with same filename as video file
    """

    try:
        command = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-i", input_file, "-ac", "1", "-ar", "16000",
                   "-vn", "-f", "wav", audio_file_name]
        ret = subprocess.run(command).returncode
        _logger.info(f"Extracted audio to audio/{basename(audio_file_name)}")
    except Exception as e:
        _logger.error(str(e))
        sys.exit(1)


def convert_samplerate(audio_path, desired_sample_rate):
    """Convert extracted audio to the format expected by DeepSpeech
    ***WONT be called as extract_audio() converts the audio to 16kHz while saving***

    Args:
        audio_path : audio file path
        desired_sample_rate : DeepSpeech expects 16kHz

    Returns:
        numpy buffer : audio signal stored in numpy array
    """

    sox_cmd = "sox {} --type raw --bits 16 --channels 1 --rate {} --encoding signed-integer \
        --endian little --compression 0.0 --no-dither norm -3.0 - ".format(
        quote(audio_path), desired_sample_rate)
    try:
        output = subprocess.check_output(
            shlex.split(sox_cmd), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"SoX returned non-zero status: {e.stderr}")
    except OSError as e:
        raise OSError(e.errno, f"SoX not found, use {desired_sample_rate}hz files or install it: {e.strerror}")
    return np.frombuffer(output, np.int16)
