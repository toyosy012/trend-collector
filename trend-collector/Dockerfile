FROM python:3.10.9-slim-buster

USER root

EXPOSE 8000

WORKDIR /root
COPY trendcollector /root
COPY requirements.* /root
RUN apt -y update && apt install -y locales && localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 &&\
    pip install --upgrade pip && pip install --upgrade setuptools pip-tools
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TERM xterm
RUN pip-compile && pip-sync

CMD ["python", "main.py"]

