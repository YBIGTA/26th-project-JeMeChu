"use client";

import React, { useEffect, useState } from "react";

const RecommendationsPage = () => {
  const [recommendedRestaurants, setRecommendedRestaurants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setRecommendedRestaurants([
        {
          name: "탭샵바 합정점",
          distance: "250m",
          menu: "루꼴라치즈떡볶이 (9,000원)",
          description: "다양한 요리를 자유롭게 선택하며 분위기 좋은 공간에서 즐길 수 있는 곳!",
          imageUrl: "/images/sample1.jpg",
          naverLink: "https://map.naver.com/",
        },
        {
          name: "육전국밥 홍대점",
          distance: "250m",
          menu: "수육고기국밥 (15,000원)",
          description: "고소하고 깊은 국물과 함께 든든한 한 끼를 즐길 수 있는 홍대 맛집!",
          imageUrl: "/images/sample2.jpg",
          naverLink: "https://map.naver.com/",
        },
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  return (
    <div className="w-screen h-screen flex flex-col items-center bg-white px-6 py-10 overflow-y-auto">
      {/* ✅ Title with Shadow Effect */}
      <h1 className="text-[32px] font-bold text-black font-['IBM Plex Sans KR'] leading-normal drop-shadow-[0px_4px_4px_rgba(0,0,0,0.25)]">
        오늘의 식당{" "}
        <span className="text-[33px] text-[#FC4A37] drop-shadow-[0px_4px_4px_rgba(0,0,0,0.1)]">TOP 5</span>
      </h1>

      {/* Loading Indicator */}
      {loading && <p className="text-gray-500">로딩 중...</p>}

      {/* Restaurant List */}
      <div className="flex flex-col w-full max-w-[400px]">
        {recommendedRestaurants.map((restaurant, index) => (
          <div
            key={index}
            className="relative flex flex-col p-4 mb-6 bg-gray-100 rounded-xl shadow-md"
          >
            {/* Rank Badge */}
            <div className="absolute -left-5 top-2 bg-[#FC4A37] text-white text-sm font-bold w-[35px] h-[35px] flex items-center justify-center rounded-full">
              {index + 1}
            </div>

            {/* ✅ Restaurant Name Styled to Match Figma */}
            <h2 className="text-[24px] font-bold text-[#FC4A37] font-['IBM Plex Sans KR'] tracking-[0.48px]">
              {restaurant.name}
            </h2>

            <p className="text-gray-500 text-sm">나와의 거리 {restaurant.distance}</p>
            <p className="text-black font-medium mt-1">{restaurant.menu}</p>
            <p className="text-[#FC4A37] text-sm mt-1">{restaurant.description}</p>

            {/* Image */}
            <img
              src={restaurant.imageUrl}
              alt={restaurant.name}
              className="w-full h-auto mt-4 rounded-lg"
            />

            {/* Naver Link */}
            <a
              href={restaurant.naverLink}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#259645] font-medium mt-2 block"
            >
              Naver 지도에서 확인하기
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationsPage;
