import streamlit as st
import requests
import json
import os
import threading
import time

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

def main():
    st.image("skale.png", width=60,)  # Replace with the path to your logo file
    st.title("Chat with Models")
#    st.subheader("by skale.dev", anchor="https://skale.dev")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Server selection
    server_options = {
        "Local": "http://localhost:11434",
        "amp1": "http://amp1.mooo.com:11434"
    }
    selected_server = st.selectbox("Select Ollama Server", list(server_options.keys()))
    server_url = server_options[selected_server]

    # Fetch and display available models
    available_models = get_available_models(server_url)
    if available_models:
        selected_model = st.selectbox("Select LLM Model", available_models)
    else:
        st.warning("No models available or couldn't connect to the server.")
        return

    # File upload
    uploaded_file = st.file_uploader("Upload a PDF or TXT file for future RAG use", type=["pdf", "txt"])
    if uploaded_file is not None:
        save_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File {uploaded_file.name} saved for future use in RAG.")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
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

            with st.spinner("Generating response..."):
                for i, chunk in enumerate(query_ollama_stream(server_url, prompt, selected_model, stop_event)):
                    if stop_clicked:
                        stop_event.set()
                        break
                    chunk_text = chunk.get('response', '')
                    full_response += chunk_text
                    response_placeholder.markdown(full_response)
                    
                    # Update stop button with a unique key
                    stop_clicked = stop_button_placeholder.button("Stop Generation", key=f"stop_{i}")
                    
                    # Add a small delay to prevent too frequent updates
                    time.sleep(0.1)
            
            stop_button_placeholder.empty()
            if stop_event.is_set():
                full_response += "\n\n[Generation stopped by user]"
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
