FROM python:3.9-slim

RUN python -m pip install rasa==3.6.9

WORKDIR /app
COPY . .

RUN rasa train nlu

USER 1001

ENTRYPOINT [ "rasa" ]

CMD [ "run", "--enable-api", "--port", "8080" ]
