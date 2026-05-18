import os
#import shutil
from dotenv import load_dotenv
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import date
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda



load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")


def load_document(file_path):
   loader = PyPDFLoader(file_path)
   documents = loader.load()
   text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000 ,chunk_overlap = 100)
   texts = text_splitter.split_documents(documents)
   return texts

def setup_rag(texts):
    #if os.path.exists("./chroma_langchain_db"):
        #shutil.rmtree("./chroma_langchain_db")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = Chroma.from_documents(
    documents= texts,
    embedding=embeddings,
    collection_name=str(uuid.uuid4())
    #persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
    )

    retriever = vector_store.as_retriever(search_kwargs={"k":20})
    model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1.0,  # Gemini 3.0+ defaults to 1.0
    max_tokens=None,
    timeout=None,
    max_retries=2,
    )
    store = {}
    def get_session_history(session_id):
      if session_id not in store:
          store[session_id] = ChatMessageHistory()
      return store[session_id]

    today = str(date.today())
    system_message = " You are an expert career coach and recruiter. Answer the questions based on the context" + "Today's date is " + today
    prompt = ChatPromptTemplate.from_messages(
      [
          ("system",system_message + "\n\n {context}"),
          MessagesPlaceholder(variable_name="history"),
          ("human", "{question}"),
      ]
  )

    chain = {"context": RunnableLambda(lambda x: x["question"]) | retriever,"question": RunnableLambda(lambda x: x["question"]), "history": RunnableLambda(lambda x: x.get("history", []))} | prompt | model | StrOutputParser()
    chain_with_history = RunnableWithMessageHistory(
      chain,
      get_session_history,
      input_messages_key="question",
      history_messages_key="history",
     
  )
      
    return chain_with_history
    


  

