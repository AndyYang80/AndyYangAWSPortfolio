import os
import bs4
import getpass
import boto3
import json
from botocore.exceptions import ClientError
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain import hub
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from markdown import markdown


def response(user_query):

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    client = boto3.client("bedrock-runtime", region_name="us-east-2")

    # Set the model ID, e.g., Llama 3 70b Instruct.
    model_id = "us.meta.llama3-2-1b-instruct-v1:0"

    docsearch = FAISS.load_local("vectorstore", OpenAIEmbeddings(), allow_dangerous_deserialization = True)
    retriever = docsearch.as_retriever(search_type="similarity")

    context = format_docs(retriever.invoke(user_query))

    # Embed the prompt in Llama 3's instruction format.
    formatted_prompt = f"""
    <|begin_of_text|><|start_header_id|>user<|end_header_id|>
    You are Andy Yang, a experienced data scientist. Answer the question while conidering the following context: {context}
    {user_query}
    Do not give answer with false information and keep your answer within 1 paragraph.
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """

    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": 256,
        "temperature": 0.5,
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["generation"]

    return markdown(response_text)