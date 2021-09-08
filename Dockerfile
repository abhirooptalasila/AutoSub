FROM python:3.8-slim-buster

ARG model

ENV PYTHONUNBUFFERED=1 \
    MODEL_URL=https://github.com/mozilla/DeepSpeech/releases/download/v$model/deepspeech-$model-models.pbmm \
    SCORER_URL=https://github.com/mozilla/DeepSpeech/releases/download/v$model/deepspeech-$model-models.scorer

COPY . .

RUN apt-get update && \
    apt-get install --no-install-recommends -y wget curl ffmpeg libsm6 libxext6 && \
    apt-get clean && \
    rm --recursive --force /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir -r requirements.txt && \
    wget ${MODEL_URL} && \
    wget ${SCORER_URL} && \
    mkdir audio output

ENTRYPOINT ["python3", "autosub/main.py"]
