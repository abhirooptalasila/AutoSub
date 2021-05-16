FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1

ARG model

RUN apt-get update
RUN apt-get install wget curl ffmpeg libsm6 libxext6 -y && apt-get clean

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

ENV model_url=https://github.com/mozilla/DeepSpeech/releases/download/v$model/deepspeech-$model-models.pbmm
ENV scorer_url=https://github.com/mozilla/DeepSpeech/releases/download/v$model/deepspeech-$model-models.scorer

RUN wget ${model_url}
RUN wget ${scorer_url}

RUN mkdir audio output

ENTRYPOINT ["python3", "autosub/main.py"]
