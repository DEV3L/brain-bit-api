FROM python:3.6

ENV IS_DOCKER=true
ENV HOST=0.0.0.0

ADD . /src
WORKDIR /src
EXPOSE 5000

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "run.py"]
