"use client";

import React, { useEffect, useState } from "react";
import Sidebar from "../../components/Sidebar"
import { highlightCore } from "../utils/highlightCore";
import { Restaurant } from "../utils/types";
import { Menu } from "lucide-react";


//import { parseRestaurantData } from "../utils/parseRestaurantData";
const RecommendationsPage = () => {
  const [recommendedRestaurants, setRecommendedRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRestaurant, setSelectedRestaurant] = useState<Restaurant | null>(null);
  const [searchHistory, setSearchHistory] = useState<{ keyword: string; results: Restaurant[] }[]>([]);
  const [selectedKeyword, setSelectedKeyword] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

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
  const openPopup = (restaurant: Restaurant) => {
    setSelectedRestaurant(restaurant);
  };

  // 🔥 Close Popup Function
  const closePopup = () => {
    setSelectedRestaurant(null);
  };
  // 🔥 키워드를 클릭하면 해당 검색 결과를 로드
  const handleSelectKeyword = (keyword: string) => {
    console.log("Clicked keyword:", keyword);
  
    const selectedEntry = searchHistory.find(
      (entry) => entry.keyword === keyword
    ) as { keyword: string; results: Restaurant[] } | undefined;    
    
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
  
  const handleRestaurantClick = (restaurant: Restaurant) => {
    if (restaurant.connect_url?.trim()) {
      window.open(restaurant.connect_url, "_blank");
    } else {
      console.warn("해당 식당의 URL 정보가 없습니다:", restaurant.name);
    }
  };
    

  
  return (
    <div className="w-screen h-screen flex bg-white">
      {/* ✅ Sidebar - 검색 기록 */}
      <Sidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)} // ✅ ❌ 버튼 클릭 시 닫힘
        onSelectKeyword={handleSelectKeyword} 
        onRestaurantClick={handleRestaurantClick}
        searchHistory={searchHistory} 
        selectedKeyword={selectedKeyword}
      />


    
      <div className="w-screen h-screen flex flex-col items-center bg-white px-6 py-10 overflow-y-auto">
        {/* ✅ Sidebar Button (Top Left) */}
        <button
            className="absolute left-6 top-6 bg-gray-200 p-2 rounded-full shadow-md hover:bg-gray-300 transition"
            onClick={() => setSidebarOpen(!sidebarOpen)} // ✅ Sidebar 열고 닫기
        >
          <Menu size={24} strokeWidth={2} className="text-gray-600" />
        </button>
      
        <div className="mt-10 mb-12">
          <img src="https://i.imgur.com/JRHrkHB.png" alt="로고" width={267} height={46.763} />
        </div>

        {loading ? (
          <p className="text-gray-500">로딩 중...</p>
        ) : recommendedRestaurants.length > 0 ? (
          // {/* ✅ Restaurant List */}
          <div className="w-[340px] flex-col">
            
            {(recommendedRestaurants || []).map((restaurant, index) => {
                // 🔥 카드 클릭 시 팝업을 여는 함수 (이미지 클릭 제외)
                const handleCardClick = (e: React.MouseEvent<HTMLDivElement>) => {
                  // 이미지 클릭일 경우, 이벤트를 차단해서 팝업 안 뜨게 함
                  if ((e.target as HTMLElement).tagName === "IMG") {
                    e.stopPropagation();
                    return;
                  }
                  openPopup(restaurant);
                };

                return (
    
                  <div
                    key={index}
                    className="flex flex-col bg-gray-100 rounded-xl shadow-md overflow-hidden mb-10 cursor-pointer"
                    onClick={handleCardClick}
                  >
                    {/* ✅ Restaurant Image */}
                    <img
                      src={
                        restaurant.photo_url && restaurant.photo_url[0] && Array.isArray(restaurant.photo_url)
                          ? restaurant.photo_url[0]
                          : "https://i.imgur.com/zAzV9Db.png"
                      }
                      alt={restaurant.name}
                      className="w-full h-[200px] object-cover cursor-default"
                      onClick={(e) => e.stopPropagation()} // 이미지 클릭 시 팝업 열리지 않도록 이벤트 전파 차단
                    />
                    {/* ✅ Content Box (Text) */}
                    <div className="p-4">
                      {/* ✅ Rank Number + Restaurant Name + Distance */}
                      <div className="flex items-end">
                        <h2
                          className="text-[23px] font-bold text-[#FC4A37] font-gmarket cursor-pointer"
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
                      {/* ✅ Menu (First Item) */}
                      {restaurant.menu?.length > 0 && (
                        <p className="text-black font-normal mt-2 flex items-center">
                          🍽️ <span className="ml-1">메뉴:</span>
                          <span className="font-medium font-opacity-70 ml-1">
                            {restaurant.menu[0]?.[0]}
                            {restaurant.menu[0]?.[1] != 0 && (
                              <> ({restaurant.menu[0][1].toLocaleString()}원)</>
                            )}
                          </span>
                        </p>
                      )}

                      {/* ✅ Reason */}
                      <p className="text-[16px] font-medium text-black text-opacity-65 mt-2 leading-relaxed">
                        {highlightCore(restaurant.reason ?? "", restaurant.core ?? "")}
                      </p>
                    </div>
                  </div>
                );
              })}
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
          {(Array.isArray(selectedRestaurant.photo_url) ? selectedRestaurant.photo_url : [selectedRestaurant.photo_url])?.map((img: string, idx: number) => (
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
            

          {/* ✅ 메뉴 & 영업시간을 반반 정렬 */}
          <div className="grid grid-cols-2 gap-4">
            {/* ✅ 메뉴 */}
            <div>
              {selectedRestaurant.menu && (
                <div className="text-gray-600 text-sm">
                  <p className="font-bold flex items-center gap-1">
                    🍽️ 메뉴:
                  </p>
                  <div className="mt-1 pl-4 border-l-2 border-gray-300">
                  {(Array.isArray(selectedRestaurant.menu) ? selectedRestaurant.menu : []).slice(0, 8).map((item: [string, number], index: number) => (
                      <p key={index}>
                        <span className="font-medium">{item[0]}</span>
                        {item[1] !== 0 && ` (${item[1].toLocaleString()}원)`}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* ✅ 영업시간 */}
            <div>
              {selectedRestaurant.business_hours && (
                <div className="text-gray-600 text-sm">
                  <p className="font-bold flex items-center gap-1">
                    ⏰ 영업시간:
                  </p>
                  <div className="mt-1 pl-4 border-l-2 border-gray-300">
                    {selectedRestaurant.business_hours !== "정보 없음"
                      ? selectedRestaurant.business_hours.split("; ").map((hour, index) => {
                          const [day, time] = hour.split(": ");
                          return (
                            <p key={index} className="mb-1">
                              <span className="font-bold">{day}</span>: {time}
                            </p>
                          );
                        })
                      : "정보 없음"}
                  </div>
                </div>
              )}
            </div>
          </div>


          {/* ✅ 기타 정보 (시설, 주차, 전화번호) */}
          <div className="mt-4 space-y-2 text-gray-600 text-sm">
            {/* ✅ 시설 */}
            <p>
              🏢 <b>시설: </b> 
              {Array.isArray(selectedRestaurant.facilities) ? selectedRestaurant.facilities.join(", ") : "정보 없음"}
            </p>
              
            {/* ✅ 전화번호 */}
            <p>
              📞 <b>전화: </b> 
              {selectedRestaurant.phone 
                ? selectedRestaurant.phone 
                : "정보 없음"}
            </p>
              

            {/* ✅ 주차 정보 */}
            {selectedRestaurant.parking !== undefined && selectedRestaurant.parking !== null && (
              <p className="text-gray-600 text-sm">
                🚗 <b>주차:</b> {!selectedRestaurant.parking || selectedRestaurant.parking.trim() === "NaN" ? "정보 없음" : selectedRestaurant.parking}
              </p>
            )}

            {/* ✅ 좌석 정보 */}
            <p>
              💺 <b>좌석 정보: </b> 
              {Array.isArray(selectedRestaurant.seat_info) ? selectedRestaurant.seat_info.join(", ") : "정보 없음"}
            </p>


          </div>

          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationsPage;

