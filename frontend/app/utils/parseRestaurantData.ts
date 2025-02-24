// utils/parseRestaurantData.ts
export const parseRestaurantData = (restaurant: any) => {
    // photo_url 파싱
    let parsedPhoto = restaurant.photo_url;
    if (typeof parsedPhoto === "string") {
      try {
        parsedPhoto = JSON.parse(parsedPhoto.replace(/'/g, '"'));
      } catch (err) {
        console.warn("photo_url 파싱 실패:", err);
        parsedPhoto = ["https://i.imgur.com/zAzV9Db.png"];
      }
    }
  
    // menu 파싱
    let parsedMenu = restaurant.menu;
    if (typeof parsedMenu === "string") {
      try {
        parsedMenu = JSON.parse(parsedMenu.replace(/'/g, '"'));
        parsedMenu = parsedMenu.map((item: any) => [
          item[0],
          item[1] == null ? 0 : item[1],
        ]);
      } catch (err) {
        console.warn("menu 파싱 실패:", err);
        parsedMenu = [];
      }
    }
  
    // facilities 파싱
    let parsedFacilities = restaurant.facilities;
    if (typeof parsedFacilities === "string") {
      try {
        parsedFacilities = JSON.parse(parsedFacilities.replace(/'/g, '"'));
      } catch (err) {
        console.warn("facilities 파싱 실패:", err);
        parsedFacilities = [];
      }
    }
  
    // seat_info 파싱
    let parsedSeatInfo = restaurant.seat_info;
    if (typeof parsedSeatInfo === "string") {
      try {
        parsedSeatInfo = JSON.parse(parsedSeatInfo.replace(/'/g, '"'));
      } catch (err) {
        console.warn("seat_info 파싱 실패:", err);
        parsedSeatInfo = [];
      }
    }
  
    // distance 및 business_hours 처리
    const distanceValue = restaurant.distance ?? "정보 없음";
    const hoursValue = restaurant.business_hours === "NaN" ? "정보 없음" : restaurant.business_hours;
  
    return {
      ...restaurant,
      photo_url: parsedPhoto,
      menu: parsedMenu,
      facilities: parsedFacilities,
      seat_info: parsedSeatInfo,
      distance: distanceValue,
      business_hours: hoursValue,
    };
  };
  