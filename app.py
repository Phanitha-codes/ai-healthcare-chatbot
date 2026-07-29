import streamlit as st
from chatbot import get_bot_response

st.set_page_config(page_title="AI Healthcare Chatbot", page_icon="🩺")

st.title("🩺 AI Healthcare Chatbot")
st.caption(
    "I can help with health, symptoms, and wellness questions. "
    "I'm not a licensed doctor — always consult a professional for diagnosis or treatment."
)

# Initialize chat history in session state (persists across reruns
# within the same browser session)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input box
user_input = st.chat_input("Ask a health-related question...")

if user_input:
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get bot reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = get_bot_response(user_input, st.session_state.messages[:-1])
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
