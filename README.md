# Chat_AI Project

โปรเจกต์นี้เป็นส่วน Backend ของระบบ Chat AI ที่พัฒนาด้วย FastAPI (Python)
** Open AI ที่ใช้คือ Ollama **
### ต้องติดตั้ง Ollama ในเครื่องด้วยครับและ ดึง Moduls มาใช้ พิม ollama pull ตามด้วย Moduls ดังนี้

* mxbai-embed-large:latest   
* gemma3:1b                  
* all-minilm:latest           
* llama3:latest
        
## การเริ่มต้นใช้งาน (Getting Started)

### ข้อกำหนด (Prerequisites)

* **Python 3.x**: แนะนำ Python 3.9 หรือสูงกว่า (ดาวน์โหลดได้จาก [python.org](https://www.python.org/downloads/))
* **pip**: ตัวจัดการแพ็กเกจของ Python (มักจะมาพร้อมกับการติดตั้ง Python)

### ขั้นตอนการติดตั้งและการรัน

1.  **โคลน Repository:**
    เปิด Command Prompt (หรือ Terminal) แล้วโคลนโปรเจกต์:
    ```bash
    git clone [https://github.com/Pokpong735/Chat_testAI.git](https://github.com/Pokpong735/Chat_testAI.git)
    ```
    จากนั้นเข้าไปในโฟลเดอร์โปรเจกต์:
    ```bash
    cd Chat_testAI
    ```

2.  **สร้างและเปิดใช้งาน Virtual Environment:**
    สร้างสภาพแวดล้อมเสมือนสำหรับโปรเจกต์นี้:
    ```bash
    python -m venv venv
    ```
    เปิดใช้งาน Virtual Environment:
    * **บน Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **บน macOS / Linux:**
        ```bash
        source venv/bin/activate
        ```
    (เมื่อเปิดใช้งานสำเร็จ คุณจะเห็น `(venv)` นำหน้า Path ใน Command Prompt/Terminal)

3.  **ติดตั้ง Dependencies ของ Python:**
    ติดตั้งไลบรารี Python ทั้งหมดที่จำเป็น รวมถึง FastAPI และ Uvicorn โดยใช้ไฟล์ `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    **หมายเหตุ:** ตรวจสอบให้แน่ใจว่าไฟล์ `requirements.txt` ของคุณมี `fastapi` และ `uvicorn[standard]` (หรือแค่ `uvicorn` ถ้าคุณจัดการแพ็กเกจเสริมเอง) อยู่ด้วย

4.  **รัน Backend Application:**
    หลังจากติดตั้งทุกอย่างเรียบร้อย คุณสามารถรัน Backend ของคุณได้โดยใช้ Uvicorn:
    ```bash
    uvicorn main_backend:app --reload
    ```
    * **คำอธิบาย:**
        * `main_backend`: คือชื่อไฟล์ Python ของคุณ (จาก `main_backend.py`)
        * `app`: คือชื่อของ Object FastAPI Instance ที่คุณสร้างไว้ในไฟล์ `main_backend.py` (เช่น `app = FastAPI()`)
        * `--reload`: ตัวเลือกนี้จะทำให้เซิร์ฟเวอร์รีโหลดโดยอัตโนมัติเมื่อมีการเปลี่ยนแปลงโค้ดในระหว่างการพัฒนา
    * Backend จะรันที่ `http://127.0.0.1:8000` โดยค่าเริ่มต้น (หรือพอร์ตอื่นๆ หากมีการกำหนดค่าไว้)

5. **ลองยิง API ผ่าน POSTMAN , THUNTER**
    ```bash
    http://127.0.0.1:8000/upload_csv แนบไฟล์ใน body 1.key = file    2.Value = ไฟล์ที่จะเอาลง
    ถ้าผ่านจะขึ้น Status ว่า "CSV loaded and vectorstore built"
    ```

6. **ลองถาม**
    ```bash
    http://127.0.0.1:8000/ask แนบคำตอบใน body 1.key = query  2.Value = คำถามที่จะถาม
    AI จะตอบถ้ามันสามาถตอบได้ และ จะตอบ i don't know ถ้าไม่รู้
    ```
---

1.  **การตั้งค่า Frontend (React/Web Application):**

    a.  **ติดตั้ง Dependencies ของ Node.js:**
        cd font ก่อน  
        ในโฟลเดอร์โปรเจกต์หลัก (ที่เดียวกับ `package.json`):
        ```bash
        npm install
        ```
        หรือถ้าคุณใช้ Yarn:
        ```bash
        yarn install
        ```

    b.  **รัน Frontend Application:**
        ```bash
        npm start
        ```
        หรือถ้าคุณใช้ Yarn:
        ```bash
        yarn start
        ```
        Frontend จะเปิดในเบราว์เซอร์ที่ `http://localhost:3000` โดยอัตโนมัติ (หรือพอร์ตอื่นๆ ที่โปรเจกต์ React กำหนด)
