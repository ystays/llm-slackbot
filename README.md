# saatva-slackbot

To run chatbot, execute the following commands in separate terminals:

```
ngrok http 3000
```

```
python3 server.py
```

Then, copy the forwarding link from ngrok and append `/slack/events` to it. Paste the resulting link to the Request URL box on the Event Subscriptions page of the Slack App at api.slack.com. Once the Request URL is verified, the slackbot will be online.