
import os
from slack_sdk import WebClient
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request, render_template

import pinecone
from query_llm import query_similarity_search_QA_w_sources_OpenAI_Model


load_dotenv()
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
response = slack_client.auth_test()
print(response["user_id"])


app = App(token=os.environ["SLACK_BOT_TOKEN"])
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# Decorator for handling direct bot message events
@app.event("message")
def handle_direct_message(event, say):
    if event.get("subtype") is None and event.get("channel_type") == "im":
        user_input = event["text"]
        user_id = event["user"]
        if user_id in chat_histories:
            result, chat_history_new = query_similarity_search_QA_w_sources_OpenAI_Model(user_input, chat_histories[user_id])
            chat_histories[user_id].append(chat_history_new)
        else:
            result, chat_history_new = query_similarity_search_QA_w_sources_OpenAI_Model(user_input)
            chat_histories[user_id] = [chat_history_new]
        say(result)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """
    Route for handling Slack events.
    This function passes the incoming HTTP request to the SlackRequestHandler for processing.

    Returns:
        Response: The result of handling the request.
    """
    if "type" in request.json and request.json["type"] == "url_verification":
        return request.json["challenge"]
    return handler.handle(request)

@flask_app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

if __name__ == "__main__":
    # initialize pinecone
    pinecone.init(
        api_key=str(os.environ['PINECONE_API_KEY']),  
        environment=str(os.environ['PINECONE_ENV'])  
    )
    chat_histories = {}
    flask_app.run(port=3000)
    print("flask app running")


