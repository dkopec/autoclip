# pull official base image
FROM python:3.11.2-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# copy project
COPY . .

# get ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
