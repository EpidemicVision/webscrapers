FROM python:3.10-slim-buster

WORKDIR /usr/src/

RUN apt-get update && apt-get -y install nano
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENV PYTHONPATH "/usr/src:${PYTHONPATH}"

COPY . .

CMD ["tail", "-f", "/dev/null"]
