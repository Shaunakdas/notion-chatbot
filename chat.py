"""Script to pose a query to the Notion database."""
import faiss
from langchain import OpenAI
from langchain.chains import VectorDBQAWithSourcesChain
import pickle
import argparse

# Create an argument parser to fetch the question from the command-line argument.
arg_parser = argparse.ArgumentParser(description='Pose a question to the Notion database.')
arg_parser.add_argument('question', type=str, help='The question to ask the Notion database')
parsed_args = arg_parser.parse_args()

# Load the LangChain, which is our Question-Answering model.
# 'faiss_store.pkl' contains the serialized store object, while 'docs.index' contains the actual index.
search_index = faiss.read_index("docs.index")

with open("faiss_store.pkl", "rb") as f:
    vector_store = pickle.load(f)

# Here, we reintegrate the search index into the vector store object.
vector_store.index = search_index
qa_model = VectorDBQAWithSourcesChain.from_llm(llm=OpenAI(temperature=0), vectorstore=vector_store)

# Pose the user's question to the QA model.
response = qa_model({"question": parsed_args.question})

# Display the answer and the source of the answer to the console.
print(f"Answer: {response['answer']}")
print(f"Sources: {response['sources']}")
