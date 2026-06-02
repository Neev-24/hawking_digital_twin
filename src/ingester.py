import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- PATH SETUP ---
# Grab paths relative to where this file is running
SRC_DIR = os.path.dirname(os.path.abspath(__file__))          
PROJECT_ROOT = os.path.dirname(SRC_DIR)                      

# Data lives in root, DB sits right here in src
DATA_DIR = os.path.join(PROJECT_ROOT, "data")                 
DB_DIR = os.path.join(SRC_DIR, "chroma_db")                  

print(f"Reading PDFs from: {DATA_DIR}")
print(f"Target DB path: {DB_DIR}\n")


# --- LOADING THE DATA ---
all_documents = []
if not os.path.exists(DATA_DIR):
    print(f"Error: Missing data folder at {DATA_DIR}")
    exit()

# Filter out only PDFs from the data directory
pdf_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.pdf')]

if not pdf_files:
    print("No PDFs found! Drop some transcripts/papers into the data folder first.")
    exit()

# Loop through and parse each PDF page by page
for pdf_file in pdf_files:
    pdf_path = os.path.join(DATA_DIR, pdf_file)
    print(f"Processing: {pdf_file}")
    try:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        all_documents.extend(pages)
    except Exception as e:
        print(f"Skipping broken file {pdf_file} due to error: {e}")

print(f"\nSuccessfully loaded {len(all_documents)} total pages.")


# --- CHUNKING LOGIC ---
# Chop text into manageable sizes so context isn't too huge for the LLM window
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=120,
    separators=["\n\n", "\n", ".", " ", ""]
)

print("Splitting text...")
chunks = text_splitter.split_documents(all_documents)
print(f"Created {len(chunks)} chunks.")


# --- EMBEDDING & STORAGE ---
print("Loading all-MiniLM-L6-v2 local embedding model...")
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print("Generating vectors and saving to ChromaDB...")
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_function,
    persist_directory=DB_DIR
)

print(f"\nDone! Knowledge base generated at: {DB_DIR}")