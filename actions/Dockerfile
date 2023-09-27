FROM rasa/rasa:latest

USER root

COPY . /app

WORKDIR /app
RUN pip install python-dotenv rasa-sdk requests
EXPOSE 5055

CMD ["run", "actions", "--debug"]