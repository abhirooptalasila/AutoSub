# AutoSub

- [AutoSub](#autosub)
  - [About](#about)
  - [Installation](#installation)
  - [Docker](#docker)
  - [How-to example](#how-to-example)
  - [How it works](#how-it-works)
  - [Motivation](#motivation)
  - [Contributing](#contributing)
  - [References](#references)

## About

AutoSub is a CLI application to generate subtitle files (.srt, .vtt, and .txt transcript) for any video file using either [Mozilla DeepSpeech](https://github.com/mozilla/DeepSpeech) or [Coqui STT](https://github.com/coqui-ai/STT). I use their open-source models to run inference on audio segments and [pyAudioAnalysis](https://github.com/tyiannak/pyAudioAnalysis) to split the initial audio on silent segments, producing multiple smaller files (makes inference easy).

⭐ Featured in [DeepSpeech Examples](https://github.com/mozilla/DeepSpeech-examples) by Mozilla

## Installation

* Clone the repo
    ```bash
    $ git clone https://github.com/abhirooptalasila/AutoSub
    $ cd AutoSub
    ```
* [OPTIONAL] Create a virtual environment to install the required packages. By default, AutoSub will be installed globally. All further steps should be performed while in the `AutoSub/` directory
    ```bash
    $ python3 -m pip install --user virtualenv
    $ virtualenv -p python3 sub
    $ source sub/bin/activate
    ```
* Use the corresponding requirements file depending on whether you have a GPU or not. If you want to install for a GPU, replace `requirements.txt` with `requirements-gpu.txt`. Make sure you have the appropriate [CUDA](https://deepspeech.readthedocs.io/en/v0.9.3/USING.html#cuda-dependency-inference) version
    ```bash
    $ pip install .
    ```
* Install FFMPEG. If you're on Ubuntu, this should work fine
    ```bash
    $ sudo apt-get install ffmpeg
    $ ffmpeg -version               # I'm running 4.1.4
    ```
* By default, if no model files are found in the root directory, the script will download v0.9.3 models for DeepSpeech or TFLITE model and Huge Vocab for Coqui. Use `getmodels.sh` to download DeepSpeech model and scorer files with the version number as argument. For Coqui, download from [here](https://coqui.ai/models)
    ```bash
    $ ./getmodels.sh 0.9.3
    ```
* For .tflite models with DeepSpeech, follow [this](https://github.com/abhirooptalasila/AutoSub/issues/41#issuecomment-968847604)


## Docker

* If you don't have the model files, get them
    ```bash
    $ ./getmodels.sh 0.9.3
    ```
* For a CPU build
    ```bash
    $ docker build -t autosub .
    $ docker run --volume=`pwd`/input:/input --name autosub autosub --file /input/video.mp4
    $ docker cp autosub:/output/ .
    ```
* For a GPU build that is reusable (saving time on instantiating the program)
    ```bash
    $ docker build --build-arg BASEIMAGE=nvidia/cuda:10.1-cudnn7-runtime-ubuntu18.04 --build-arg DEPSLIST=requirements-gpu.txt -t autosub-base . && \
    docker run --gpus all --name autosub-base autosub-base --dry-run || \
    docker commit --change 'CMD []' autosub-base autosub-instance
    ```
* Finally
    ```bash
    $ docker run --volume=`pwd`/input:/input --name autosub autosub-instance --file ~/video.mp4
    $ docker cp autosub:/output/ .
    ```

## How-to example

* The model files should be in the repo root directory and will be loaded/downloaded automatically. Incase you have multiple versions, use the `--model` and `--scorer` args while executing
* By default, Coqui is used for inference. You can change this by using the `--engine` argument with value `"ds"` for DeepSpeech
* For languages other than English, you'll need to manually download the model and scorer files. Check [here](https://discourse.mozilla.org/t/links-to-pretrained-models/62688) for DeepSpeech and [here](https://coqui.ai/models) for Coqui.
* After following the installation instructions, you can run `autosub/main.py` as given below. The `--file` argument is the video file for which subtitles are to be generated
    ```bash
    $ python3 autosub/main.py --file ~/movie.mp4
    ```
* After the script finishes, the SRT file is saved in `output/`
* The optional `--split-duration` argument allows customization of the maximum number of seconds any given subtitle is displayed for. The default is 5 seconds
    ```bash
    $ python3 autosub/main.py --file ~/movie.mp4 --split-duration 8
    ```
* By default, AutoSub outputs SRT, VTT and TXT files. To only produce the file formats you want, use the `--format` argument
    ```bash
    $ python3 autosub/main.py --file ~/movie.mp4 --format srt txt
    ```
* Open the video file and add this SRT file as a subtitle. You can just drag and drop in VLC.



## How it works

Mozilla DeepSpeech is an open-source speech-to-text engine with support for fine-tuning using custom datasets, external language models, exporting memory-mapped models and a lot more. You should definitely check it out for STT tasks. So, when you run the script, I use FFMPEG to **extract the audio** from the video and save it in `audio/`. By default DeepSpeech is configured to accept 16kHz audio samples for inference, hence while extracting I make FFMPEG use 16kHz sampling rate. 

Then, I use [pyAudioAnalysis](https://github.com/tyiannak/pyAudioAnalysis) for silence removal - which basically takes the large audio file initially extracted, and splits it wherever silent regions are encountered, resulting in smaller audio segments which are much easier to process. I haven't used the whole library, instead I've integrated parts of it in `autosub/featureExtraction.py` and `autosub/trainAudio.py`. All these audio files are stored in `audio/`. Then for each audio segment, I perform DeepSpeech inference on it, and write the inferred text in a SRT file. After all files are processed, the final SRT file is stored in `output/`.

When I tested the script on my laptop, it took about **40 minutes to generate the SRT file for a 70 minutes video file**. My config is an i5 dual-core @ 2.5 Ghz and 8GB RAM. Ideally, the whole process shouldn't take more than 60% of the duration of original video file. 


## Motivation

In the age of OTT platforms, there are still some who prefer to download movies/videos from YouTube/Facebook or even torrents rather than stream. I am one of them and on one such occasion, I couldn't find the subtitle file for a particular movie I had downloaded. Then the idea for AutoSub struck me and since I had worked with DeepSpeech previously, I decided to use it. 


## Contributing

I would love to follow up on any suggestions/issues you find :)


## References
1. https://github.com/mozilla/DeepSpeech/
2. https://github.com/tyiannak/pyAudioAnalysis
3. https://deepspeech.readthedocs.io/
