import streamlit as st
#import datetime

st.set_page_config(layout="wide")

# Chat Widget Layout
st.sidebar.header("Chat Widget")

# Input for user messages and output area for chat history
message_input = st.text_area("Enter your message: ", height=50)
chat_history = ""

# Button to submit the input and display the chat history
if st.button('Send'):
    new_line = "\n" + "*" * 40 + "\n"
    # Add user's message with timestamp to chat history
    current_time = st.session_state['current_time'] if 'current_time' in st.session_state else datetime.now()
    chat_history += f"[{current_time}] {message_input}\n{new_line}"

    # Display the updated chat history
    st.write(chat_history)