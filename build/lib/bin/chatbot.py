import os
import fitz
import faiss
import numpy as np
from openai import OpenAI
import docx

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_paths):
    """
    Extract all text from a list of PDFs.
    """
    text = ""
    for pdf_path in pdf_paths:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    return text

def extract_text_from_docx(docx_path):
    """
    Extract all text from a .docx file.
    """
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_folder(folder_path):
    """
    Find all .pdf and .docx files in folder and extract their text.
    Concatenate all extracted text.
    """
    files = os.listdir(folder_path)
    pdf_files = [os.path.join(folder_path, f) for f in files if f.lower().endswith('.pdf')]
    docx_files = [os.path.join(folder_path, f) for f in files if f.lower().endswith('.docx')]

    pdf_text = extract_text_from_pdf(pdf_files) if pdf_files else ""
    docx_text = ""
    for docx_path in docx_files:
        docx_text += extract_text_from_docx(docx_path)

    return pdf_text + docx_text

def chunk_text(text, chunk_size=500):
    """
    Split text into overlapping chunks for embedding.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def get_embedding(text):
    """
    Get embedding from OpenAI.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding, dtype='float32')

def build_faiss_index(chunks):
    """
    Create FAISS index from text chunks.
    """
    embeddings = [get_embedding(chunk) for chunk in chunks]
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index, embeddings

def find_top_k_chunks(question, chunks, embeddings, index, k=3):
    """
    Retrieve top-k most similar chunks to question.
    """
    q_emb = get_embedding(question).reshape(1, -1)
    distances, indices = index.search(q_emb, k)
    return [chunks[i] for i in indices[0]]

def ask_gpt(question, context_chunks):
    """
    Ask GPT with document context.
    """
    system_instructions = (
        "You are a helpful assistant that answers questions about the provided document. "
        "Use the context to answer accurately and concisely."
    )
    context = "\n\n".join(context_chunks)
    user_content = f"Context:\n{context}\n\nQuestion: {question}"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_content}
        ]
    )
    return response.choices[0].message.content.strip()

def ask_general_gpt(question):
    """
    Ask GPT without any document context.
    """
    system_instructions = (
        "You are a helpful assistant. Answer the user's questions as best as you can."
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content.strip()

def main():
    print("=== Doc Parser Conversational Chatbot with Embeddings + FAISS ===")
    folder_path = input("Enter path to folder with documents (.pdf and .docx): ").strip()
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print("[ERROR] Folder not found or is not a directory.")
        return

    # Extract text from all documents in folder
    text = extract_text_from_folder(folder_path)
    if not text:
        print("[ERROR] No text extracted from documents in folder.")
        return
    print("[INFO] Extracted text from documents in folder.")

    # Chunk text
    chunks = chunk_text(text)
    print(f"[INFO] Split text into {len(chunks)} chunks.")

    # Build FAISS index
    print("[INFO] Creating embeddings and building FAISS index...")
    index, embeddings = build_faiss_index(chunks)
    print("[INFO] FAISS index ready!")

    # Chat loop
    while True:
        user_input = input("\nYour input (prefix with 'doc:' or 'chat:', or 'exit'): ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        if user_input.lower().startswith("doc:"):
            question = user_input[4:].strip()
            if not question:
                print("[ERROR] Please enter a question after 'doc:'.")
                continue
            top_chunks = find_top_k_chunks(question, chunks, embeddings, index, k=3)
            answer = ask_gpt(question, top_chunks)
            print("\nAssistant:", answer)
        elif user_input.lower().startswith("chat:"):
            question = user_input[5:].strip()
            if not question:
                print("[ERROR] Please enter a question after 'chat:'.")
                continue
            answer = ask_general_gpt(question)
            print("\nAssistant:", answer)
        else:
            print("[INFO] Please prefix your input with 'doc:' for document questions or 'chat:' for general chat.")

if __name__ == "__main__":
    main()