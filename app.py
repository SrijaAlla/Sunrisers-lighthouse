import os
import time
from dotenv import load_dotenv
from tqdm.autonotebook import tqdm
from pinecone_functions import Pinecone, ServerlessSpec
from openai import OpenAI
# from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
# from langchain.memory import ConversationBufferMemory
from flask import Flask, request, jsonify
from flask_cors import CORS
# from langchain_community.document_loaders.word_document import Docx2txtLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone_functions import check_and_load_docx_from_dir, calculate_and_display_embedding_cost, load_or_create_embeddings_index
app = Flask(__name__)
CORS(app)  
load_dotenv(dotenv_path="./.env")

# Acessing the various API KEYS
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENV = os.environ.get("PINECONE_ENV")

pc = Pinecone(api_key=PINECONE_API_KEY) 
index_name = "health-care-plans"
existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

index = pc.Index(index_name)

chunks = check_and_load_docx_from_dir('./medicaid_docs')
calculate_and_display_embedding_cost(chunks)
namespace = 'insurance-plans'
vectorstore = load_or_create_embeddings_index(index_name=index_name, chunks=chunks, namespace=namespace)


# vectorstore = PineconeVectorStore.from_texts(chunks, embedding=embeddings, index_name=index_name, pool_threads=8 )
query = "Tell me about BlueCross PPO plan"
results = vectorstore.similarity_search(query, k=3)
print(results)

def create_qa_with_memory(api_key, vectorstore, query):
    client = OpenAI(api_key=api_key)

    results = vectorstore.similarity_search(query, k=3)

    similar_docs = []
    for result in results: 
        similar_docs.append(result.page_content)
    
    context = ' '.join(similar_docs)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        # System message setting the role of the bot as a healthcare advisor
            {"role": "system", 
             "content": (
            "You are a healthcare insurance advisor that helps patients understand "
            "their insurance needs, identify relevant healthcare insurance carriers, "
            "and determine if a carrier is the right fit and affordable for the patient.You are wokring for Lighhouse medical free clinic "
            "Here is all the information you need: {context}. "
            "Use this information to answer questions and provide clear, personalized "
            "guidance to help patients make informed decisions."
            "Give a response in 100 to 150 words. Try to keep the answer short"
            "If the user asks any questions other than health insurance related or health related, say you only answer questions realted to health insurance and lighthouse"
            )},
        # User query input
            {"role": "user", "content": query},
        ]
    )

    
    return response.choices[0].message.content.replace("**", "\n")

# Store chat history in session or local variable
chat_history = []

@app.route("/api/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question")
    if user_input:
        response = create_qa_with_memory(OPENAI_API_KEY, vectorstore, user_input)

        # Append to chat history
        chat_history.append({"user": user_input, "bot": response})

        # Return the response to the frontend
        return jsonify({"response": response, "chat_history": chat_history})
    return jsonify({"response": "Sorry, I didn't understand that."}), 400

if __name__ == "__main__":
    app.run(debug=True)