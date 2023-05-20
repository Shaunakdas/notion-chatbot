"""This script handles the process of importing Notion data into LangChain."""

from pathlib import Path
from langchain.text_splitter import CharacterTextSplitter
import faiss
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import pickle


# Load the data as exported by Notion
# Here, we're retrieving all markdown files under 'Notion_DB/' directory.
ps = list(Path("Notion_DB/").glob("**/*.md"))

data = []
sources = []

# For each markdown file, we read the file content and add it to our 'data' list.
# We also record the source file path for each data chunk.
for p in ps:
    with open(p) as f:
        data.append(f.read())
    sources.append(p)

# Due to the context limits of the language models, we may need to split the documents into smaller chunks.
# 'CharacterTextSplitter' helps to split the text into chunks of a specific size. 
# Here, we've set the chunk size as 1500 and used newline as the separator.
text_splitter = CharacterTextSplitter(chunk_size=1500, separator="\n")
docs = []
metadatas = []

# For each data chunk, we split it into smaller pieces and extend our 'docs' list with these pieces.
# Correspondingly, we also extend 'metadatas' with the source information for each piece.
for i, d in enumerate(data):
    splits = text_splitter.split_text(d)
    docs.extend(splits)
    metadatas.extend([{"source": sources[i]}] * len(splits))


# With the help of 'OpenAIEmbeddings', we create a 'FAISS' vector store from the documents. 
# This store is then written to disk as 'docs.index'.
# Note: we set 'metadatas' as a parameter to keep track of the source of each document chunk.
store = FAISS.from_texts(docs, OpenAIEmbeddings(), metadatas=metadatas)
faiss.write_index(store.index, "docs.index")

# For the sake of reducing memory footprint, we set the 'store.index' to None.
store.index = None

# Finally, we serialize the 'store' object (without the index) and save it as 'faiss_store.pkl'.
with open("faiss_store.pkl", "wb") as f:
    pickle.dump(store, f)
