"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import Sidebar from "../../components/Sidebar"
import { highlightCore } from "../utils/highlightCore";

//import { parseRestaurantData } from "../utils/parseRestaurantData";
const RecommendationsPage = () => {
  const [recommendedRestaurants, setRecommendedRestaurants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRestaurant, setSelectedRestaurant] = useState<any>(null); // 🔥 Selected restaurant for popup
  const [searchHistory, setSearchHistory] = useState<any[]>([]);
  const router = useRouter();
  const [selectedKeyword, setSelectedKeyword] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

  const API_URL = process.env.NEXT_PUBLIC_API; // 환경 변수에서 API 주소 가져오기

  useEffect(() => {
    // 🔥 검색 기록을 로컬스토리지에서 불러오기
    const history = JSON.parse(localStorage.getItem("searchHistory") || "[]");
    console.log("Loaded search history from localStorage:", history); // ✅ Debugging log
    if (Array.isArray(history)) {
      setSearchHistory(history);
      // 이미 파싱된 상태라고 가정 -> 바로 첫 번째 항목을 추천 리스트로 사용
      if (Array.isArray(history[0].results)) {
        setRecommendedRestaurants(history[0].results);
      }
    }
    setLoading(false);
      
  }, []);


  // 🔥 Open Popup Function
  const openPopup = (restaurant: any) => {
    setSelectedRestaurant(restaurant);
  };

  // 🔥 Close Popup Function
  const closePopup = () => {
    setSelectedRestaurant(null);
  };
  // 🔥 키워드를 클릭하면 해당 검색 결과를 로드
  const handleSelectKeyword = (keyword: string) => {
    console.log("Clicked keyword:", keyword);
  
    const selectedEntry = searchHistory.find((entry) => entry.keyword === keyword);
    console.log("Selected Entry:", selectedEntry);

    if (!selectedEntry || !Array.isArray(selectedEntry.results) || selectedEntry.results.length !== 3) {
      console.warn("No valid results found for keyword:", keyword);
      setRecommendedRestaurants([]); // ✅ Prevents crash by setting empty array
      return;
    }

    // ✅ Toggle logic: If same keyword is clicked, hide results; otherwise, show them
    if (selectedKeyword === keyword) {
      setSelectedKeyword(""); // Unselect the keyword
      setRecommendedRestaurants([]);
    } else {
      setSelectedKeyword(keyword);
      setRecommendedRestaurants(selectedEntry.results);
    }
  
    console.log("Loaded search results:", selectedEntry.results);
    setRecommendedRestaurants(selectedEntry.results);
  };
  
  const handleRestaurantClick = (restaurant: any) => {
    if (restaurant.connect_url && typeof restaurant.connect_url === "string" && restaurant.connect_url.trim()) {
      window.open(restaurant.connect_url, "_blank");
    } else {
      console.warn("해당 식당의 URL 정보가 없습니다:", restaurant.name);
    }
  };
  

  
  return (
    <div className="relative w-screen h-screen flex bg-white">
      {/* ✅ Sidebar - 검색 기록 */}
      <div className="absolute z-[9999]">
        {sidebarOpen && (
          <Sidebar 
            isOpen={sidebarOpen} 
            onClose={() => setSidebarOpen(false)} // ✅ ❌ 버튼 클릭 시 닫힘
            onSelectKeyword={handleSelectKeyword} 
            onRestaurantClick={handleRestaurantClick}
            searchHistory={searchHistory} 
            selectedKeyword={selectedKeyword}
          />
        )}
      </div>
    
      <div className="w-screen h-screen flex flex-col items-center bg-white px-6 py-10 overflow-y-auto">
        {/* ✅ Sidebar Button (Top Left) */}
        <button
            className="absolute left-6 top-6 bg-gray-200 p-2 rounded-full shadow-md hover:bg-gray-300 transition"
            onClick={() => setSidebarOpen(!sidebarOpen)} // ✅ Sidebar 열고 닫기
        >
          📜 history
        </button>
      
        <div className="mt-10 mb-12">
          <img src="https://i.imgur.com/JRHrkHB.png" alt="로고" width={267} height={46.763} />
        </div>

        {loading ? (
          <p className="text-gray-500">로딩 중...</p>
        ) : recommendedRestaurants.length > 0 ? (
          // {/* ✅ Restaurant List */}
          <div className="flex flex-col w-full max-w-[400px]">
            
            {(recommendedRestaurants || []).map((restaurant, index) => (
              <div key={index} className="flex flex-col bg-gray-100 rounded-xl shadow-md overflow-hidden mb-10">
                {/* ✅ Restaurant Image */}
                <img
                  src={
                    restaurant.photo_url && restaurant.photo_url[0] && Array.isArray(restaurant.photo_url)
                      ? restaurant.photo_url[0]
                      : "https://i.imgur.com/zAzV9Db.png"
                  }
                  alt={restaurant.name}
                  className="w-full h-[200px] object-cover"
                />
                {/* ✅ Content Box (Text) */}
                <div className="p-4">
                  {/* ✅ Rank Number + Restaurant Name + Distance */}
                  <div className="flex items-end">
                    <h2
                      className="text-[20px] font-bold text-[#FC4A37] font-gmarket cursor-pointer"
                      onClick={() => openPopup(restaurant)}
                    >
                      <span className="mr-2">{index + 1}.</span> {restaurant.name}
                    </h2>

                    {/* ✅ Distance (Aligned to Bottom) */}
                    {restaurant.distance && (
                      <div className="ml-2 pb-[2px]">
                        <p className="text-[14px] font-normal text-[#6F6F6F] font-gmarket ">
                          {restaurant.distance}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* ✅ Reason */}
                  <p className="text-[16px] font-light text-black mt-2">
                    {highlightCore(restaurant.reason, restaurant.core)}
                  </p>

                  {/* ✅ Menu (First Item) */}
                  {restaurant.menu?.length > 0 && (
                    <p className="text-black font-normal mt-2 flex items-center">
                      🍽️ <span className="ml-1">메뉴:</span>
                      <span className="font-light ml-1">
                        {restaurant.menu[0]?.[0]}
                        {restaurant.menu[0]?.[1] != 0 && (
                          <> ({restaurant.menu[0][1].toLocaleString()}원)</>
                        )}
                      </span>
                    </p>
                  )}
                </div>
              </div>

            ))}
          </div>
        ) : (
          <p className="text-gray-500">검색 결과가 없습니다.</p>
        )}
      </div>



      {/* ✅ Popup (Modal) */}
      {selectedRestaurant && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-lg w-full relative">
      
          {/* ✅ Close Button (Top Right) */}
            <button
              className="absolute top-4 right-4 text-gray-600 text-2xl"
              onClick={closePopup}
            >
              ✖
            </button>

          {/* ✅ Restaurant Name (Centered) */}
          <h2 className="text-[26px] font-bold text-[#FC4A37] font-gmarket text-center mb-4">
            {selectedRestaurant.name}
          </h2>

          {/* ✅ Multiple Images in Popup */}
          <div className="flex gap-2 overflow-x-auto">
            {selectedRestaurant.photo_url?.map((img: string, idx: number) => (
              <img
                key={idx}
                src={img}
                alt={`Image ${idx + 1}`}
                className="w-1/3 h-auto rounded-lg object-cover"
              />
            ))}
          </div>

          {/* ✅ Full Description */}
          <p className="text-[16px] font-normal text-black text-center mt-2 mb-4">
            {selectedRestaurant.reason}
          </p>
                
          {/* ✅ Full Menu (Show up to 3 items) */}
          {selectedRestaurant?.menu?.length > 0 && (
            <p className="text-gray-600 text-sm mb-2">
              🍽️ <b>메뉴:</b>{" "}
              {selectedRestaurant.menu
                .slice(0, 5) // 🔥 Show only the first 3 menu items
                .map((item: any) => 
                  item[1] != 0 
                    ? `${item[0]} (${item[1].toLocaleString()}원)` 
                    : `${item[0]}`
                )
                .join(", ")}
            </p>
          )}


          {/* ✅ Business Hours */}
          {selectedRestaurant.business_hours && (
            <p className="text-gray-600 text-sm mb-2">
              ⏰ <b>영업시간:</b> {selectedRestaurant.business_hours}
            </p>
          )}

          {/* ✅ Facilities */}
          {selectedRestaurant.facilities.length > 0 && (
            <p className="text-gray-600 text-sm mb-2">
              🏢 <b>시설:</b> {selectedRestaurant.facilities.join(", ")}
            </p>
          )}

          {/* ✅ Parking Info */}
          {selectedRestaurant.parking && (
            <p className="text-gray-600 text-sm">
              🚗 <b>주차:</b> {selectedRestaurant.parking}
            </p>
          )}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationsPage;

