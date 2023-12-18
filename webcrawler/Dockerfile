FROM ubuntu:latest

RUN apt-get update

RUN apt-get install -y tor privoxy
ADD privoxy.conf /etc/privoxy/config

RUN apt -y install python3 python3-pip build-essential
RUN apt-get install -y curl libffi-dev libssl-dev libxml2-dev libxslt-dev
RUN pip3 install --upgrade pip

ADD requirements.txt /usr/requirements.txt
RUN pip3 install -r /usr/requirements.txt

ADD entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod 700 /usr/bin/entrypoint.sh

WORKDIR /opt

EXPOSE 6800 8118 9050

VOLUME /opt

ENV http_proxy http://127.0.0.1:8118
ENV https_proxy http://127.0.0.1:8118