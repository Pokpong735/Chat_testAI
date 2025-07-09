import React, { useState, useEffect, useRef } from 'react';
import GetMessageService from './Service/GetMessage';

function App() {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isSending, setIsSending] = useState(false); // State สำหรับแสดงสถานะการโหลด
  const chatContainerRef = useRef(null);

  // Effect ที่จะ Scroll ลงไปล่างสุดเมื่อมีข้อความใหม่
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleInputChange = (event) => {
    setNewMessage(event.target.value);
  };

  const handleSendMessage = async () => { // <--- ทำให้เป็น async function
    if (newMessage.trim() === '') return;

    const userMsg = newMessage.trim(); // เก็บข้อความผู้ใช้
    setNewMessage(''); // ล้างช่อง input ทันที

    // เพิ่มข้อความของผู้ใช้ลงไปใน UI ก่อน
    setMessages((prevMessages) => [
      ...prevMessages,
      { id: Date.now(), type: 'user', text: userMsg }
    ]);

    setIsSending(true); // ตั้งค่าสถานะว่ากำลังส่งข้อความ

    try {
      // เรียกใช้ Service เพื่อส่งข้อความไป Backend และรับคำตอบจาก OpenAI
      const openAIResponse = await GetMessageService.getOpenAIResponse(userMsg);

      // เพิ่มข้อความตอบกลับจาก OpenAI ลงไปใน UI
      setMessages((prevMessages) => [
        ...prevMessages,
        { id: Date.now() + 1, type: 'openai', text: openAIResponse }
      ]);
    } catch (error) {
      console.error('Failed to get OpenAI response:', error);
      // แสดงข้อความ error ให้ผู้ใช้เห็น (หรือจัดการ error ตามเหมาะสม)
      setMessages((prevMessages) => [
        ...prevMessages,
        { id: Date.now() + 1, type: 'error', text: `เกิดข้อผิดพลาด: ${error.message || 'ไม่สามารถรับคำตอบจาก OpenAI ได้'}` }
      ]);
    } finally {
      setIsSending(false); // สิ้นสุดสถานะการส่ง
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !isSending) { // <--- เพิ่มเช็คสถานะ isSending
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-400 p-4">
      <div className="flex flex-col h-[90vh] w-[90%] md:w-[70%] lg:w-[50%] bg-white shadow-2xl rounded-lg">

        <div
        ref={chatContainerRef}
        className="flex-grow overflow-y-auto p-4 border-b border-gray-200 hide-scrollbar" // <--- เพิ่ม hide-scrollbar
      >
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col m-3 text-base ${
                msg.type === 'user' ? 'items-end text-right' : msg.type === 'openai' ? 'items-start text-left' : 'items-center text-center text-red-600' // สำหรับ error
              }`}
            >
              <div className="font-bold text-sm text-gray-600 mb-1">
                {msg.type === 'user' ? 'USER' : msg.type === 'openai' ? 'OPENAI' : 'SYSTEM ERROR'}
              </div>
              <div className={`
                p-3 rounded-xl max-w-[80%] break-words
                ${msg.type === 'user' ? 'bg-blue-500 text-white rounded-br-none' : msg.type === 'openai' ? 'bg-gray-200 text-gray-800 rounded-bl-none' : 'bg-red-100 text-red-800 border border-red-400'}
              `}>
                {msg.text}
              </div>
            </div>
          ))}
          {isSending && ( // แสดง "Typing..." หรือ Loading เมื่อกำลังรอคำตอบ
            <div className="flex flex-col items-start m-3 text-base">
                <div className="font-bold text-sm text-gray-600 mb-1">OPENAI</div>
                <div className="bg-gray-200 text-gray-800 p-3 rounded-xl rounded-bl-none max-w-[80%]">
                    Typing...
                </div>
            </div>
          )}
        </div>

        <div className="p-4 bg-gray-50 border-t border-gray-200 flex items-center space-x-3">
          <input
            type="text"
            className="flex-grow p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder={isSending ? "กำลังรอคำตอบ..." : "พิมพ์ข้อความของคุณ..."} // เปลี่ยน placeholder เมื่อกำลังส่ง
            value={newMessage}
            onChange={handleInputChange}
            onKeyDown={handleKeyPress}
            disabled={isSending} // <--- ปิดการใช้งาน input เมื่อกำลังส่ง
          />
          <button
            onClick={handleSendMessage}
            className="px-6 py-3 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200"
            disabled={isSending} // <--- ปิดการใช้งานปุ่มเมื่อกำลังส่ง
          >
            {isSending ? 'กำลังส่ง...' : 'ส่ง'} {/* เปลี่ยนข้อความปุ่ม */}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;