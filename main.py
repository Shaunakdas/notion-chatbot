"""This script forms the frontend of the application"""
import streamlit as st
from streamlit_chat import message
import faiss
from langchain import OpenAI
from langchain.chains import VectorDBQAWithSourcesChain
import pickle

# Load the LangChain which is our question-answering model.
# 'faiss_store.pkl' contains the serialized store object, while 'docs.index' contains the actual index.
index = faiss.read_index("docs.index")

with open("faiss_store.pkl", "rb") as f:
    serialized_store = pickle.load(f)

# Here, we reintegrate the index into the store object.
serialized_store.index = index
question_answer_model = VectorDBQAWithSourcesChain.from_llm(llm=OpenAI(temperature=0), vectorstore=serialized_store)


# Below is the StreamLit user interface setup.
# The page is configured with a title and an icon.
st.set_page_config(page_title="Blendle Notion QA Bot", page_icon=":robot:")
st.header("Blendle Notion QA Bot")

# Here, we are initializing or updating the session states 'generated' and 'past'
if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []


# This function fetches the user's input text from the text input box.
def fetch_user_input():
    user_query = st.text_input("You: ", "Hello, how are you?", key="input")
    return user_query

user_query = fetch_user_input()

# If there's user input, we fetch the response from our model.
if user_query:
    model_response = question_answer_model({"question": user_query})
    response_output = f"Answer: {model_response['answer']}\nSources: {model_response['sources']}"

    # Append user queries and model responses to their respective session states.
    st.session_state.past.append(user_query)
    st.session_state.generated.append(response_output)

# If there's any response generated, we display it in a chat-like format.
if st.session_state["generated"]:
    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
