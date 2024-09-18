# Elective Genie - AI Chatbot

This project is an AI-powered chatbot designed to help students select electives at the University at Buffalo. It uses a Retrieval-Augmented Generation (RAG) approach with a Pinecone vector database and OpenAI GPT for generating responses.

## Getting Started

Follow the instructions below to set up and run both the backend (Flask) and frontend (React) for the chatbot.


#### Prerequisites
- Python 3.x installed.
- necessary Python packages installed from requirements.text.
```python
pip install requirements.txt
```
#### Setup

1. Clone the repository and navigate to the project directory.

2. Create a `.env` file in the root directory and add the following environment variables:
   ```bash
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENV=your_pinecone_environment
   ```
### Backend Setup
```python
python app.py
```
### Frontend Setup
```python
cd chatbot-frontend
npm install
npm start
```
### Scraper 
```python
cd data/
```
output is store in `documents.txt`
