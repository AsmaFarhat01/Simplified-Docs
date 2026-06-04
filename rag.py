import os
#import shutil
from dotenv import load_dotenv
import uuid
import json
import time

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
from sklearn.metrics.pairwise import cosine_similarity



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

    retriever = vector_store.as_retriever(search_kwargs={"k":5})
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
    system_message = "You are a legal document assistant." \
    " Your job is to help users understand contracts, agreements, and legal documents in plain English." \
    " When answering, flag any risky or unusual clauses, explain legal jargon simply, and highlight what the user is agreeing to." \
    " Always be clear and direct. Today's date is " + today
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
      
    return chain_with_history, model,retriever

def evaluate_rag(retriever,model,chain,session_id):
   fetched_chunks = retriever.invoke("legal clauses and obligations")
   fetched_text = [x.page_content for x  in fetched_chunks]
   context = "".join(fetched_text)

   eval_prompt = f"""you are a lawyer. generate most frequently asked 3 Q & A pairs based on the context provided below .
                  Respond only in JSON format. example json format: [{{"question": "...", "expected": "..."}}]
                  "Keep each expected answer under 6 sentences.
                  context: {context}"""
   
   eval_response = model.invoke(eval_prompt)
   response_text = eval_response.content
   response_text = response_text.strip().removeprefix("```json").removesuffix("```").strip()
   qa_pairs = json.loads(response_text)
   embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
   scores_list = []
   for pair in qa_pairs:
      answer =  chain.invoke({"question": pair["question"]}, config={"configurable": {"session_id": session_id}})
      query_vector = embeddings.embed_query(answer[:2000])
      expected_vector = embeddings.embed_query(pair["expected"][:2000])
      score = cosine_similarity([query_vector], [expected_vector])[0][0]
      scores_list.append({"question":pair["question"],"expected":pair["expected"],"score":score})
      time.sleep(10)
   return scores_list
   


#if __name__ == "__main__":
    #texts = load_document(r"C:\Users\HP\Downloads\Service-Contract-Template.pdf")
    #chain, model, retriever = setup_rag(texts)
    #evaluate_rag(retriever, model, chain)

  

