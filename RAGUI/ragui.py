import streamlit as st
import requests
import json
import os
import threading
import time
import numpy as np
import mimetypes
import faiss
from typing import List, Tuple

# Assuming you have already installed faiss-cpu: pip install faiss-cpu

def query_ollama_stream(server_url, prompt, model, stop_event):
    url = f"{server_url}/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    with requests.post(url, json=data, stream=True) as response:
        for line in response.iter_lines():
            if stop_event.is_set():
                break
            if line:
                yield json.loads(line)

def get_available_models(server_url):
    try:
        response = requests.get(f"{server_url}/api/tags")
        if response.status_code == 200:
            models = response.json()
            return [model['name'] for model in models['models']]
        else:
            st.error(f"Failed to fetch models. Status code: {response.status_code}")
            return []
    except requests.RequestException as e:
        st.error(f"Error connecting to server: {e}")
        return []

def read_file_content(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith('text'):
        with open(file_path, 'r', errors='replace') as file:
            return file.read()
    else:
        with open(file_path, 'rb') as file:
            return file.read()

def embed_file(server_url, file_path, embed_model):
    content = read_file_content(file_path)
    
    url = f"{server_url}/api/embeddings"
    data = {
        "model": embed_model,
        "prompt": content if isinstance(content, str) else content.decode('utf-8', errors='replace')
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            embedding = response.json()['embedding']
            return np.array(embedding, dtype=np.float32)
        else:
            st.error(f"Failed to generate embedding. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        st.error(f"Error connecting to server: {e}")
        return None

def initialize_faiss_index(dimension: int) -> faiss.IndexFlatL2:
    return faiss.IndexFlatL2(dimension)

def add_to_faiss_index(index: faiss.IndexFlatL2, embedding: np.ndarray, file_path: str):
    if "faiss_file_paths" not in st.session_state:
        st.session_state.faiss_file_paths = []
    st.session_state.faiss_file_paths.append(file_path)
    index.add(embedding.reshape(1, -1))

def search_faiss_index(index: faiss.IndexFlatL2, query_embedding: np.ndarray, k: int) -> List[Tuple[int, float]]:
    distances, indices = index.search(query_embedding.reshape(1, -1), k)
    return list(zip(indices[0], distances[0]))

def get_context_from_faiss(index: faiss.IndexFlatL2, query_embedding: np.ndarray, k: int) -> str:
    results = search_faiss_index(index, query_embedding, k)
    context = ""
    for idx, distance in results:
        file_path = st.session_state.faiss_file_paths[idx]
        content = read_file_content(file_path)
        context += f"Content from {os.path.basename(file_path)}:\n{content}\n\n"
    return context

def main():
    st.image("skale.png", width=60)
    st.title("Chat with Models and Documents")
    st.caption("by skale.dev")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "faiss_index" not in st.session_state:
        st.session_state.faiss_index = None

    server_options = {
        "Local": "http://localhost:11434",
        "amp1": "http://amp1.mooo.com:11434"
    }
    selected_server = st.selectbox("Select Ollama Server", list(server_options.keys()))
    server_url = server_options[selected_server]

    available_models = get_available_models(server_url)
    if available_models:
        selected_model = st.selectbox("Select LLM Model", available_models)
    else:
        st.warning("No models available or couldn't connect to the server.")
        return

    embed_models = [model for model in available_models if "nomic-embed-text" in model]
    embed_model = embed_models[0] if embed_models else None

    uploaded_file = st.file_uploader("Upload a PDF or TXT file for RAG", type=["pdf", "txt"])
    if uploaded_file is not None:
        save_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File {uploaded_file.name} saved for RAG.")

        if st.button("Embed File"):
            if embed_model:
                with st.spinner(f"Embedding file using {embed_model}..."):
                    embedding = embed_file(server_url, save_path, embed_model)
                    if embedding is not None:
                        if st.session_state.faiss_index is None:
                            st.session_state.faiss_index = initialize_faiss_index(embedding.shape[0])
                        add_to_faiss_index(st.session_state.faiss_index, embedding, save_path)
                        st.success("File embedded and added to FAISS index successfully!")
            else:
                st.error("No suitable embedding model (containing 'nomic-embed-text') is available on this server.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter your message:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            stop_button_placeholder = st.empty()
            full_response = ""
            
            stop_event = threading.Event()
            stop_clicked = False

            # Get context from FAISS if available
            context = ""
            if st.session_state.faiss_index is not None and embed_model:
                query_embedding = embed_file(server_url, "query.txt", embed_model)
                if query_embedding is not None:
                    context = get_context_from_faiss(st.session_state.faiss_index, query_embedding, k=1)

            # Prepare prompt with context
            full_prompt = f"Context:\n{context}\n\nUser Query: {prompt}\n\nAssistant:"

            with st.spinner("Generating response..."):
                for i, chunk in enumerate(query_ollama_stream(server_url, full_prompt, selected_model, stop_event)):
                    if stop_clicked:
                        stop_event.set()
                        break
                    chunk_text = chunk.get('response', '')
                    full_response += chunk_text
                    response_placeholder.markdown(full_response)
                    
                    stop_clicked = stop_button_placeholder.button("Stop Generation", key=f"stop_{i}")
                    
                    time.sleep(0.1)
            
            stop_button_placeholder.empty()
            if stop_event.is_set():
                full_response += "\n\n[Generation stopped by user]"
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()