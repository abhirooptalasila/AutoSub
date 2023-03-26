#!/bin/bash
#Downloaded models will be saved on ./model

#Flags:
# -m or --model: Model version. Default: 0.9.3
# -t or --type: Model type. Default: stt
# -h or --help: Show help
while [ "$1" != "" ]; do
	case $1 in
		-m | --model )          shift
								model=$1
								;;
		-t | --type )           shift
								type=$1
								;;
		-h | --help )           echo "Usage: getmodels.sh [-m model] [-t type] [-h help]"
								echo "Flags:"
								echo "-m or --model: Model version. Default: 0.9.3"
								echo "-t or --type: Model type. Default: stt"
								echo "-h or --help: Show help"
								exit
								;;
		* )                     echo "Usage: getmodels.sh [-m model] [-t type] [-h help]"
								echo "Flags:"
								echo "-m or --model: Model version. Default: 0.9.3"
								echo "-t or --type: Model type. Default: stt"
								echo "-h or --help: Show help"
								exit 1
	esac
	shift
done

#If type is ds, download DeepSpeech model, otherwise download Mozilla TTS model
mkdir -p ./deepspeech
if [ "$type" = "ds" ]; then
	model_url=https://github.com/mozilla/DeepSpeech/releases/download/v$model/deepspeech-$model-models.pbmm
	scorer_url=https://github.com/mozilla/DeepSpeech/releases/download/v$model/deepspeech-$model-models.scorer
	wget -O ./deepspeech/deepspeech-$model-models.pbmm $model_url
	wget -O ./deepspeech/deepspeech-$model-models.scorer $scorer_url
elif [ "$type" = "tts" ]; then
	model_url="https://github.com/coqui-ai/STT-models/releases/download/english/coqui/v$model/model.tflite"
	scorer_url="https://github.com/coqui-ai/STT-models/releases/download/english%2Fcoqui%2Fv1.0.0-huge-vocab/huge-vocabulary.scorer"
	wget -O ./deepspeech/model.tflite $model_url
	wget -O ./deepspeech/huge-vocabulary.scorer $scorer_url

