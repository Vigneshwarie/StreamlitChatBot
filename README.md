# StreamlitDocChat

## Description
StreamlitDocChat is an app that chunks documents, stores them in MongoDB, and enables conversational interaction using OpenAI's language model, allowing users to chat with their documents effortlessly.

## Tech Stack
**Python:** The core programming language used for the application logic.   
**MongoDB:** A NoSQL database for storing document chunks.   
**OpenAI:** Provides the language model for conversational interactions.   

## Installation
### Prerequisites
Before you begin, ensure you have met the following requirements:   
- Python 3.8 or higher   
- MongoDB   
- OpenAI API key

### Clone the Repository
```
git clone https://github.com/Vigneshwarie/StreamlitDocChat.git
cd StreamlitDocChat
```
### Set Up the Virtual Environment
Create and activate a virtual environment:   
```
python -m venv .venv
source .venv/bin/activate  
```
### Install Dependencies
Install the necessary packages from requirements.txt:    
```
pip install -r requirements.txt
```
### Configuration
Create a .env file in the root directory of your project and add your OpenAI API key and MongoDB URI:    
```
OPENAI_API_KEY=your_openai_api_key
MONGODB_CONNECTION_STRING=your_mongodb_uri
MONGODB_DB_NAME=your_mongodb_db_name
MONGODB_COLLECTION_NAME=your_mongodb_collection_name
```
### Run the Application
Start the application:    
```
streamlit run app.py
```

## Credits
- [OpenAI](https://www.openai.com/) for providing the language model.
- [MongoDB](https://www.mongodb.com/) for the database solution.

## License
 ![Github license](https://img.shields.io/badge/license-MIT-blue.svg) 

