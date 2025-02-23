"use client";

import React, { useState } from "react";
import Sidebar from "../../components/Sidebar"; // ✅ Import Sidebar

const HistoryPage = () => {
  const [selectedKeyword, setSelectedKeyword] = useState<string | null>(null);
  const [searchHistory, setSearchHistory] = useState<any[]>([]);

  React.useEffect(() => {
    const history = JSON.parse(localStorage.getItem("searchHistory") || "[]");
    setSearchHistory(history);
  }, []);

  return (
    <div className="flex">
      {/* ✅ Sidebar Component */}
      <Sidebar onSelectKeyword={(keyword) => setSelectedKeyword(keyword)} />

      {/* ✅ Main Content */}
      <div className="w-full h-screen flex flex-col items-center bg-white px-6 py-10 overflow-y-auto">
        <h1 className="text-[28px] font-bold text-[#FC4A37] mb-6">🔍 검색 기록</h1>

        {/* ✅ Show Restaurants for Selected Keyword */}
        {selectedKeyword && (
          <div className="w-full max-w-[400px]">
            <h2 className="text-[20px] font-bold text-[#FC4A37] mb-2">🔎 "{selectedKeyword}" 검색 결과</h2>
            {searchHistory
              .find((entry) => entry.keyword === selectedKeyword)
              ?.results.map((restaurant, index) => (
                <div key={index} className="flex flex-col bg-gray-100 rounded-xl shadow-md overflow-hidden mb-6">
                  {/* ✅ Restaurant Image */}
                  <img
                    src={Array.isArray(restaurant.imageUrls) ? restaurant.imageUrls[0] : "/images/default.jpg"}
                    alt={restaurant.name}
                    className="w-full h-[200px] object-cover"
                  />

                  {/* ✅ Content Box */}
                  <div className="p-4">
                    <div className="flex items-end">
                      <h2 className="text-[20px] font-bold text-[#FC4A37] font-ibm tracking-[0.6px]">
                        <span className="mr-2">{index + 1}.</span> {restaurant.name}
                      </h2>
                      {restaurant.distance && (
                        <div className="ml-2 pb-[2px]">
                          <p className="text-[14px] font-normal text-[#6F6F6F] font-['IBM Plex Sans KR'] tracking-[0.5px]">
                            🚶 {restaurant.distance}
                          </p>
                        </div>
                      )}
                    </div>
                    <p className="text-[16px] font-normal text-black mt-2">{restaurant.description}</p>
                    {restaurant.menu && restaurant.menu.length > 0 && (
                      <p className="text-black font-bold mt-2 flex items-center">
                        🍽️ <span className="ml-1">메뉴:</span>
                        <span className="font-normal ml-1">
                          {restaurant.menu[0][0]} ({restaurant.menu[0][1].toLocaleString()}원)
                        </span>
                      </p>
                    )}
                  </div>
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoryPage;
