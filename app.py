import streamlit as st
import tempfile
from rag import load_document
from rag import setup_rag, evaluate_rag
import os


if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_file" not in st.session_state:
    st.session_state.current_file = None
if "chain" not in st.session_state:
    st.session_state.chain = None

def get_score_label(eval_score):
    if eval_score>= 0.85:
        return "The score is excellent"
    elif eval_score >= 0.70:
         return "The score is good"
    else:
        return "Needs improvement"

st.title("🗂️ Simplified Docs")
st.markdown("#### *Legal documents, finally in plain English.*")
st.divider()

st.markdown("**Upload a contract, lease, terms of service, or any legal PDF below 👇**")

uploaded_file = st.file_uploader("Choose a PDF", type="PDF")

st.markdown("""
💡 **Not sure what to ask? Try these:**
- 🚩 *Are there any red flags in this document?*
- 📋 *What am I actually agreeing to?*
- ⚠️ *Which clauses are risky for me?*
- 🔍 *Explain this in simple English*
""")
if uploaded_file:
    if uploaded_file.name != st.session_state.current_file:
        with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as tmp:
            
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
    
        st.session_state.messages.clear()
        st.session_state.current_file = uploaded_file.name
        try:

            texts = load_document(tmp_path)
            st.session_state.chain,st.session_state.model,st.session_state.retriever = setup_rag(texts)
        except Exception as e:
            st.error("❌ Could not process this file. Please make sure it's a valid PDF.")
            os.remove(tmp_path)
            st.stop()
        try:

            st.session_state.eval_scores = evaluate_rag(st.session_state.retriever,st.session_state.model, st.session_state.chain,st.session_state.current_file)
        except Exception as e:
             st.warning("⚠️ Evaluation could not be completed. You can still chat with your document!")
             st.session_state.eval_scores = []
        
        
if "eval_scores" in st.session_state and st.session_state.eval_scores:
    st.markdown("### 📊 RAG Evaluation Scores")
    for item in st.session_state.eval_scores:
        st.write(f"**Q:** {item['question']}")
        st.write(f"**Score:** {item['score']:.2f} - {get_score_label(item['score'])}")
        st.divider()

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

user_question = st.chat_input("Ask a question about your PDF")
    
      


if user_question and st.session_state.chain:
    session_id = st.session_state.current_file
    result = st.session_state.chain.invoke(
         {"question" :user_question},
            config = {"configurable":{"session_id":st.session_state.current_file}})
    st.session_state.messages.append({"role": "user", "content": user_question})
    st.session_state.messages.append({"role": "assistant", "content": result})
    st.chat_message("user").write(user_question)
    st.chat_message("assistant").write(result)
        

   






