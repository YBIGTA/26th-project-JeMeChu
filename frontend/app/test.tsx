"use client"; // Next.js 13 이상 클라이언트 컴포넌트 사용
import React, { useState } from "react";
const API_URL = "http://192.168.56.1:8000/test"; // :흰색_확인_표시: FastAPI 서버 주소
const TestPage = () => {
    const [responseMessage, setResponseMessage] = useState<string | null>(null);
    // :흰색_확인_표시: FastAPI로 POST 요청을 보내는 함수
    const handleTestRequest = async () => {
        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: "프론트엔드에서 보낸 테스트 메시지" }),
            });
            if (!response.ok) {
                throw new Error("서버 응답 실패!");
            }
            const data = await response.json();
            console.log(":확성기: 응답 데이터:", data);
            setResponseMessage(data.received_message); // :흰색_확인_표시: 응답 메시지 상태 업데이트
        } catch (error) {
            console.error(":경고: 오류 발생:", error);
            setResponseMessage("FastAPI 연결 실패! 서버 상태를 확인하세요.");
        }
    };
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
            <h1 className="text-2xl font-bold mb-4">:링크: FastAPI 연결 테스트</h1>
            <button
                onClick={handleTestRequest}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg shadow-md hover:bg-blue-600 transition"
            >
                FastAPI 테스트 요청 보내기
            </button>
            {responseMessage && (
                <p className="mt-4 text-lg font-semibold text-gray-800">
                    :작은_파란색_다이아몬드: 응답 메시지: {responseMessage}
                </p>
            )}
        </div>
    );
};
export default TestPage;