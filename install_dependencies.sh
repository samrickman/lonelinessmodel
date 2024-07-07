#!/bin/sh
# Install python 3.9 (non-interactive mode)
ARG DEBIAN_FRONTEND=noninteractive
apt-get update --fix-missing && \
apt-get install software-properties-common -y --no-install-recommends && \
apt install gpg-agent -y && \
add-apt-repository -y ppa:deadsnakes/ppa && \
apt-get install -y python3.9 --no-install-recommends python3-pip python3.9-distutils python3.9-dev build-essential

# Make sure 'python' opens this version
echo 'alias python=python3.9' >> ~/.bashrc

# Install requirements
python3.9 -m pip install -r requirements.txt --user

# Install Spacy sentence tokenizer model - this will download 3.5.0 as that equals spacy version
python3.9 -m spacy download en_core_web_sm
