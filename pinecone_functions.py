from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time
import os
from dotenv import load_dotenv
import docx2txt


load_dotenv(dotenv_path="./.env")

# Acessing the various API KEYS
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENV = os.environ.get("PINECONE_ENV")
pc = Pinecone(
    api_key=os.environ.get("PINECONE_API_KEY") or 'PINECONE_API_KEY'
)

def check_and_load_docx_from_dir(directory):
    # Ensure the directory path exists
    if not os.path.exists(directory):
        print("Directory does not exist.")
        return False

    # Check if directory is actually a directory
    if not os.path.isdir(directory):
        print("The specified path is not a directory.")
        return False

    # List all files in the directory
    all_files = os.listdir(directory)
    print(f'Heres the list of all .docx files within the {directory} directory: {all_files}')
    
    # Check if each file ends with .docx
    for file in all_files:
        if not file.endswith(".docx"):
            print(f"Non-DOCX file found: {file}")
            return False
    
    # load directory path
    directory_path = directory 
    # add list comprehension for file os.path.join usage
    docx_files = [f for f in all_files if f.endswith(".docx")]
    # Create emptly list container
    documents = []
    # Loop through the directory, bundle and load docx files. 
    for docx_file in docx_files:
        file_path = os.path.join(directory_path, docx_file)
        loader = Docx2txtLoader(file_path)
        documents.extend(loader.load())

    # Split text
    text_splitter = RecursiveCharacterTextSplitter( 
        chunk_size=1000,  # Maximum size of each chunk
        chunk_overlap=100,  # Number of overlapping characters between chunks
        )
    
    # Create empty list to hold chunks
    chunks = []

    # Split and add to the list
    for document in documents:
        chunks.extend(text_splitter.split_documents([document]))  
        
    return chunks

def calculate_and_display_embedding_cost(texts):
    import tiktoken
    enccoding = tiktoken.encoding_for_model("gpt-4o-mini")
    total_tokens = sum([len(enccoding.encode(page.page_content)) for page in texts])
    print(f'Token Amount: {total_tokens}')
    print(f'Embedding Cost in USD:{total_tokens / 1000 * 0.0004:.6f}')

def load_or_create_embeddings_index(index_name, chunks, namespace):
    
    if index_name in pc.list_indexes().names():
        print(f'Index {index_name} already exists. Loading embeddings...', end='')
        vector_store = PineconeVectorStore.from_documents(
        documents=chunks, embedding=OpenAIEmbeddings(model='text-embedding-3-small'), index_name=index_name, namespace=namespace)
        
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
        
        print('Done')
    else:
        print(f'Creating index {index_name} and embeddings ...', end = '')
        pc.create_index(name=index_name, dimension=1536, metric='cosine',  spec=ServerlessSpec(
                cloud='aws',
                region='us-west-2'
            ))
        
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
        # Add to vectorDB using LangChain 
        vector_store = PineconeVectorStore.from_documents(
        documents=chunks, embedding=OpenAIEmbeddings(), index_name=index_name, namespace=namespace)
        print('Done')   
    return vector_store