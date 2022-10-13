FROM python:3.8.14-bullseye

RUN apt-get update
RUN pip3 install --upgrade pip
RUN mkdir -p /srv
COPY requirements.txt /srv/requirements.txt
WORKDIR /srv
RUN pip3 install -r requirements.txt
COPY . /srv/
WORKDIR /srv/application
ENV PYTHONIOENCODING=utf8
ENV LC_ALL=en_US.utf-8
ENV LANG=en_US.utf-8
RUN chmod 777 /srv/application
CMD ["uwsgi","/srv/uwsgi.ini"]