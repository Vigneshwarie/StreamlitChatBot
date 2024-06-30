import streamlit as st
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
DB_NAME = os.getenv("MONGODB_DB_NAME")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")


def get_response(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content.strip()


def main():
    st.title("GPT-4o Chatbot")
    prompt = st.text_area("You: ")
    if st.button("Ask"):
        with st.spinner("Generating response..."):
            response = get_response(prompt)
            st.text_area("Bot: ", value=response, height=200,
                         max_chars=None, key=None)


if __name__ == "__main__":
    main()
