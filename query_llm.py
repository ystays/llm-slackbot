# import schema for chat messages and ChatOpenAI in order to query chatmodels GPT-3.5-turbo or GPT-4

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import os
from dotenv import load_dotenv

from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback

from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA, ConversationalRetrievalChain, LLMChain
import pinecone
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.question_answering import load_qa_chain

def query_similarity_search_QA_w_sources_OpenAI_Model(question, chat_history=[]):
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    embeddings = OpenAIEmbeddings()
    docsearch = Pinecone.from_existing_index(os.environ['PINECONE_INDEX_NAME'], embeddings)

    #docs = docsearch.similarity_search(question)
    #qa_chain = RetrievalQA.from_chain_type(model, retriever=docsearch.as_retriever())
    #qa_chain({"query": question})

    _template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""

    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

    template = """Use the following pieces of context to answer the question at the end. You are a friendly and reliable chatbot on the saatva.com website for Saatva. Saatva is a premier online retailer of luxury mattresses in the country. You have access to details of the products sold by Saatva, which include mattresses, bedding, furniture and bundles. Use that data to accurately answer questions about all Saatva products. In particular, ensure that questions about pricing are answered precisely with the amount of savings and the final price always stated clearly. If more than one price is available, use the lower, discounted price and state the amount of savings. Use as few sentences as possible to answer questions unless further details are asked for, and keep the answer as concise as possible. If you don't know the answer, just say you don't know the answer, don't try to make up an answer. 

    {context}
    
    Question: {question}
    Helpful Answer: """
    QA_PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])
    
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    # qa_chain = RetrievalQA.from_chain_type(
    #     llm,
    #     retriever=docsearch.as_retriever(),
    #     memory=memory,
    #     chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    # )

    # #sources_chain = load_qa_with_sources_chain(model,chain_type="refine")
    
    # with get_openai_callback() as cb:
    #     res = qa_chain({"query": question})
    #     result = res["result"]
    #     #result = sources_chain.run(input_documents=docsearch.similarity_search(question), question=question)
    #     print(cb)
    #     res = qa_chain({"query": "Could you please state the price again?"})
    #     print(res["result"])
    #     print(qa_chain.combine_documents_chain.memory)
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
    
    # from langchain.transformers import GPT3Tokenizer, GPT3ChatLM

    # tokenizer = GPT3Tokenizer.from_pretrained("gpt3.5-turbo")
    # model = GPT3ChatLM.from_pretrained("gpt3.5-turbo")

    # for document in documents:
    #     content = document.page_content
    
    # response = model.generate(
    #     content,
    #     max_length=50,
    #     num_return_sequences=1,
    #     temperature=0.7
    # )
    
    # print(response.choices[0].text)


# chat = ChatOpenAI(model_name="gpt-3.5-turbo",temperature=0.3)
# messages = [
#     SystemMessage(content="You are an expert data scientist"),
#     HumanMessage(content="Write a Python script that trains a neural network on simulated data ")
# ]
# response=chat(messages)

# print(response.content,end='\n')


# Import prompt and define PromptTemplate

# from langchain import PromptTemplate

# template = """
# You are an expert data scientist with an expertise in building deep learning models. 
# Explain the concept of {concept} in a couple of lines
# """

# prompt = PromptTemplate(
#     input_variables=["concept"],
#     template=template,
# )

# Import LLMChain and define chain with language model and prompt as arguments.

# from langchain.chains import LLMChain
# chain = LLMChain(llm=llm, prompt=prompt)

# # Run the chain only specifying the input variable.
# print(chain.run("autoencoder"))




# Define a second prompt 

# second_prompt = PromptTemplate(
#     input_variables=["ml_concept"],
#     template="Turn the concept description of {ml_concept} and explain it to me like I'm five in 500 words",
# )
# chain_two = LLMChain(llm=llm, prompt=second_prompt)

# # Define a sequential chain using the two chains above: the second chain takes the output of the first chain as input

# from langchain.chains import SimpleSequentialChain
# overall_chain = SimpleSequentialChain(chains=[chain, chain_two], verbose=True)

# # Run the chain specifying only the input variable for the first chain.
# explanation = overall_chain.run("autoencoder")
# print(explanation)
