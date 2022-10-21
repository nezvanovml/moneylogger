FROM python:3.8.14-bullseye

RUN apt-get update
RUN pip3 install --upgrade pip
RUN mkdir -p /srv
COPY requirements.txt /srv/requirements.txt
WORKDIR /srv
RUN pip3 install -r requirements.txt
COPY uwsgi.ini /srv/
COPY application /srv/application
RUN mkdir -p /srv/downloads
WORKDIR /srv/application
ENV PYTHONIOENCODING=utf8
ENV LC_ALL=en_US.utf-8
ENV LANG=en_US.utf-8
#RUN chmod -R 744 /srv
CMD ["uwsgi","/srv/uwsgi.ini"]