FROM ubuntu
RUN apt-get update
RUN apt-get install git -y
RUN pip install --upgrade pip
COPY . /
