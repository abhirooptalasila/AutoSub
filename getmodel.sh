#!/bin/bash

if [ -z $1 ]; then
	echo "Please provide as argument the model number you wish to download. E.G. 0.9.3"
	exit 1;
else
	model=$1
fi

model_url=https://github.com/mozilla/DeepSpeech/releases/download/v$model/deepspeech-$model-models.pbmm
scorer_url=https://github.com/mozilla/DeepSpeech/releases/download/v$model/deepspeech-$model-models.scorer

wget ${model_url} && wget ${scorer_url}

