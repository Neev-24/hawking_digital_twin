# 🌌 Professor Stephen Hawking — Digital Twin Interface
### AIMS DTU Summer Project 2026
🔗 Live Application: https://hawkingdigitaltwin.streamlit.app/
An advanced, context-aware Digital Twin agent of Professor Stephen Hawking. This project implements a modern Retrieval-Augmented Generation (RAG) pipeline combined with a persistent PostgreSQL relational storage layer to achieve high-fidelity persona consistency and cross-session memory tracking.

---

## 🏗️ System Architecture

The application is built upon three distinct engineering pillars:

1. **Frontend Interface (Streamlit):** A clean, custom UI utilizing a restricted system prompt constraint layer that enforces conversational brevity, bans bulleted responses, and mandates inline LaTeX formatting ($E=mc^2$).
2. **Knowledge Grounding Base (RAG via ChromaDB):** Combines academic physics papers with media interview scripts. Chunks are embedded using the `all-MiniLM-L6-v2` Hugging Face model to balance core scientific logic with conversational speech patterns.
3. **Long-Term Memory Layer (PostgreSQL):** Uses an asynchronous background extraction turn via the Gemini core engine to parse multi-turn dialogues, identify personal user attributes, and persist them across session restarts.

---

## 📂 Project Directory Structure

```text
hawking_digital_twin/
├── .env                  # Local secret environment variables (Protected)
├── .gitignore            # Git filters for environment separation
├── schema.sql            # PostgreSQL table schema
├── requirements.txt      # Project dependencies
└── src/
    ├── app.py            # Main execution pipeline & Streamlit UI
    ├── ingester.py       # Document parsing & vector embedding script
    ├── memory.py         # PostgreSQL database adapter
    └── chroma_db/        # Persisted vector database index
```

---

## What this project actually does

* **Sounds like Hawking:** Instead of acting like a generic AI assistant, the prompt forces the model to be short, sharp, and witty—matching how Professor Hawking actually spoke using his voice synthesizer. It also handles inline math formulas ($E=mc^2$) smoothly without breaking the layout.
* **Remembers you across sessions:** We split the data up. Academic papers and books are handled by the ChromaDB vector setup for facts, but your personal info (like your name or what you are studying) gets pulled out in the background and saved into a local PostgreSQL database so it remembers you next time you log in.
* **Doesn't crash when API keys run out:** Since the free tier of the Gemini API has strict daily project limits, the app is built to automatically skip a key if it hits a `429 Quota Exhausted` error. It will pop up a quick warning on the screen and seamlessly swap to the next working key in your list without crashing your chat session.

## What is in the submission folder

1. **This GitHub Repo:** Contains all the working Python scripts, the required packages (`requirements.txt`), and the database setup instructions (`schema.sql`).
2. **The Google Drive Link:** Contains the project documentation, a simple architecture diagram, a 2-minute screen recording showing the app working locally, and a PDF file containing 10 sample conversations showcasing the memory and persona in action.