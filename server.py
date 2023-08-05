
import os
from slack_sdk import WebClient
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request, render_template

import pinecone
from query_llm import query_similarity_search_QA_w_sources_OpenAI_Model

from slack_sdk.errors import SlackApiError

load_dotenv()
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
response = slack_client.auth_test()
print(response["user_id"])

pinecone.init(
    api_key=str(os.environ['PINECONE_API_KEY']),  
    environment=str(os.environ['PINECONE_ENV'])  
)

app = App(token=os.environ["SLACK_BOT_TOKEN"])
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# Decorator for handling direct bot message events
@app.event("message")
def handle_direct_message(event, say):
    if event.get("subtype") is None and event.get("channel_type") == "im":
        user_input = event["text"]
        user_id = event["user"]
        
        try:
            result = slack_client.conversations_history(channel=event["channel"], limit=16)
            chat_history = result["messages"]
            #print(chat_history)
        except SlackApiError as e:
            print("Error creating conversation: {}".format(e))

        n = len(chat_history)
        i = 1
        formattedChatHistory = []
        questionAndAnswer = {}
        while i < n:
            msg = chat_history[i]
            if "type" in msg and msg["type"] == "message" and "text" in msg:
                if "bot_id" in msg:
                    # case 1: there is an existing answer
                    if "answer" in questionAndAnswer:
                        formattedChatHistory.append(("", questionAndAnswer["answer"]))
                        questionAndAnswer = {"answer": msg["text"]}
                    # case 2: there is an existing question
                    elif "question" in questionAndAnswer: 
                        formattedChatHistory.append((questionAndAnswer["question"], msg["text"]))
                        questionAndAnswer = {}
                    else: # case 3: no existing question or answer
                        questionAndAnswer = {"answer": msg["text"]}
                elif "client_msg_id" in msg:
                    # case 1: there is an existing answer
                    if "answer" in questionAndAnswer:
                        formattedChatHistory.append((msg["text"], questionAndAnswer["answer"]))
                        questionAndAnswer = {}
                    # case 2: there is an existing question
                    elif "question" in questionAndAnswer: 
                        formattedChatHistory.append((questionAndAnswer["question"], ""))
                        questionAndAnswer = {"question": msg["text"]}
                    else: # case 3: no existing question or answer
                        questionAndAnswer = {"question": msg["text"]}
                        

            i+=1
        formattedChatHistory.reverse()
        print(formattedChatHistory)
        result, chat_history_new = query_similarity_search_QA_w_sources_OpenAI_Model(user_input, formattedChatHistory)
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
    #chat_histories={}
    flask_app.run(port=3000)
    print("flask app running")