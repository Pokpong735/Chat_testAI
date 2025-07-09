const API_BASE_URL = process.env.REACT_APP_BACKEND_API_URL || 'http://127.0.0.1:8000';

const GetMessageService = {
    /**
     * ส่งข้อความของผู้ใช้ไปยัง Backend และรับคำตอบจาก OpenAI
     * @param {string} userMessage ข้อความที่ผู้ใช้พิมพ์
     * @returns {Promise<string>} คำตอบที่ได้จาก OpenAI
     */
   getOpenAIResponse: async (userMessage) => {
    try {
        // สร้าง FormData object
        const formData = new FormData();
        formData.append("query", userMessage); // เพิ่ม field "query"

        const response = await fetch('http://127.0.0.1:8000/ask', {
            method: 'POST',
            // ไม่ต้องระบุ Content-Type เมื่อใช้ FormData()
            // Browser จะตั้งค่า 'Content-Type: multipart/form-data' พร้อม boundary ให้เอง
            body: formData, // ส่ง FormData object ตรงๆ
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.answer;
    } catch (error) {
        console.error('Error fetching OpenAI response:', error);
        throw new Error(error.message || 'Failed to get response from OpenAI.');
    }
},

    /**
   
     * @param {string} userMessage 
     * @returns {Promise<string>} 
     */
    getOpenAIResponseButTesting: async (userMessage) => {
        return new Promise((resolve) => {
            // จำลองการหน่วงเวลาเหมือนการเรียก API จริง
            setTimeout(() => {
                const mockResponses = [
                    `ทดสอบ: คุณถามว่า "${userMessage}" ใช่ไหม?`,
                    `ทดสอบ: นี่คือคำตอบจำลองสำหรับ "${userMessage}"`,
                    `ทดสอบ: ฉันเป็น AI ที่ยังไม่มี backend จริงๆ ตอนนี้!`,
                    `ทดสอบ: ข้อความของคุณคือ "${userMessage}"`,
                    `ทดสอบ: ลองพิมพ์อะไรอีกสิ!`,
                ];
                const randomIndex = Math.floor(Math.random() * mockResponses.length);
                resolve(mockResponses[randomIndex]);
            }, 4000); // จำลองการหน่วงเวลา 4 วินาที
        });
    }
};

export default GetMessageService;