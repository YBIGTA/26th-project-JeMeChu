import React, { useState } from "react";

const Sidebar = ({ isOpen, onClose, searchHistory }) => {
  const [openKeyword, setOpenKeyword] = useState(null); // ✅ 현재 열려 있는 검색 기록

  const toggleKeyword = (keyword) => {
    setOpenKeyword(openKeyword === keyword ? null : keyword);
  };

  if (!isOpen) return null;
  // ✅ 네이버 지도 이동 함수 (현재는 console.log로 대체)
  const handleRestaurantClick = (restaurantName) => {
    const naverMapURL = `https://map.naver.com/?query=${restaurantName}`; // 추후 변경 가능
    console.log(`Navigating to: ${naverMapURL}`);
    // window.open(naverMapURL, "_blank");  // 🚀 네이버 맵 연결되면 이 코드 활성화
  };

  return (
    <div className="fixed inset-0 flex z-[9999]"> {/* ✅ 최상위 z-index 설정 */}
      <div className="fixed inset-0 bg-black opacity-30" onClick={onClose}></div>

      <div className="fixed left-0 top-0 h-full w-80 bg-white p-6 shadow-lg transition-transform duration-300 ease-in-out z-[10000]">
        <button className="absolute top-4 right-4 text-gray-600 text-xl" onClick={onClose}>✖</button>
        <h2 className="text-xl font-bold mb-4">🔍 검색 기록</h2>

        {searchHistory.length === 0 ? (
          <p className="text-gray-500 text-sm mb-4">검색 기록이 없습니다.</p>
        ) : (
          <div className="flex flex-col gap-3">
            {searchHistory.map((entry, index) => (
              <div key={index} className="bg-gray-100 rounded-lg p-3">
                <button
                  className="w-full text-left font-bold text-black px-2 py-1 rounded-lg hover:bg-gray-200 transition"
                  onClick={() => toggleKeyword(entry.keyword)}
                >
                  {entry.keyword}
                </button>

                {/* ✅ 검색어 클릭 시 해당 검색 당시 추천 식당 표시 */}
                {openKeyword === entry.keyword && (
                  <div className="mt-2 border-t border-gray-300 pt-2">
                    {entry.results.map((restaurant, idx) => (
                      <button
                        key={idx}
                        className="w-full text-left text-blue-600 hover:underline px-2 py-1 transition"
                        onClick={() => handleRestaurantClick(restaurant.name)}
                      >
                        {restaurant.name}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
