FROM python:3.7-alpine

RUN adduser -D dirk

WORKDIR /home/bv
RUN mkdir /logs

COPY requirements.txt requirements.txt
# Alpine Linux requires build environment
# https://github.com/docker-library/python/issues/312
# https://github.com/giampaolo/psutil/issues/872
# build-deps allows to remove build dependencies later on
# gcc, musl-dev and linux-headers are required for psutil
# alpine-sdk is required for pandas
#  libffi-dev openssl-dev is required for gunicorn
RUN apk update
RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers alpine-sdk
RUN python -m venv bvenv
RUN bvenv/bin/pip install --upgrade pip
RUN bvenv/bin/pip install -r requirements.txt
# RUN apk del .build-deps gcc musl-dev linux-headers alpine-sdk

# COPY properties properties
COPY lib lib
COPY load_murcs load_murcs
# COPY fromflask.py config.py boot.sh .env .flaskenv ./
# RUN chmod +x boot.sh

RUN chown -R dirk:dirk ./
USER dirk

# EXPOSE 5000
# ENTRYPOINT ["./boot.sh"]