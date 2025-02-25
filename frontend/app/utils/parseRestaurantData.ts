import { Restaurant } from "./types"; // ✅ Import the type

export const parseRestaurantData = (restaurant: Partial<Restaurant>): Restaurant => {
  // ✅ Ensure photo_url is always an array
  let parsedPhoto: string[] = [];
  if (typeof restaurant.photo_url === "string") {
    try {
      parsedPhoto = JSON.parse(restaurant.photo_url.replace(/'/g, '"'));
    } catch (err) {
      console.warn("photo_url 파싱 실패:", err);
      parsedPhoto = ["https://i.imgur.com/zAzV9Db.png"];
    }
  } else if (Array.isArray(restaurant.photo_url)) {
    parsedPhoto = restaurant.photo_url;
  } else {
    parsedPhoto = ["https://i.imgur.com/zAzV9Db.png"];
  }

  // ✅ Ensure menu is always an array of [string, number]
  let parsedMenu: [string, number][] = [];
  if (typeof restaurant.menu === "string") {
    try {
      const tempMenu = JSON.parse(restaurant.menu.replace(/'/g, '"'));
      if (Array.isArray(tempMenu)) {
        parsedMenu = tempMenu.map((item) =>
          Array.isArray(item) && typeof item[0] === "string" && typeof item[1] === "number"
            ? [item[0], item[1]]
            : ["Unknown", 0]
        );
      }
    } catch (err) {
      console.warn("menu 파싱 실패:", err);
      parsedMenu = [];
    }
  } else if (Array.isArray(restaurant.menu)) {
    parsedMenu = restaurant.menu;
  } else {
    parsedMenu = [];
  }

  // ✅ Ensure facilities is always an array of strings
  let parsedFacilities: string[] = [];
  if (typeof restaurant.facilities === "string") {
    try {
      parsedFacilities = JSON.parse(restaurant.facilities.replace(/'/g, '"'));
      if (!Array.isArray(parsedFacilities)) parsedFacilities = [];
    } catch (err) {
      console.warn("facilities 파싱 실패:", err);
      parsedFacilities = [];
    }
  } else if (Array.isArray(restaurant.facilities)) {
    parsedFacilities = restaurant.facilities;
  } else {
    parsedFacilities = [];
  }

  // ✅ Ensure seat_info is always an array of strings
  let parsedSeatInfo: string[] = [];
  if (typeof restaurant.seat_info === "string") {
    try {
      parsedSeatInfo = JSON.parse(restaurant.seat_info.replace(/'/g, '"'));
      if (!Array.isArray(parsedSeatInfo)) parsedSeatInfo = [];
    } catch (err) {
      console.warn("seat_info 파싱 실패:", err);
      parsedSeatInfo = [];
    }
  } else if (Array.isArray(restaurant.seat_info)) {
    parsedSeatInfo = restaurant.seat_info;
  } else {
    parsedSeatInfo = [];
  }

  // ✅ Ensure distance and business_hours have valid values
  const distanceValue = restaurant.distance ?? "정보 없음";
  const hoursValue = restaurant.business_hours && restaurant.business_hours !== "NaN"
    ? restaurant.business_hours
    : "정보 없음";

  return {
    ...restaurant,
    photo_url: parsedPhoto,
    menu: parsedMenu,
    facilities: parsedFacilities,
    seat_info: parsedSeatInfo,
    distance: distanceValue,
    business_hours: hoursValue,
  } as Restaurant;
};