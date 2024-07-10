import os
from dotenv import load_dotenv
import openai
import requests
import json

import time
import logging
from datetime import datetime
import streamlit as st
from helpers.message_processing import mask_pii, unmask_pii
from helpers.upload_doc import upload_documents
from helpers.human_agent_handling import switch_to_human_agent

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
# Create an OpenAI API client
client = openai.OpenAI()
model = "gpt-4-1106-preview"  # "gpt-3.5-turbo-16k"

# Upload documents
# file_ids = upload_documents()

# Create an assistant
# assistant = client.beta.assistants.create(
#     name="ClientConnect Assistant",
#     model=model,
#     instructions = "Provide information and assistance to clients about BearingPoint services and offerings. Answer questions accurately and comprehensively. If the required information is not available or the question is beyond your scope, respond with #NO_RESPONSE#. Sign your name as "BearingPoint Assistant" for every reply.",
#     tools = [{"type":"file_search"}],
# )
# print(assistant.id)
# Hardcoded assistant ID
assis_id = "asst_l8IPV2IlX8J2gJyY3WXKjkoo"

# Initialize Streamlit session state variables
def initialize_session():
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "start_chat" not in st.session_state:
        st.session_state.start_chat = False
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Start chat
def start_chat():
    st.session_state.start_chat = True
    chat_thread = client.beta.threads.create()
    st.session_state.thread_id = chat_thread.id
    print(chat_thread.id)
    st.write("Thread ID:", chat_thread.id)

# Handle user message
def handle_user_message(prompt):
    st.session_state.messages.append(
        {"role":"user",
         "content":prompt}
    )
    with st.chat_message("user"):
        st.markdown(prompt)
    print(prompt)

    masked_prompt = mask_pii(prompt)

    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id, role="user", content=masked_prompt
    )

    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assis_id,
        instructions="""Please answer the questions using the knowledge provided in the files.
        When adding additional information, make sure to distinguish it with bold or underlined text.""",
    )

    with st.spinner("Wait... Generating response..."):
        while run.status != "completed":
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id, run_id=run.id
            )
            print(run.status)
        
        if run.status == "failed":
            switch_to_human_agent(st.session_state.thread_id, client)
            st.session_state.messages.append({"role": "assistant", "content": "I'm not sure about that. Redirecting you to a human agent..."})
            with st.chat_message("assistant"):
                st.markdown("I'm not sure about that. Redirecting you to a human agent...")
        else:
            messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
            assistant_messages_for_run = [
                message
                for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]

            for message in assistant_messages_for_run:
                if message.content == "#NO_RESPONSE#":
                    switch_to_human_agent(st.session_state.thread_id, client)
                    st.session_state.messages.append({"role": "assistant", "content": "I'm not sure about that. Redirecting you to a human agent..."})
                    with st.chat_message("assistant"):
                        st.markdown("I'm not sure about that. Redirecting you to a human agent...")
                    return
                print(message.content)
                unmasked_response = unmask_pii(message.content)
                st.session_state.messages.append(
                    {"role": "assistant", "content": unmasked_response}
                )
                with st.chat_message("assistant"):
                    st.markdown(unmasked_response, unsafe_allow_html=True)



# Initialize session state variables
initialize_session()

# Streamlit page configuration
st.set_page_config(page_title="BearingPoint ClientConnect", page_icon=":books:")

st.title("BearingPoint ClientConnect")
st.write("Chat with BearingPoint to get assistance with your inquiries.")

# Chatbot UI
if st.session_state.start_chat:
    # Display existing messages
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # Handle new user input
    if prompt := st.chat_input("Type your message here"):
        handle_user_message(prompt)
else:
    st.write("Click the button below to start chatting with BearingPoint.")
    if st.button("Start Chatting"):
        start_chat()