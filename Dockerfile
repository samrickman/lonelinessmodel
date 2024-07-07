FROM ubuntu:22.04
WORKDIR /models
COPY install_dependencies.sh .
COPY requirements.txt .
ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN ./install_dependencies.sh
ADD app .
# The model was too big to upload to GitHub so I split it. Put it back together:
RUN cat model/split_model/x** > model/pytorch_model.bin
ENTRYPOINT [ "python3.9", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]