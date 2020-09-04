# AutoSub

- [AutoSub](#autosub)
  - [About](#about)
  - [Motivation](#motivation)
  - [Installation](#installation)
  - [How-to example](#how-to-example)
  - [How it works](#how-it-works)
  - [TO-DO](#to-do)
  - [Contributing](#contributing)
  - [References](#references)

## About

AutoSub is a CLI application to generate subtitle file (.srt) for any video file using [Mozilla DeepSpeech](https://github.com/mozilla/DeepSpeech). I use the DeepSpeech Python API to run inference on audio segments and [pyAudioAnalysis](https://github.com/tyiannak/pyAudioAnalysis) to split the initial audio on silent segments, producing multiple small files.

## Motivation

In the age of OTT platforms, there are still some who prefer to download movies/videos from YouTube/Facebook or even torrents rather than stream. I am one of them and on one such occasion, I couldn't find the subtitle file for a particular movie I had downloaded. Then the idea for AutoSub struck me and since I had worked with DeepSpeech previously, I decided to use it. 


## Installation

* Clone the repo. All further steps should be performed while in the `AutoSub/` directory
    ```bash
    $ git clone https://github.com/abhirooptalasila/AutoSub
    $ cd AutoSub
    ```
* Create a pip virtual environment to install the required packages
    ```bash
    $ python3 -m venv sub
    $ source sub/bin/activate
    $ pip3 install -r requirements.txt
    ```
* Download the model and scorer files from DeepSpeech repo. The scorer file is optional, but it greatly improves inference results.
    ```bash
    # Model file (~190 MB)
    $ wget https://github.com/mozilla/DeepSpeech/releases/download/v0.8.2/deepspeech-0.8.2-models.pbmm
    # Scorer file (~900 MB)
    $ wget https://github.com/mozilla/DeepSpeech/releases/download/v0.8.2/deepspeech-0.8.2-models.scorer
    ```
* Create two folders `audio/` and `output/` to store audio segments and final SRT file
    ```bash
    $ mkdir audio output
    ```

## How-to example

* After following the installation instructions, you can run `autosub/main.py` as given below. `--model` and `--scorer` arguments take the absolute paths of the respective files. The `--file` argument is the video file for which SRT file is to be generated
    ```bash
    $ python3 autosub/main.py --model /home/AutoSub/deepspeech-0.8.2-models.pbmm --scorer /home/AutoSub/deepspeech-0.8.2-models.scorer --file ~/movie.mp4
    ```
* After the script finishes, the SRT file is saved in `output/`
* Open the video file and add this SRT file as a subtitle, or you can just drag and drop in VLC.
* When I tested the script on my laptop, it took about 40 minutes to generate the SRT file for a 70 minutes video file. 

## How it works


## TO-DO


## Contributing


## References
1. https://github.com/mozilla/DeepSpeech/
2. https://github.com/tyiannak/pyAudioAnalysis
3. https://deepspeech.readthedocs.io/
4. 