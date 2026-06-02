import os
import streamlit as st
from google import genai
from google.genai import types
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from memory import load_memories, save_memory  
from dotenv import load_dotenv
import time

# Pull environment variables from the root .env file
load_dotenv()

# --- UI & PAGE SETUP ---
st.set_page_config(page_title="Stephen Hawking Digital Twin", page_icon="🌌", layout="centered")
st.title("🌌 Professor Stephen Hawking")
st.subheader("Digital Twin Interface — AIMS DTU Summer Project 2026")

# Profile selector in the sidebar to handle independent database users
st.sidebar.title("🔐 User Profile")
user_name = st.sidebar.text_input("Enter your name to load memories:", value="Guest")

# --- PATHS & RAG STORAGE ---
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(SRC_DIR, "chroma_db")

@st.cache_resource
def load_vector_db():
    # Cache the embedding model loader so it doesn't download on every user turn
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(persist_directory=DB_DIR, embedding_function=embedding_function)

vector_db = load_vector_db()


# --- API VALIDATION & ON-DEMAND QUOTA CONFIGURATION ---
API_KEYS_RAW = os.environ.get("GEMINI_API_KEYS", "")
API_KEYS = [key.strip() for key in API_KEYS_RAW.split(",") if key.strip()]

if not API_KEYS:
    st.error("🔑 API Keys Missing! Please verify your GEMINI_API_KEYS array in your .env file.")
    st.stop()

# Track the current active key index globally within the session state
if "api_key_index" not in st.session_state:
    st.session_state.api_key_index = 0

def get_active_gemini_client():
    """Returns a client instance for the current active key without shifting the index."""
    current_key = API_KEYS[st.session_state.api_key_index]
    return genai.Client(api_key=current_key)

def rotate_to_next_key():
    """Explicitly cycles the pointer to the next key block only when a quota exhaustion occurs."""
    old_index = st.session_state.api_key_index
    st.session_state.api_key_index = (old_index + 1) % len(API_KEYS)
    return get_active_gemini_client()


# Pull persistent history from the local Postgres instance
long_term_history = load_memories(user_name)

# --- VECTOR SEARCH LOGIC ---
def get_grounding_context(query: str, k: int = 3) -> str:
    """Queries ChromaDB to fetch matching document chunks."""
    docs = vector_db.similarity_search(query, k=k)
    context_blocks = []
    for d in docs:
        source = os.path.basename(d.metadata.get('source', 'Unknown Source'))
        context_blocks.append(f"--- Context from source [{source}] ---\n{d.page_content}")
    return "\n\n".join(context_blocks)


# --- PERSONA LAYER ---
CURRENT_YEAR = 2026 

HAWKING_SYSTEM_PROMPT = f"""
You are a Digital Twin of Professor Stephen Hawking, acting exactly as he would in knowledge, reasoning style, and personality.
Your tone must be highly intellectual, pedagogically clear, British, and infused with his signature sharp, witty, and self-deprecating humor.

The current year is strictly {CURRENT_YEAR}. You are fully aware of your entire life's timeline, including your later works on Soft Hair (2016) and your final book release in 2018.

CRITICAL FORMATTING CONSTRAINTS (Voice Synthesizer Authenticity):
1. NO BULLET POINTS OR NUMBERED LISTS: You must NEVER answer using bullet points or lists.
2. SYNTHESIZER BREVITY: Because you speak through a communication equalizer, you must be extremely concise. Deliver your ideas in exactly 1 to 2 short, punchy paragraphs. Maximize information density while keeping word counts low.
3. INLINE LATEX ONLY: Keep mathematical expressions integrated naturally using inline LaTeX.
4. PERSONAL MEMORY COGNIZANCE: Smoothly weave in details the user has shared with you in past interactions.
[WHAT YOU REMEMBER ABOUT THIS USER FROM PAST SESSIONS VIA POSTGRESQL]:
{long_term_history}

Never break character. Do not mention that you are an AI model, a chatbot.
"""


# --- CONVERSATION HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome back to my study. Though my physical mobility is limited, my mind remains completely free to explore the universe. What mysteries shall we ponder together today?"}
    ]

# Render chat logs dynamically on UI rerun events
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# --- EXECUTION TURN WITH AUTO-ROUTING FALLBACK ---
if user_input := st.chat_input("Ask about black holes, quantum gravity, or his life..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Pondering..."):
            
            # Prepare RAG Grounding Context
            context = get_grounding_context(user_input)
            full_payload = f"""
            [GROUNDING ARCHIVE CONTEXT]
            {context}
            
            [USER CONVERSATION INPUT]
            {user_input}
            """
            
            reply_text = None
            successful_client = None
            
            # Dynamically pull total pool count to bound our search loop
            total_keys_available = len(API_KEYS)
            keys_tested = 0

            # --- PHASE 1: LOOP UNTIL A WORKING PROJECT QUOTA IS FOUND ---
            while keys_tested < total_keys_available:
                try:
                    # Get whichever key index is currently active
                    current_client = get_active_gemini_client()
                    
                    # Test execution call
                    response = current_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=full_payload,
                        config=types.GenerateContentConfig(
                            system_instruction=HAWKING_SYSTEM_PROMPT,
                            temperature=0.6,
                        ),
                    )
                    
                    # If it didn't throw an exception, this key is completely valid!
                    reply_text = response.text
                    successful_client = current_client  # Lock this key down for background tasks
                    break
                    
                except Exception as e:
                    error_str = str(e).lower()
                    
                    # If this key hits the daily ceiling or a strict resource block
                    if "429" in error_str or "quota" in error_str or "exhausted" in error_str:
                        keys_tested += 1
                        st.toast(f"⚠️ Key {st.session_state.api_key_index + 1} is exhausted. Auto-skipping...")
                        
                        # Move the global pointer to the next key block
                        rotate_to_next_key()
                    
                    # Separate Handling: If it's a 503 IP-level burst limit block
                    elif "503" in error_str or "unavailable" in error_str:
                        st.warning("⏳ *Google's regional gateway is facing a temporary IP burst spike. Please wait a few moments and resubmit.*")
                        break
                    else:
                        # Print any other rare structural errors immediately
                        st.error(f"Execution exception encountered: {e}")
                        break

            # --- PHASE 2: OUTPUT RESPONSES & PROCESS SQL MEMORY ---
            if reply_text and successful_client:
                # Render the successful response to the UI
                st.write(reply_text)
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
                
                # Run the background memory compilation step using the same working client
                extraction_prompt = f"""
                Analyze this user statement: '{user_input}'. 
                If they explicitly mentioned their name, profession, interest, background, college, or personal facts, extract it as a short, 1-sentence declarative fact written in the third person (e.g., 'The user is an engineering student at DTU'). 
                If they did not share any personal details about themselves, reply with exactly one word: NONE.
                """
                
                # Slight internal spacing delay to ease IP burst metrics
                time.sleep(1.2)
                
                try:
                    memory_check = successful_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=extraction_prompt
                    )
                    extracted_fact = memory_check.text.strip()
                    
                    if "NONE" not in extracted_fact and user_name != "Guest":
                        save_memory(user_name, extracted_fact)
                except Exception:
                    # Ignore background storage drops silently to preserve presentation UX
                    pass
                    
            elif keys_tested >= total_keys_available:
                st.error("❌ **System Fault:** All configured project API keys inside your environmental pool are completely exhausted.")