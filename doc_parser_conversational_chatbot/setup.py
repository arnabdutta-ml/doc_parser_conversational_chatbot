import os
from setuptools import setup, find_packages

this_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ''

setup(
    name='doc_parser_conversational_chatbot',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'openai',
        'pymupdf',
        'faiss-cpu',
        'python-docx',
    ],
    entry_points={
        'console_scripts': [
            'doc-parser-chatbot=doc_parser_conversational_chatbot.chatbot:main',
        ],
    },
    author='Your Name',
    description='A CLI chatbot to query PDF and DOCX files using OpenAI and FAISS',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
