import os
import time
from dotenv import load_dotenv
from tqdm.autonotebook import tqdm
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  
load_dotenv(dotenv_path="./.env")

# Acessing the various API KEYS
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENV = os.environ.get("PINECONE_ENV")

pc = Pinecone(api_key=PINECONE_API_KEY) 
index_name = "elective-genie"
embeddings = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model="text-embedding-3-small"
)
index = pc.Index(index_name)
f = open("./documents.txt",'r', encoding='utf-8')
content = f.read()
content = content.replace('\n','')
chunks = content.split("$$")
# print(chunks)


vectorstore = PineconeVectorStore.from_texts(chunks, embedding=embeddings, index_name=index_name, pool_threads=8 )
query = "What is taught in Advanced Block chain Technology?"
results = vectorstore.similarity_search(query, k=3)
print(results)
client = OpenAI(api_key=OPENAI_API_KEY)
# Initialize the LLM and QA object with memory support
def create_qa_with_memory(api_key, vectorstore):
    # Memory to store the conversation history
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-4o-mini",  # You can customize the model if needed
        temperature=0
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        memory=memory  # Include memory for context
    )
    
    return qa
qa = create_qa_with_memory(OPENAI_API_KEY, vectorstore)

# Store chat history in session or local variable
chat_history = []

@app.route("/api/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question")
    if user_input:
        # Get the response from the QA system
        response = qa.invoke(user_input)
        answer = response["result"]

        # Append to chat history
        chat_history.append({"user": user_input, "bot": answer})

        # Return the response to the frontend
        return jsonify({"response": answer, "chat_history": chat_history})
    return jsonify({"response": "Sorry, I didn't understand that."}), 400

if __name__ == "__main__":
    app.run(debug=True)