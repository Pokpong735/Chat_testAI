from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.chains import RetrievalQA
import os
import tempfile
import traceback # <<< เพิ่มบรรทัดนี้

# ... โค้ดส่วนที่เหลือของคุณ
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000", # just test
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Origin CORS
    allow_credentials=True,      # (cookies, authorization headers)
    allow_methods=["*"],         # HTTP Methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],         # อนุญาตทุก Headers
)



vectorstore = None
retriever = None

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    global vectorstore, retriever

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(await file.read())
        file_path = tmp.name

    # ระบุ encoding ที่เหมาะสม
    loader = CSVLoader(file_path, encoding="utf-8")  # หรือ "utf-8-sig"
    documents = loader.load()

    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    vectorstore = FAISS.from_documents(documents, embeddings)
    retriever = vectorstore.as_retriever()

    return {"status": "CSV loaded and vectorstore built"}

@app.post("/ask")
# async def ask_query(query: str = Form(...)):
#     if retriever is None:
#         return {"error": "Please upload a CSV first."}

#     llm = Ollama(model="gemma3:1b")  # หรือ llama3
#     qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
#     result = qa.run(query)
#     return {"answer": result}
async def ask_query(query: str = Form(...)):
    print(f"Received query: {query}")
    if retriever is None:
        print("Error: Vectorstore not initialized. Please upload CSV first.")
        return {"error": "Please upload a CSV first."}

    try:
        llm_translator = OllamaLLM(model="gemma3:1b") # หรือ llama3, หรือโมเดลที่เก่งการแปล
        # แปลคำถามภาษาไทยเป็นภาษาอังกฤษ
        # (อาจจะต้องปรับ prompt ให้เหมาะสมกับการแปล)
        translated_query = llm_translator.invoke(f"Translate this Thai query to English: '{query}'")
        print(f"Translated query: {translated_query}")

        llm_qa = OllamaLLM(model="gemma3:1b") # LLM สำหรับ QA
        qa = RetrievalQA.from_chain_type(llm=llm_qa, retriever=retriever)
        # ใช้คำถามที่แปลแล้วส่งไปให้ Retriever
        result = qa.run(translated_query)

    
        # final_result = llm_qa.invoke(f"Translate this English answer to Thai: '{result}'")
        # return {"answer": final_result}

        return {"answer": result} # หรือคืนผลลัพธ์เป็นภาษาอังกฤษไปเลย (ถ้า Front-end จัดการได้)

    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"An error occurred during query processing: {e}")
        print(error_traceback)
        return {"error": f"Failed to process query: {e}", "details": error_traceback}



