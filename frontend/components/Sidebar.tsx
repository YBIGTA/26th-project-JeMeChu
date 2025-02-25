import React, { useState, useEffect } from "react";
import { X, Search, ChevronRight } from "lucide-react"; // 닫기 버튼 아이콘

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

  const [shouldRender, setShouldRender] = useState(isOpen);
  const [animationClass, setAnimationClass] = useState("-translate-x-full opacity-0 invisible");

  // ✅ 상태 변경 시 렌더링 타이밍 조정 (애니메이션 효과 보장)
  useEffect(() => {
    if (isOpen) {
      setShouldRender(true);
      setTimeout(() => setAnimationClass("translate-x-0 opacity-100 visible"), 10); // 🔥 10ms 딜레이 후 애니메이션 적용
  
    } else {
      setAnimationClass("-translate-x-full opacity-0 invisible");
      setTimeout(() => setShouldRender(false), 300); // 애니메이션 지속 시간만큼 딜레이 후 제거
    }
  }, [isOpen]);

  if (!shouldRender) return null; // ✅ 완전히 닫힌 후에만 제거


  const toggleKeyword = (keyword: string) => {
    const newOpen = openKeyword === keyword ? null : keyword;
    setOpenKeyword(newOpen);
    // 선택한 검색어가 바뀌면 부모의 onSelectKeyword 호출 (있다면)
    if (onSelectKeyword) {
      onSelectKeyword(keyword);
    }
  };


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
        className={`fixed top-0 left-0 h-full w-80 bg-white p-6 shadow-xl 
          transition-all duration-300 ease-in-out z-[10000] ${animationClass}`}  
      >
        {/* 닫기 버튼 */}
        <button className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 transition" onClick={onClose}>
          <X size={24} />
        </button>

        {/* 검색 기록 */}
        <h2 className="text-2xl font-bold font-gmarket mb-4">🔍 History</h2>
        
        {/* 검색 기록 리스트 */}
        <div className="overflow-y-auto max-h-[80vh] pr-2">
          {searchHistory.length === 0 ? (
            <p className="text-gray-500 text-sm mb-4">검색 기록이 없습니다.</p>
          ) : (
            <div className="flex flex-col gap-3">
              {searchHistory.map((entry, index) => (
                <div key={index} className="bg-gray-100 rounded-lg p-1">
                  <button
                    className="w-full text-left font-normal font-gmarket text-black px-3 py-1 rounded-lg hover:scale-105 transition-all"
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
                          className="w-full flex items-center gap-2 text-left text-gmarket text-[#FF6C29] hover:scale-105 px-2 py-1 transition"
                          onClick={() => onRestaurantClick(restaurant)}
                        >
                          <ChevronRight size={18}/> {restaurant.name}
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
    </div>
  );
};

export default Sidebar;
