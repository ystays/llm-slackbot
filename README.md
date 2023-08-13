# saatva-slackbot

## Project Description
Slack chatbot that scrapes product data from saatva.com and answers questions using GPT API calls. Written in Python, uses BeautifulSoup, Flask, langchain and pinecone.

## Install and Run

Steps:
1. Scrape and parse HTML from saatva.com. To do so, run scraper.py. Ensure that all 3 functions `save_all_urls(), check_for_url_duplicates(), access_html_and_parse()` are set to run. This creates a csv file, links_pdp.csv, that contains all unique links to PDPs on saatva.com. A directory ,/output is also created to save the text (converted from HTML) found on each PDP. Data from each PDP is placed in its own file with a file name based on its URL.
2. Create vector embeddings and upload to pinecone.io. To do so, run upload_pinecone.py. This uses the text data from the ../output directory. The query function from query_llm.py is called here.
3. To run chatbot, execute the following commands in separate terminals:

```
ngrok http 3000
```

```
python3 server.py
```

Then, copy the forwarding link from ngrok and append `/slack/events` to it. Paste the resulting link to the Request URL box on the Event Subscriptions page of the Slack App at api.slack.com. Once the Request URL is verified, the slackbot will be online.


## Usage
Send direct messages to the bot in the created Slack workspace and receive responses based on the scraped data.
