```shell
rasa run actions
rasa interactive
```

- Use rasa interactive to test new flows
- manually run rasa train if not reflecting new changes sometimes
- use rasa shell to test convo

openai flow:
What can you help with?

activate form by triggering intent: "ask me anything" or variations in that intent

# Dependency for spaCy

```bash
pip3 install 'rasa[spacy]'
python3 -m spacy download en_core_web_md
```

## Unintall uvloop for bug in Rasa interactive

When chatting with bot to trigger external reminder and get Error: EXTERNAL_reminder error Future exception was never retrieved future: <Future finished exception=BlockingIOError(35, 'write could not complete without blocking', 0)>

```bash
pip uninstall uvloop
```

TODO:

1. edit external trigger to activate a reminder instead of custom action

- scheduled reminders queue

2. this reminder waits for 4 seconds, then activates custom action to print response

# send external trigger

1. get ID from bot chat
2. edit name of trigger (EXTERNAL\_<trigger_name> and entities involved for slots + actions)

```bash
curl -H "Content-Type: application/json" -X POST -d \
'{"name": "EXTERNAL_dry_plant", "entities": {"plant": "Orchid"}}' \
"http://localhost:5005/conversations/<CONVERSATION_ID_FROM_BOT>/trigger_intent?output_channel=latest"
```

**_callback server only used for recieving messages from CURL like when posting External Events_**

# Flow for triggering external reminder to call custom action

- make sure uvloop installed for callback server

```shell
python callback_server.py
rasa run actions
rasa run --enable-api
curl -XPOST http://localhost:5005/webhooks/callback/webhook \
   -d '{"sender": "tester", "message": "remind me to call Brands!"}' \
   -H "Content-type: application/json"
```

no chat through chat, but sending message to bot via webhook in curl request abd _message_ param in JSON payload

# Running Docker container locally

```bash
docker run -it -p 8080:8080 ogbrand25/rasa-demo
docker run -it ogbrand25/rasa-demo shell
```

* because declared this in Dockerfile, everytime image is called as in above command, the below commands are ran as though called manually: rasa run --enable-api --port 8080:

ENTRYPOINT [ "rasa" ]

CMD [ "run", "--enable-api", "--port", "8080" ]

## attach local volume and run remote docker container

- pwd attaches local dir as volume (filesystem) so can access locally trained model
- this pulls official docker container from rasa instead of fiddly self-defined Dockerfile that we pushed as rasa-demo to personal dockerhub

```bash
docker run -it -p 8080:8080 -v $(pwd):/app rasa/rasa:3.6.9-full run --enable-api --port 8080
```

# Deploying to GKE
1. spun up GKE autopilot cluster
2. git clone this repo into cloud shell
3. kubectl apply -f manifest.yaml (applies outer Dockerfile again with new configs)
4. kubectl rasa port-forward svc.rasa-web 8080:8080
5. get EXTNERAL-IP from LB svc and query http://34.101.211.39:8080/model/parse

NAME                                     READY   STATUS              RESTARTS   AGE
pod/rasa-custom-model-5c7b65664f-jft68   0/1     ContainerCreating   0          79s
pod/rasa-custom-model-5c7b65664f-p2qdl   0/1     ContainerCreating   0          79s

NAME                 TYPE           CLUSTER-IP       EXTERNAL-IP     PORT(S)          AGE
service/kubernetes   ClusterIP      34.118.224.1     <none>          443/TCP          114m
service/rasa-web     LoadBalancer   34.118.227.143   34.101.211.39   8080:32200/TCP   81s