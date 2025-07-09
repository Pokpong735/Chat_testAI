from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.agents import tool, AgentExecutor, create_react_agent # <<< เพิ่ม imports เหล่านี้
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
import tempfile
import traceback

app = FastAPI()

# CORS settings
origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vectorstore = None
retriever = None

# --- Prompt Template สำหรับ RAG ---
RAG_PROMPT_TEMPLATE = """You are an AI assistant specialized in answering questions about products based on the provided context.
Answer the question only based on the context provided.
If the answer is not found in the context, politely state that you cannot find the answer in the provided information.
Do not make up any information.
Keep the answer concise and relevant.

When the question asks for a list of products or items, present them as a numbered list (e.g., 1. Item One, 2. Item Two, 3. Item Three).
If there is only one item, just state the item name.

Context:
{context}

Question: {question}
Answer in Thai if the question is in Thai, otherwise answer in English.
"""
# --- Tool สำหรับตอบคำถามทั่วไปเกี่ยวกับผลิตภัณฑ์ ---
@tool
def answer_product_question(question: str) -> str:
    """
    Answers general inquiries and provides detailed descriptions about products,
    features, or characteristics by searching through the loaded product data.
    Use this tool for questions like 'What is X?', 'Tell me about Y?', 'What are the features of Z?',
    or to list products based on a general attribute (e.g., 'What kinds of wireless products are available?').
    Input must be an English question or a query describing the product/attribute.
    """
    global retriever
    if retriever is None:
        return "Product data is not loaded. Please upload the CSV file first."

    try:
        llm_qa = OllamaLLM(model="gemma3:1b") # LLM สำหรับ QA
        custom_prompt = PromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm_qa,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": custom_prompt}
        )
        response = qa_chain.invoke({"query": question})
        print("PASS1")
        return response["result"]

    except Exception as e:
        print(f"Error in answer_product_question tool: {e}")
        traceback.print_exc()
        return f"An error occurred while answering the general product question: {e}"

# --- Tool ใหม่: สำหรับการถามราคาและปริมาณคงเหลือ (เฉพาะเจาะจงสินค้า) ---
@tool
def get_product_price_and_stock(product_name: str) -> str:
    """
    Retrieves the exact price and current stock quantity of a specific product.
    Use this tool ONLY when the user explicitly asks for the 'price', 'cost', 'how much', 'stock', 'quantity', 'available', or 'remaining'
    of a PARTICULAR, NAMED product (e.g., 'Laptop Pro', 'Smart Phone').
    The input must be the exact name of the product you are asking about, in English.
    """
    global retriever
    if retriever is None:
        return "Product data is not loaded. Please upload the CSV file first."

    try:
        llm_qa = OllamaLLM(model="gemma3:1b") # LLM สำหรับ QA
        custom_prompt = PromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm_qa,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": custom_prompt}
        )
        query_for_rag = f"What is the price and stock quantity of {product_name}?"
        response = qa_chain.invoke({"query": query_for_rag})
        result = response["result"]

        if "not found" in result.lower() or "no information" in result.lower():
            return f"Could not find specific price and stock information for {product_name} in the provided data."
        
        return result

    except Exception as e:
        print(f"Error in get_product_price_and_stock tool: {e}")
        traceback.print_exc()
        return f"An error occurred while retrieving price and stock: {e}"

# --- Global Agent (สำหรับ Function Calling) ---

agent_executor = None # จะเก็บ AgentExecutor ที่สร้างจาก LLM และ Tools


@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    global vectorstore, retriever, agent_executor # ต้อง global agent_executor ด้วย
    file_path = None

    print(f"Received upload request for file: {file.filename}")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            content = await file.read()
            tmp.write(content)
            file_path = tmp.name
        print(f"File saved temporarily at: {file_path}")

        loader = CSVLoader(file_path, encoding="utf-8")
        documents = loader.load()
        print(f"Loaded {len(documents)} documents from CSV.")

        embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        print("OllamaEmbeddings initialized with model: mxbai-embed-large")

        vectorstore = FAISS.from_documents(documents, embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        print("Vectorstore built successfully.")

        # --- สร้าง Agent หลังจากที่ Vectorstore พร้อมใช้งาน ---
        llm_agent = OllamaLLM(model="gemma3:1b") # LLM ที่จะใช้ควบคุม Agent
        tools = [answer_product_question , get_product_price_and_stock] # ลิสต์ของ Tools ที่ Agent ใช้ได้

        # Prompt สำหรับ Agent (เพื่อให้ Agent เข้าใจว่าจะใช้ Tool เมื่อไหร่)
        # นี่คือ prompt พื้นฐานสำหรับ ReAct agent
        # สามารถปรับแต่งได้ตามต้องการ
        agent_prompt = PromptTemplate.from_template("""Answer the following questions as best you can. You have access to the following tools:

        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question. When the observation contains a list with numbering or bullet points, ensure that the final answer preserves that formatting.

        Here are some examples to guide your thought process and tool usage:

        # Example 1: Asking for price and stock of a specific product
        Question: How much does the Bicycle cost and what is its stock quantity?
        Thought: The user is asking for the price and stock of a specific product, "Bicycle". The `get_product_price_and_stock` tool is designed for this. I need to provide the exact product name as input.
        Action: get_product_price_and_stock
        Action Input: Bicycle
        Observation: The price of Bicycle is 234 USD and the stock quantity is 394.
        Thought: I have successfully retrieved the price and stock quantity for the Bicycle. I can now provide the final answer to the user.
        Final Answer: The price of Bicycle is 234 USD and the stock quantity is 394.

        # Example 2: Asking for general product information or a list of products by feature, expect numbered list
        Question: What kinds of wireless products are available?
        Thought: The user is asking for a list of products based on a general attribute "wireless", not a specific price or stock query. The `answer_product_question` tool is suitable for general inquiries and listing products by attributes. I should pass the original translated question to this tool.
        Action: answer_product_question
        Action Input: What kinds of wireless products are available?
        Observation: Please see the following wireless products:\n1. Wireless Tablet Router Printer Wireless Premium Air\n2. Wireless Dock\n3. Advanced Router Rechargeable
        Thought: I have retrieved the list of wireless products and it is already formatted as a numbered list. I can now provide this as the final answer to the user, preserving the numbering.
        Final Answer: Please see the following wireless products:\n1. Wireless Tablet Router Printer Wireless Premium Air\n2. Wireless Dock\n3. Advanced Router Rechargeable

        # Example 3: Asking for information not found in data
        Question: What is the warranty period for product XYZ?
        Thought: The user is asking for specific product information. The `answer_product_question` tool can handle general inquiries. I will use it to search for the warranty information.
        Action: answer_product_question
        Action Input: What is the warranty period for product XYZ?
        Observation: I cannot find information about the warranty period for product XYZ in the provided data.
        Thought: The tool indicated that the information about the warranty period for product XYZ is not available in the provided data. I should inform the user politely.
        Final Answer: I am sorry, I cannot find information about the warranty period for product XYZ in the relevant data.

        Begin!

        Question: {input}
        Thought:{agent_scratchpad}""")


        agent = create_react_agent(llm_agent, tools, agent_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
        print("Agent created and ready to use.")

        return {"status": "CSV loaded and vectorstore built. Agent initialized."}

    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"An error occurred during CSV upload or vectorstore creation: {e}")
        print(error_traceback)
        return {"error": f"Failed to process CSV: {e}", "details": error_traceback}
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"Temporary file {file_path} deleted.")


@app.post("/ask")
async def ask_query(query: str = Form(...)):
    global agent_executor # ต้อง global agent_executor ด้วย
    print(f"Received query: {query}")

    if agent_executor is None:
        print("Error: Agent not initialized. Please upload CSV first.")
        return {"error": "Please upload a CSV file and initialize the system first."}

    try:
        # 1. LLM สำหรับการแปลคำถาม (Query Translation)
        llm_translator = OllamaLLM(model="gemma3:1b")
        translation_prompt = f"Translate this query to English. Respond only with the English translation, without any additional text or explanation: '{query}'"
        translated_query = llm_translator.invoke(translation_prompt)
        translated_query = translated_query.strip().replace('"', '')
        print(f"Translated query for agent: '{translated_query}'")

        # 2. ส่งคำถามที่แปลแล้วไปให้ AgentExecutor
        # AgentExecutor จะตัดสินใจว่าจะใช้ Tool ไหน (answer_product_question)
        agent_response = await agent_executor.ainvoke({"input": translated_query}) # ใช้ ainvoke สำหรับ async
        result = agent_response["output"]

        print(f"Final answer from agent: {result[:100]}...")

        # 3. (Optional) แปลคำตอบสุดท้ายกลับเป็นภาษาไทย ถ้า LLM ตอบเป็นภาษาอังกฤษ
        # หากต้องการให้ LLM ที่เป็น Agent ตอบภาษาอังกฤษ และแปลกลับที่นี่:
        # prompt_translate_back = f"Translate this English answer to Thai, keeping the context and meaning accurate: '{result}'"
        # final_answer_thai = llm_translator.invoke(prompt_translate_back) # ใช้ llm_translator ก็ได้
        # print(f"Final Answer (Thai): {final_answer_thai[:100]}...")
        # return {"answer": final_answer_thai}

        return {"answer": result}

    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"An error occurred during query processing by agent: {e}")
        print(error_traceback)
        return {"error": f"Failed to process query: {e}", "details": error_traceback}