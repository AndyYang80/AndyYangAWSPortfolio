import os
import boto3
import json
from botocore.exceptions import ClientError
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from markdown import markdown

def response(user_query):

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    client = boto3.client(service_name = 'lambda', region_name="us-east-2")

    # Set the model ID, e.g., Llama 3 70b Instruct.
    model_id = "us.meta.llama3-2-1b-instruct-v1:0"

    docsearch = FAISS.load_local("vectorstore", OpenAIEmbeddings(), allow_dangerous_deserialization = True)
    retriever = docsearch.as_retriever(search_type="similarity")

    context = format_docs(retriever.invoke(user_query))

    try:
        # Invoke the model with the request.
        payload_dict = {"query" : user_query, "context" : context}

        payload = json.dumps(payload_dict)
        out = client.invoke(
                FunctionName="llamaInferenceSyang",
                InvocationType='RequestResponse',
                Payload = payload
            )

    except (ClientError, Exception) as e:
        raise Exception(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")

    # Decode the response body.
    model_response = json.loads(out["Payload"].read())
    model_response = model_response.strip("\n")

    return markdown(model_response)