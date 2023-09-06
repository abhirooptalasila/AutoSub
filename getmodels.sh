#!/bin/bash

if [ -z $1 ]; then
	echo "Please provide as argument the model number you wish to download. E.G. 1.0.0"
	exit 1;
else
	model=$1
fi

model_url=https://github.com/coqui-ai/STT-models/releases/download/english%2Fcoqui%2Fv$model-huge-vocab/model.tflite
scorer_url=https://github.com/coqui-ai/STT-models/releases/download/english%2Fcoqui%2Fv$model-huge-vocab/huge-vocabulary.scorer

wget ${model_url} -O "coqui-v$model-english-huge-vocabulary.tflite"
wget ${scorer_url} -O "coqui-v$model-english-huge-vocabulary.scorer"

