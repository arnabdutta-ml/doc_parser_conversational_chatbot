# Doc Parser Conversational Chatbot

A command-line tool to chat with the contents of PDF and DOCX files in a folder, using OpenAI GPT models with FAISS-based retrieval.

## Features
- Reads all .pdf and .docx files in a given folder
- Uses OpenAI Embeddings and FAISS for semantic search
- Chat with context-aware or general GPT modes
- Supports both document-specific and general chat queries

## Installation

Clone this repo:
git clone https://github.com/arnabdutta-ml/doc_parser_conversational_chatbot.git

cd doc_parser_conversational_chatbot

Install requirements:
pip install -r requirements.txt

## Wheel based local install
pip install dist/doc_parser_conversational_chatbot-0.1.0-py3-none-any.whl
