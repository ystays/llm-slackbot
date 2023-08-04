from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import os
from dotenv import load_dotenv

from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback

from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain, LLMChain
import pinecone
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.question_answering import load_qa_chain

def query_similarity_search_QA_w_sources_OpenAI_Model(question, chat_history=[]):
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    embeddings = OpenAIEmbeddings()
    docsearch = Pinecone.from_existing_index(os.environ['PINECONE_INDEX_NAME'], embeddings)

    _template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""

    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

    template = """Use the following pieces of context to answer the question at the end. You are a friendly and reliable chatbot on the saatva.com website for Saatva. Saatva is a premier online retailer of luxury mattresses in the country. You have access to details of the products sold by Saatva, which include mattresses, bedding, furniture and bundles. Use that data to accurately answer questions about all Saatva products. In particular, ensure that questions about pricing are answered precisely with the amount of savings and the final price always stated clearly. If more than one price is available for the requested product, use the lower, discounted price of that product and state the amount of savings. Use as few sentences as possible to answer questions unless further details are asked for, and keep the answer as concise as possible. If you don't know the answer, just say you don't know the answer, don't try to make up an answer. 

    {context}
    
    Question: {question}
    Helpful Answer: """
    QA_PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])
    
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    streaming_llm = OpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0)

    question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT)
    doc_chain = load_qa_chain(streaming_llm, chain_type="stuff", prompt=QA_PROMPT)

    chat = ConversationalRetrievalChain(
        retriever=docsearch.as_retriever(),
        combine_docs_chain=doc_chain,
        question_generator=question_generator)
    
    with get_openai_callback() as cb:
        res = chat({"question": question, "chat_history": chat_history})
        chat_history_new = (question, res["answer"])
        result = res["answer"]
        print(cb)
    if len(chat_history) > 100:
        print("Warning: Chat history length is sizable.")
    return result, chat_history_new


if __name__ == "__main__":
    load_dotenv()
    # initialize pinecone
    pinecone.init(
        api_key=os.environ['PINECONE_API_KEY'],  # find at app.pinecone.io
        environment=os.environ['PINECONE_ENV']  # next to api key in console
    )