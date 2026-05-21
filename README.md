Built this to practice RAG pipelines end to end using real tools.
# Simplified Docs

A RAG-powered legal document assistant that reads contracts, leases, and terms of service — and explains them in plain English.

** LIVE DEMO **: https://pdf-assistant-kdqrhxjeb2wahzkij3rkj2.streamlit.app/  


## What it does
Upload any legal PDF and ask questions like:
- "Are there any red flags?"
- "What am I actually agreeing to?"
- "Which clauses are risky for me?"


## Features
- Upload any PDF and ask questions about it
- Flags risky clauses and explains legal jargon in plain English
- Supports follow-up questions with conversation memory
- Switch PDFs anytime — app resets automatically

## Tech Stack
- LangChain
- Google Gemini (LLM + Embeddings)
- ChromaDB
- Streamlit

## Setup
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file: `GOOGLE_API_KEY=your_key_here`
4. Run: `streamlit run app.py`
