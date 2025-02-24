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
      <div className="fixed inset-0 bg-black opacity-30" onClick={onClose}></div>
      <div className="fixed left-0 top-0 h-full w-80 bg-white p-6 shadow-lg transition-transform duration-300 ease-in-out z-[10000]">
        <button className="absolute top-4 right-4 text-gray-600 text-xl" onClick={onClose}>
          ✖
        </button>
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
                {/* 해당 검색어 클릭 시 추천 식당 목록 표시 */}
                {openKeyword === entry.keyword && (
                  <div className="mt-2 border-t border-gray-300 pt-2">
                    {entry.results.map((restaurant, idx) => (
                      <button
                        key={idx}
                        className="w-full text-left text-blue-600 hover:underline px-2 py-1 transition"
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
