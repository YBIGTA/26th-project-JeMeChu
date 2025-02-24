"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import Sidebar from "../../components/Sidebar"

const RecommendationsPage = () => {
  const [recommendedRestaurants, setRecommendedRestaurants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRestaurant, setSelectedRestaurant] = useState<any>(null); // 🔥 Selected restaurant for popup
  const [searchHistory, setSearchHistory] = useState<string>("");
  const router = useRouter();
  const [selectedKeyword, setSelectedKeyword] = useState<any[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

  useEffect(() => {
    setTimeout(() => {
      setRecommendedRestaurants([
        {
          name: "탭샵바 합정점",
          distance: "250m",
          menu: [["루꼴라 치즈 떡볶이", 9900]],
          description: "다양한 요리를 자유롭게 선택하며 분위기 좋은 공간에서 즐길 수 있는 곳!",
          business_hours: "매일 11:00 - 24:00",
          facilities: ["와인 페어링", "포장", "예약 가능"],
          parking: "무료 주차 가능",
          imageUrls: ['https://search.pstatic.net/common/?autoRotate=true&type=w560_sharpen&src=https%3A%2F%2Fldb-phinf.pstatic.net%2F20250116_234%2F1736993517599R0Oqc_JPEG%2F%25B1%25D7%25B8%25B22.jpg', 'https://search.pstatic.net/common/?autoRotate=true&type=w278_sharpen&src=https%3A%2F%2Fldb-phinf.pstatic.net%2F20250116_254%2F1736993510471IkD4D_JPEG%2F%25B1%25D7%25B8%25B21.jpg', 'https://search.pstatic.net/common/?autoRotate=true&type=w278_sharpen&src=https%3A%2F%2Fldb-phinf.pstatic.net%2F20250116_205%2F1736993519045YFwkP_JPEG%2F%25B1%25D7%25B8%25B27.jpg'],
        },
        {
          name: "육전국밥 홍대점",
          distance: "50m",
          menu: [["수육고기국밥", 15000]],
          description: "고소하고 깊은 국물과 함께 든든한 한 끼를 즐길 수 있는 홍대 맛집!",
          business_hours: "월-금 10:30 - 21:00",
          facilities: ["무선 인터넷", "혼밥 가능"],
          parking: "없음",
          imageUrls: [],
        },
        {
          name: "연남동 브런치카페",
          distance: "150m",
          menu: [["에그 베네딕트", 18000], ["아보카도 토스트", 16000]],
          description: "여유로운 아침을 위한 최고의 브런치 카페!",
          business_hours: "화-일 08:00 - 16:00",
          facilities: ["테라스", "채식 옵션", "예약 가능"],
          parking: "인근 공용 주차장 이용 가능",
          imageUrls: ['https://search.pstatic.net/common/?autoRotate=true&type=w560_sharpen&src=https%3A%2F%2Fldb-phinf.pstatic.net%2F20200214_51%2F158166848954983lgB_JPEG%2F7LjX4ZBKQYA5cY-hxdDjxKUd.jpg', 'https://search.pstatic.net/common/?autoRotate=true&type=w278_sharpen&src=https%3A%2F%2Fldb-phinf.pstatic.net%2F20200214_111%2F15816684696149Iuwa_JPEG%2F_VSYAFAHDGNlhac8Qgie4op3.jpg', 'https://search.pstatic.net/common/?autoRotate=true&type=w278_sharpen&src=https%3A%2F%2Fldb-phinf.pstatic.net%2F20200214_179%2F15816684694822Pjzo_JPEG%2F_gwbOUEIxQJeBVwvHY2kRusk.jpg']
          ,
        },
        {
          name: "마라탕전문점 홍대점",
          distance: "300m",
          menu: [["마라탕 (소)", 12000], ["마라샹궈", 25000]],
          description: "얼얼한 마라의 매운맛을 제대로 즐길 수 있는 곳!",
          business_hours: "매일 11:30 - 23:00",
          facilities: ["단체석", "무선 인터넷", "포장 가능"],
          parking: "주차 불가",
          imageUrls: ['https://search.pstatic.net/common/?autoRotate=true&type=w560_sharpen&src=https%3A%2F%2Fpup-review-phinf.pstatic.net%2FMjAyMjA3MTNfNzQg%2FMDAxNjU3Njg5NDQ5NTMx.Q0i7yEHSR95XPYL3uhB2bWx7w41z4GnwR3xLUjwf9eAg.DsDeQR98UfemqUfNnvS2phF0NGYrsF7hYZ7tNHmD_usg.JPEG%2Fupload_cba91c14b2d0fd5b61a262f8a67df690.jpeg', 'https://search.pstatic.net/common/?autoRotate=true&type=w278_sharpen&src=https%3A%2F%2Fpup-review-phinf.pstatic.net%2FMjAyMjA4MjhfMjE2%2FMDAxNjYxNjYzMDEyNDk0.FC94z3fBtTzeILAPdQ6H9tdYXTpBAscnZl_Oz4AoLp0g.onXWRUgl3sEgd--DrarwZuBHRb787FoMDrIxRlJEl-og.JPEG%2FC4CCB4B6-94E7-4208-AC04-DB004062F93C.jpeg', 'https://search.pstatic.net/common/?autoRotate=true&type=w278_sharpen&src=https%3A%2F%2Fpup-review-phinf.pstatic.net%2FMjAyMjA5MTFfMjEw%2FMDAxNjYyOTAyMjMyNzYw.PEt9nTTXWjW5m7HXRhklNZc7Hmjjt8WacEE15lLJJWsg.FsnbdFY1Lm75u8Dee8GuBPhTZFCibpu6QyX_2BkOPwcg.JPEG%2F296B949A-BDB8-4573-BDFD-2CC3EB361D53.jpeg']
          ,
        },
        {
          name: "신촌 수제버거 맛집",
          distance: "500m",
          menu: [["더블 치즈버거", 12000], ["감자튀김", 5000]],
          description: "수제 패티의 깊은 맛을 느낄 수 있는 수제버거 전문점!",
          business_hours: "월-토 11:00 - 22:00, 일 휴무",
          facilities: ["반려동물 동반 가능", "테이크아웃 가능"],
          parking: "인근 공용 주차장 이용 가능",
          imageUrls: ['https://search.pstatic.net/common/?autoRotate=true&type=w560_sharpen&src=https%3A%2F%2Fldb-phinf.pstatic.net%2F20220817_125%2F1660741016108Bw9aN_JPEG%2F193A88C5-1209-46DD-8BBC-160804F9FAC9.jpeg', 'https://search.pstatic.net/common/?autoRotate=true&type=w278_sharpen&src=https%3A%2F%2Fldb-phinf.pstatic.net%2F20220817_38%2F1660741017049vEFNr_JPEG%2F4ED6F6FD-870A-4DA4-9199-06105656783C.jpeg', 'https://search.pstatic.net/common/?autoRotate=true&type=w278_sharpen&src=https%3A%2F%2Fldb-phinf.pstatic.net%2F20220817_154%2F1660741015571LbPPM_JPEG%2F28D8FAE3-1E36-46A3-B5C2-FD81072A7A77.jpeg']
          ,
        },
      ]);
      setLoading(false);
    }, 1000);
    // 🔥 검색 기록을 로컬스토리지에서 불러오기
    const history = JSON.parse(localStorage.getItem("searchHistory") || "[]");
    console.log("Loaded search history from localStorage:", history); // ✅ Debugging log
    if (Array.isArray(history)) {
      setSearchHistory(history);
    }
    // ✅ 가장 최근 검색어 가져오기
    if (history.length > 0) {
      const latestQuery = history[0].keyword;

      // ✅ 백엔드에 요청 (현재는 Mock 데이터 사용)
      fetch(`/api/search?query=${latestQuery}`)
        .then((res) => res.json())
        .then((data) => {
          console.log("Fetched recommendations:", data);

          // ✅ 응답이 정상적인지 확인 후 저장
          if (Array.isArray(data) && data.length === 5) {
            setRecommendedRestaurants(data);

            // ✅ 검색 기록 업데이트 (결과 저장)
            const updatedHistory = history.map((entry) =>
              entry.keyword === latestQuery ? { ...entry, results: data } : entry
            );

            localStorage.setItem("searchHistory", JSON.stringify(updatedHistory));
          }
        })
        .catch((error) => {
          console.error("Error fetching recommendations:", error);
        });
    }    
      
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

    if (!selectedEntry || !Array.isArray(selectedEntry.results) || selectedEntry.results.length !== 5) {
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
  
    // setSelectedKeyword(keyword);
    //   // ✅ undefined 체크 및 기본값 설정
    // const parsedResults = Array.isArray(selectedEntry.results) ? selectedEntry.results : [];

    // console.log("Loaded search results:", parsedResults);
  
    // setRecommendedRestaurants(parsedResults);
    console.log("Loaded search results:", selectedEntry.results);
    setRecommendedRestaurants(selectedEntry.results);
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
          📜history
        </button>
      
        {/* ✅ Title with Shadow Effect */}
        <h1 className="text-[32px] font-bold text-black font-ibm leading-normal drop-shadow-[0px_4px_4px_rgba(0,0,0,0.25)] mb-9 tracking-[0.7px]">
          오늘의 식당{" "}
          <span className="text-[35px] text-[#FC4A37] drop-shadow-[0px_4px_4px_rgba(0,0,0,0.05)]">TOP 5</span>
        </h1>

        {/* ✅ Loading Indicator */}
        {loading && <p className="text-gray-500">로딩 중...</p>}

        {/* ✅ Restaurant List */}
        <div className="flex flex-col w-full max-w-[400px]">
          
          {(recommendedRestaurants || []).map((restaurant, index) => (
            <div key={index} className="flex flex-col bg-gray-100 rounded-xl shadow-md overflow-hidden mb-6">
              {/* ✅ Restaurant Image */}
              <img
                src={restaurant.imageUrls?.[0] || "https://i.imgur.com/zAzV9Db.png"} // 🔥 Use first image, fallback to default
                alt={restaurant.name}
                className="w-full h-[200px] object-cover"
              />
              {/* ✅ Content Box (Text) */}
              <div className="p-4">
                {/* ✅ Rank Number + Restaurant Name + Distance */}
                <div className="flex items-end">
                  <h2
                    className="text-[20px] font-bold text-[#FC4A37] font-ibm tracking-[0.6px] cursor-pointer"
                    onClick={() => openPopup(restaurant)}
                  >
                    <span className="mr-2">{index + 1}.</span> {restaurant.name}
                  </h2>

                  {/* ✅ Distance (Aligned to Bottom) */}
                  {restaurant.distance && (
                    <div className="ml-2 pb-[2px]">
                      <p className="text-[14px] font-normal text-[#6F6F6F] font-['IBM Plex Sans KR'] tracking-[0.5px]">
                        {restaurant.distance}
                      </p>
                    </div>
                  )}
                </div>

                {/* ✅ Description */}
                <p className="text-[16px] font-normal text-black mt-2">{restaurant.description}</p>

                {/* ✅ Menu (First Item) */}
                {restaurant?.menu?.length > 0 && (
                  <p className="text-black font-bold mt-2 flex items-center">
                    🍽️ <span className="ml-1">메뉴:</span>
                    <span className="font-normal ml-1">
                      {restaurant.menu[0]?.[0]} ({restaurant.menu[0]?.[1]?.toLocaleString()}원)
                    </span>
                  </p>
                )}
              </div>
            </div>

          ))}
        </div>
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
          <h2 className="text-[26px] font-bold text-[#FC4A37] font-ibm text-center mb-4">
            {selectedRestaurant.name}
          </h2>

          {/* ✅ Multiple Images in Popup */}
          <div className="flex gap-2 overflow-x-auto">
            {selectedRestaurant.imageUrls?.map((img: string, idx: number) => (
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
            {selectedRestaurant.description}
          </p>
                
          {/* ✅ Full Menu (Show up to 3 items) */}
          {selectedRestaurant?.menu?.length > 0 && (
            <p className="text-gray-600 text-sm mb-2">
              🍽️ <b>메뉴:</b>{" "}
              {selectedRestaurant.menu
                .slice(0, 5) // 🔥 Show only the first 3 menu items
                .map((item: any) => `${item[0]} (${item[1].toLocaleString()}원)`)
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

