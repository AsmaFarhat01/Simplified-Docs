import streamlit as st
import tempfile
from rag import load_document
from rag import setup_rag
import os


if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_file" not in st.session_state:
    st.session_state.current_file = None
if "chain" not in st.session_state:
    st.session_state.chain = None


st.title('PDF Assistant')
st.write('Upload your PDF below')

uploaded_file = st.file_uploader("choose a PDF",type="PDF")

if uploaded_file:
    if uploaded_file.name != st.session_state.current_file:
        with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as tmp:
            
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
    

    
        st.session_state.messages.clear()
        st.session_state.current_file = uploaded_file.name

        texts = load_document(tmp_path)
        st.session_state.chain = setup_rag(texts)
    
        os.remove(tmp_path)

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

user_question = st.chat_input("Ask a question about your PDF")
    
      


if user_question and st.session_state.chain:
    session_id = st.session_state.current_file
    result = st.session_state.chain.invoke(
         {"question" :user_question},
            config = {"configurable":{"session_id":"abc123"}})
    st.session_state.messages.append({"role": "user", "content": user_question})
    st.session_state.messages.append({"role": "assistant", "content": result})
    st.chat_message("user").write(user_question)
    st.chat_message("assistant").write(result)
        

   






