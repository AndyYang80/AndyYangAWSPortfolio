import boto3
import json
import os
import argparse
from botocore.exceptions import ClientError
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader

def create_vectorstore(filename):

    openai_api_key = os.getenv("OPENAI_API_KEY")

    loader = PyPDFLoader(filename)
    pages = []
    for page in loader.load():
        pages.append(page)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(pages)
    vectorstore = FAISS.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    vectorstore.save_local("vectorstore")

if __name__ == "main":
    parser = argparse.ArgumentParser(description="Generate a vector store from documents")
    parser.add_argument("arg1", type=str, help="File Name")
    args = parser.parse_args()
    create_vectorstore(args.arg1)
