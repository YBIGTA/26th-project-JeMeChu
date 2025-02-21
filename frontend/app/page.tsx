"use client"; // 클라이언트 컴포넌트 선언

import React, { useState, useEffect } from "react";
import { FaSearch } from "react-icons/fa";

const Home = () => {
  const headerText = "머뭇거리지 말고 머무거로 맛집을 찾아보세요!";
  const [displayHeader, setDisplayHeader] = useState(" ");
  const [headerIndex, setHeaderIndex] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [isChecked, setIsChecked] = useState(false);
  const [query, setQuery] = useState("");

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

  // 버튼 클릭 시 상태 변경 함수
  const handleCategoryClick = (category) => {
    setSelectedCategory((prev) => (prev === category ? null : category)); // 동일한 버튼 누르면 취소
  };

  // 입력된 query를 백엔드로 보내는 함수
  const handleSearch = async () => {
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          selectedCategory,
          isChecked,
        }),
      });

      // 응답을 텍스트로 먼저 확인
      const text = await response.text();
      console.log('Response text:', text);

      // 만약 응답이 JSON이라면, 그 후에 JSON으로 변환
      const data = JSON.parse(text); // JSON으로 변환
      console.log(data);

    } catch (error) {
      console.error('Error sending query:', error);
    }
  };

  return (
    <div className="w-screen h-screen flex flex-col items-center justify-between bg-white px-6 py-10">
      {/* 상단 텍스트 */}
      <div className="text-center">
        <h1 className="text-[#F8522A] font-['IBM_Plex_Sans_KR'] text-[48px] font-bold leading-normal tracking-[1.8px]">
          머무거
        </h1>
        <p className="text-orange-500 mt-2">{displayHeader}</p> {/* 타이핑 효과 적용 */}
      </div>

      {/* ✅ 카테고리 선택 박스 (체크박스 포함) */}
      <div className="w-[350px] h-[250px] bg-white border-[2.5px] border-black/25 rounded-[20px] shadow-[0px_4px_4px_rgba(0,0,0,0.25)] p-[20px] flex flex-col items-center">
        <h2 className="text-[#F3623F] font-['IBM_Plex_Sans_KR'] text-[25px] font-semibold tracking-[0.5px] text-center">
          카테고리
        </h2>

        {/* 버튼 리스트 */}
        <div className="grid grid-cols-3 gap-x-[22px] gap-y-[15px] justify-center mt-[20px]">
          {["한식", "중식", "일식", "양식", "주점", "기타"].map((category) => (
            <button
              key={category}
              onClick={() => handleCategoryClick(category)}
              className={`w-[76px] h-[42px] flex items-center justify-center border border-[#6F6F6F] rounded-full font-['Roboto'] text-[19px] font-bold leading-normal transition-all 
              ${
                selectedCategory === category
                  ? "bg-[#F3623F] text-white" // Pressed 상태
                  : "text-[#CFA39E] bg-white hover:bg-gray-100" // Default 및 Hover 상태
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      

        {/* ✅ 체크박스 & 텍스트 - 카테고리 박스 안에 위치 */}

        <div className="flex items-center gap-[8.7px] mt-[20px]">
          {/* 체크박스 */}
          <div 
            className={`w-[20px] h-[20px] flex items-center justify-center rounded-sm border-[1px] border-[#F8522A] cursor-pointer
              ${isChecked ? "bg-[#F3623F]" : "bg-white"}`} 
            onClick={() => setIsChecked(!isChecked)} // 체크박스 클릭 시 상태 변경
          >
            {isChecked && (
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
          <p className="text-[#F3623F]/70 font-['Roboto'] text-[15px] font-bold leading-normal">
            아무거나 괜찮으면 여기에 체크!
          </p>
        </div>
      </div>

      {/* 검색창 */}
      <div className="w-[371.159px] h-[49.879px] flex items-center border border-[#6F6F6F] bg-[rgba(230,230,230,0.82)] rounded-[40px] px-4 mt-6">
        <input
          type="text"
          placeholder="ex. 조용하고 주차장이 있는 곳 추천해줘"
          className="flex-1 bg-transparent outline-none text-gray-600 px-2 focus:ring-2 focus:ring-[#F3623F] focus:ring-offset-2 rounded-lg"
          value={query} 
          onChange={(e) => setQuery(e.target.value)} // 타이핑 시 query 상태 업데이트
        
        />
        <button
          className="w-[30px] h-[30px] flex items-center justify-center rounded-full bg-[#FC4A37]"
          onClick={handleSearch} // 검색 버튼 클릭 시 검색 함수 실행>
        >
          <FaSearch className="text-white text-[14px]" />
        </button>
      </div>

      {/* 하단 문구 */}
      <p className="text-[#6F6F6F] text-[16px] font-['Noto_Sans_KR'] font-medium leading-[19px] mt-[10px]">
        오늘도 맛있는 하루 되세요!
      </p>
    </div>
  );
};

export default Home;
