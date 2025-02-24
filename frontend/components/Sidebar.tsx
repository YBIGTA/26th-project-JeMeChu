import React, { useState } from "react";
import { X } from "lucide-react"; // 닫기 버튼 아이콘

interface HistoryEntry {
  keyword: string;
  results: any[];
}

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  searchHistory: HistoryEntry[];
  onRestaurantClick: (restaurant: any) => void;
  onSelectKeyword?: (keyword: string) => void;
  selectedKeyword?: string | null;
}

const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  searchHistory,
  onRestaurantClick,
  onSelectKeyword,
  selectedKeyword,
}) => {
  const [openKeyword, setOpenKeyword] = useState<string | null>(null);

  const toggleKeyword = (keyword: string) => {
    const newOpen = openKeyword === keyword ? null : keyword;
    setOpenKeyword(newOpen);
    // 선택한 검색어가 바뀌면 부모의 onSelectKeyword 호출 (있다면)
    if (onSelectKeyword) {
      onSelectKeyword(keyword);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex z-[9999]">
      <div
        className={`fixed inset-0 bg-black transition-opacity duration-300 ${
          isOpen ? "opacity-40 visible" : "opacity-0 invisible"
        }`}
        onClick={onClose}
      ></div>
      {/* 사이드바 */}
      <div
        className={`fixed left-0 top-0 h-full w-80 bg-white p-6 shadow-xl rounded-r-xl transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* 닫기 버튼 */}
        <button className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 transition" onClick={onClose}>
          <X size={24} />
        </button>

        {/* 검색 기록 */}
        <h2 className="text-2xl font-bold font-gmarket mb-4">🔍 검색 기록</h2>
        
        {/* 검색 기록 리스트 */}
        {searchHistory.length === 0 ? (
          <p className="text-gray-500 text-sm mb-4">검색 기록이 없습니다.</p>
        ) : (
          <div className="flex flex-col gap-4">
            {searchHistory.map((entry, index) => (
              <div key={index} className="bg-gray-100 rounded-lg p-3">
                <button
                  className="w-full text-left font-normal font-gmarket text-black px-2 py-1 rounded-lg hover:bg-gray-200 transition"
                  onClick={() => toggleKeyword(entry.keyword)}
                >
                  {entry.keyword}
                </button>

                {/* 해당 검색어 클릭 시 추천 식당 목록 표시 */}
                {openKeyword === entry.keyword && (
                  <div className="mt-2 border-t border-gray-300 pt-2">
                    {entry.results.map((restaurant, idx) => (
                      <button
                        key={idx}
                        className="w-full text-left text-gmarket text-[#FF6C29] hover:scale-105 px-2 py-1 transition"
                        onClick={() => onRestaurantClick(restaurant)}
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
