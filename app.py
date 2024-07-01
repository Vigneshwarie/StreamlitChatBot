import os
import streamlit as st
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import openai
import json
from PyPDF2 import PdfReader

load_dotenv()
CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
DB_NAME = os.getenv("MONGODB_DB_NAME")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Setting up Streamlit page configuration
st.set_page_config(page_title='College Counselor Chatbot', layout='wide')
st.set_option('deprecation.showfileUploaderEncoding', False)
st.image('assets/college.png')
st.markdown("## Chat with your College Counselor")

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
    st.write("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    st.error(f"Error connecting to MongoDB: {e}")

# Main functionality
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    file_contents = uploaded_file.read()
    file_name = uploaded_file.name

    # Extract text from PDF
    reader = PdfReader(uploaded_file)
    txt = ""
    for page in reader.pages:
        txt += page.extract_text()

    records = [{'text': txt, 'filename': file_name}]

    for record in records:
        record['embedding'] = model.encode(record['text']).tolist()

    # st.write("Generated embeddings for records:", records)

    # Insert into MongoDB
    result = client[db_name][collection_name].insert_many(records)
    st.write(f"Uploaded document ID(s): {result.inserted_ids}")

    st.success('Document uploaded and processed successfully!')

# Query section
query_text = st.text_input('Enter your query:')
if st.button('Search'):
    if query_text:
        # Encode query text
        vector_query = model.encode(query_text).tolist()
        # st.write("Query vector:", vector_query)

        # Define the pipeline for aggregation
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

        # st.write("Aggregation pipeline:", pipeline)

        # Execute the aggregation pipeline
        try:
            results = list(
                client[db_name][collection_name].aggregate(pipeline))
            # st.write("Aggregation results:", results)
        except Exception as e:
            st.error(f"Error executing the aggregation pipeline: {e}")

        if results:
            context = json.dumps(results)

            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a useful assistant. Use the assistant's content to answer the user's query \
                    Summarize your answer using the 'texts' and cite the 'page_number' and 'filename' metadata in your reply."},
                    {"role": "assistant", "content": context},
                    {"role": "user", "content": query_text}
                ]
            )

            answer = response.choices[0].message.content

            st.subheader('Query Result:')
            st.write(answer)
        else:
            st.warning('No documents found matching the query.')
