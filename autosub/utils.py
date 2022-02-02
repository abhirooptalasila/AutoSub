#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import shutil
import logger
import subprocess
from stt import Model as SModel
from deepspeech import Model as DModel

_logger = logger.setup_applevel_logger(__name__)
_models = {
    "ds": {
        "model": "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm", 
        "scorer": "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer"
        },
    "stt": {
        "model": "https://github.com/coqui-ai/STT-models/releases/download/english/coqui/v0.9.3/model.tflite",
        "scorer": "https://github.com/coqui-ai/STT-models/releases/download/english%2Fcoqui%2Fv1.0.0-huge-vocab/huge-vocabulary.scorer"
    }
}


def sort_alphanumeric(data):
    """Sort function to sort os.listdir() alphanumerically
    Helps to process audio files sequentially after splitting

    Args:
        data : file name
    """

    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


def clean_folder(folder):
    """Delete everything inside a folder

    Args:
        folder : target folder
    """

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            _logger.warn(f"Failed to delete {file_path}. Reason: {e}")


def download_model(engine, fname):
    """Download model files, if not available locally

    Args:
        engine : "ds" for DeepSpeech and "stt" for Coqui STT
        fname : either of "model" or "scorer"
    """

    _logger.info(f"{fname.capitalize()} not found locally. Downloading")
    try:
        _file = _models[engine][fname]
        command = ["wget", _file, "-q", "--show-progress"]
        ret = subprocess.run(command).returncode
    except Exception as e:
        _logger.error(str(e))
        sys.exit(1)
    return _file.split("/")[-1]


def get_model(args, arg_name):
    """Will prioritze supplied arguments but if not, try to find files

    Args:
        args : run-time arguments
        arg_name : either model or scorer file
    """
    
    if arg_name == "model":
        if args.engine == "ds":
            arg_extension = ".pbmm"
        else:
            arg_extension = ".tflite"
    elif arg_name == "scorer":
        arg_extension = ".scorer"

    arg = args.__getattribute__(arg_name)
    
    if arg is not None:
        model = os.path.abspath(arg)
        if not os.path.isfile(model):
            _logger.error(f"Supplied file {arg} doesn't exist. Please supply a valid {arg_name} file via the --{arg_name} flag")
            sys.exit(1)
    else:
        models = [file for file in os.listdir() if file.endswith(arg_extension)]
        num_models = len(models)
    
        if num_models == 0:
            model = download_model(args.engine, arg_name)

        elif num_models != 1: 
            _logger.warn(f"Detected {num_models} {arg_name} files in local dir")
            if arg_name == 'model':
                _logger.error("Must specify pbmm model")
                sys.exit(1)
            else:
                _logger.warn("Please specify scorer using --scorer")
                model = ''
        else:
            model = os.path.abspath(models[0])                    
    
    _logger.info(f"{arg_name.capitalize()}: {model}")
    return(model)


def create_model(engine, model, scorer):
    """Instantiate model and scorer

    Args:
        engine : "ds" for DeepSpeech and "stt" for Coqui STT
        model : .pbmm model file
        scorer : .scorer file
    """

    try:
        if engine == "ds":
            ds = DModel(model)
        else:
            ds = SModel(model)
    except:
        _logger.error("Invalid model file")
        sys.exit(1)

    try:
        ds.enableExternalScorer(scorer)
    except:
        _logger.warn("Invalid scorer file. Running inference using only model file")
    return(ds)
