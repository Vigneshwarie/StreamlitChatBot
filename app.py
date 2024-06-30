import json
import openai
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
from sentence_transformers import SentenceTransformer
import os
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="College Counselor Chatbot",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="auto",
)


# Load environment variables
load_dotenv()
CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
DB_NAME = os.getenv("MONGODB_DB_NAME")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize SentenceTransformer model
model = SentenceTransformer('all-mpnet-base-v2')

# Connect to MongoDB
uri = CONNECTION_STRING
db_name = DB_NAME
collection_name = COLLECTION_NAME

client = MongoClient(uri, server_api=ServerApi('1'))

# Ping to confirm a successful connection
try:
    client.admin.command('ping')
 #   st.write("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    st.write(e)


def query_document(query_text):
    vector_query = model.encode(query_text).tolist()

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index_new",
                "path": "embedding",
                "queryVector": vector_query,
                "numCandidates": 100,
                "limit": 20
            }
        },
        {
            "$project": {
                "embedding": 0,
                "_id": 0,
                "score": {
                    "$meta": "searchScore"
                },
            }
        }
    ]

    results = list(client[db_name][collection_name].aggregate(pipeline))
    context = json.dumps(results)

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a useful assistant. Use the assistant's content to answer the user's query. If no content found use the openai \
        Summarize your answer using the 'texts' and cite the 'page_number' and 'filename' metadata in your reply."},
            {"role": "assistant", "content": context},
            {"role": "user", "content": query_text}
        ]
    )

    answer = response.choices[0].message.content
    return answer


# Custom CSS
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
    }
    .stTextInput > div > input {
        background-color: #ffffff;
        color: #000000;
        border-radius: 4px;
        padding: 10px;
        font-size: 16px;
    }
    .stTextInput label {
        font-size: 20px;
        font-weight: bold;
    }
    .stMarkdown {
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    st.image('assets/college.png')
    st.markdown("## Chat with your college Counselor")

    user_query = st.text_input("Enter your Question")

    if st.button("Submit"):
        if user_query:
            with st.spinner("Processing..."):
                try:
                    answer = query_document(user_query)
                    st.markdown(f"### Answer:\n{answer}")
                except Exception as e:
                    st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
