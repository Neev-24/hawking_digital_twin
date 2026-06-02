# 🌌 Professor Stephen Hawking — Digital Twin Interface
### AIMS DTU Summer Project 2026

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