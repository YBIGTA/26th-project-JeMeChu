"use client"; // 클라이언트 컴포넌트 선언

import React, { useState, useEffect, useRef } from "react";
import { FaSearch } from "react-icons/fa";
import { useRouter } from 'next/navigation';
import { parseRestaurantData } from "./utils/parseRestaurantData";
import { ClipLoader } from "react-spinners";

// 연결 url
const API_URL = process.env.NEXT_PUBLIC_API; // 환경 변수에서 API 주소 가져오기

const Home = () => {
  const headerText = "머뭇거리지 말고 머무거로 맛집을 찾아보세요!";
  const [displayHeader, setDisplayHeader] = useState(" ");
  const [headerIndex, setHeaderIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<string>(""); // 카테고리&체크박스스
  const [details, setDetails] = useState("");
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // 상단 문구 타이핑 효과
  useEffect(() => {
    if (headerIndex < headerText.length) {
      const typingInterval = setTimeout(() => {
        setDisplayHeader((prev) => prev + headerText[headerIndex]);
        setHeaderIndex((prev) => prev + 1);
      }, 50); // 50ms 간격

      return () => clearTimeout(typingInterval);
    }
  }, [headerIndex, headerText]);

  // 🔥 Enter 키 입력 처리 함수
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch(); // Enter 키를 누르면 검색 실행
    }
  };

  // 버튼 클릭 시 상태 변경 함수
  const handleCategoryClick = (ctgy: string) => {
    setSelectedOption((prev) => (prev === ctgy ? "" : ctgy)); // 동일한 버튼 누르면 취소
  };

  // 체크박스 클릭 시 상태 변경 함수 (체크박스 선택 시 카테고리 해제)
  const handleCheckboxClick = () => {
    setSelectedOption((prev) => (prev === "아무거나" ? "" : "아무거나"));
  };  

  // 입력된 details를 백엔드로 보내는 함수
  const handleSearch = async () => {
    try {
      setLoading(true);
      // 입력 후 포커스 제거
      if (inputRef.current) {
        inputRef.current.blur();
      }      
      const requestBody = {
        ctgy: selectedOption || "아무거나",
        details,
         // ✅ 체크박스 OR 카테고리 값 (하나만 전송)
      };

      console.log("📢 검색 요청 데이터:", requestBody);
      console.log("🚀 API_URL:", API_URL); // 터미널에서 값 확인

      const response = await fetch(`${API_URL}/filter_restaurants/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const responseData = await response.json();
      console.log("🚀 검색 요청 결과:", responseData);
      
      const parsedResults = responseData.map((restaurant: any) =>
        parseRestaurantData(restaurant)
      );

      // ✅ 기존 검색 기록 불러오기
      const previousHistory = JSON.parse(localStorage.getItem("searchHistory") || "[]");

      // ✅ 새 검색 기록 추가
      const newEntry = { keyword: details, results: parsedResults };
      const updatedHistory = [newEntry, ...previousHistory].slice(0, 10); // 최근 10개 기록 유지

      // ✅ 검색 기록을 로컬 스토리지에 저장
      localStorage.setItem("searchHistory", JSON.stringify(updatedHistory));

  
      router.push('/recommendations'); // Navigate to recommendations page      


    } catch (error) {
      console.error('Error sending details:', error);
    }


  };

  return (
    <div className="w-screen h-screen flex flex-col items-center justify-between bg-[#E7E7E7] bg-opacity-50 px-6 py-10">
      {/* 상단 텍스트 */}
      <div className="flex flex-col items-center justify-center text-center">
        <div className="mt-10 mb-3">
          <img src="https://i.imgur.com/JRHrkHB.png" alt="로고" width={325.35} height={57} />
        </div>
        <p className="text-orange-500 mt-2 font-gmarket font-medium" >{displayHeader}</p> {/* 타이핑 효과 적용 */}
      </div>

      {/* ✅ 카테고리 선택 박스 (체크박스 포함) */}
      <div className="w-[350px] h-[380px] bg-white bg-opacity-90 rounded-[20px] shadow-[0px_2px_2px_rgba(0,0,0,0.15)] p-[20px] flex flex-col items-center">
        <h2 className="text-[#FF6C29] font-gmarket text-[23px] font-bold text-center mt-4">
          Category
        </h2>

        {/* 버튼 리스트 */}
        <div className="grid grid-cols-3 gap-x-[22px] gap-y-[15px] justify-center mt-[20px]">
          {["한식", "중식", "일식", "양식", "주점", "기타"].map((ctgy) => (
            <button
              key={ctgy}
              onClick={() => handleCategoryClick(ctgy)}
              className={`w-[76px] h-[42px] flex items-center justify-center border border-[#6F6F6F] rounded-full font-gmarket text-[17.5px] font-medium leading-normal transition-all 
              ${
                selectedOption === ctgy
                  ? "bg-[#FF6C29] text-white" // Pressed 상태
                  : "text-[#9E9E9E] bg-white hover:bg-gray-100" // Default 및 Hover 상태
              }`}
            >
              {ctgy}
            </button>
          ))}
        </div>
      

        {/* ✅ 체크박스 & 텍스트 - 카테고리 박스 안에 위치 */}

        <div className="flex items-center gap-[8.7px] mt-[20px]">
          {/* 체크박스 */}
          <div 
            className={`w-[20px] h-[20px] flex items-center justify-center rounded-sm border-[1px] border-[#6F6F6F] cursor-pointer
              ${selectedOption == "아무거나" ? "bg-[#FF6C29]" : "bg-white"}`} 
            onClick={handleCheckboxClick} // 체크박스 클릭 시 상태 변경
          >
            {selectedOption && (
              <svg xmlns="http://www.w3.org/2000/svg" width="10.76" height="8.37px" viewBox="0 0 14 12" fill="none">
                <path 
                  d="M1.96533 7.1813L5.3807 10.5284L12.7238 2.16071" 
                  stroke="#FFFFFF" 
                  strokeOpacity="0.8" 
                  strokeWidth="2.39px" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
              </svg>
            )}
          </div>

          {/* 텍스트 */}
          <p className="text-[#FF6C29]/70 text-[15px] font-gmarket font-medium leading-normal">
            아무거나 괜찮으면 여기에 체크 !
          </p>
        </div>

        {/* 검색창 */}
        <div className="w-full h-[49.879px] flex items-center border border-[#6F6F6F] bg-[rgba(230,230,230,0.5)] rounded-[40px] px-4 mt-11">
          <input
            ref={inputRef}
            type="text"
            placeholder="ex. 맛있고 주차가 되는 곳 추천해줘"
            className="flex-1 bg-transparent outline-none text-black text-[15px] placeholder:text-sm placeholder:tracking-[0.5px] px-2 focus:ring-2 focus:ring-[#FF6C29] focus:ring-offset-2 rounded-lg"
            value={details} 
            onChange={(e) => setDetails(e.target.value)} // 타이핑 시 details 상태 업데이트
            onKeyDown={handleKeyDown} // Enter 키 입력 시 검색 함수 실행
          />
          <button
            className="w-[30px] h-[30px] flex items-center justify-center rounded-full bg-[#FF6C29]"
            onClick={handleSearch} // 검색 버튼 클릭 시 검색 함수 실행>
            disabled={loading}
          >
            {loading ? (
              <ClipLoader size={16} color="#ffffff" />
            ) : (
              <FaSearch className="text-white text-[14px]" />
            )}
          </button>
        </div>
      </div>



      {/* 하단 문구 */}
      <p className="text-[#5A5A5A] text-[16px] font-gmarket font-medium leading-[19px] mt-[10px]">
        오늘도 맛있는 하루 되세요!
      </p>
    </div>
  );
};

export default Home;