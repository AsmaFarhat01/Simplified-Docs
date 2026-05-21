Built this to practice RAG pipelines end to end using real tools.
# PDF Assistant

A RAG-powered chatbot that answers questions based on uploaded PDF documents.

## Features
- Upload any PDF and ask questions about it
- Answers based strictly on document content
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
