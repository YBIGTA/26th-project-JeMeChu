# distance_utils.py
import math
import geocoder
import requests
import psycopg2
import os

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 지구 반지름 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_ip_location():
    g = geocoder.ip("me")
    if g.ok:
        return g.latlng[0], g.latlng[1]
    return None, None

def get_current_location():
    # 여기서는 GPS 사용 여부와 상관없이 IP 위치로 단순 구현
    return get_ip_location()

def get_lat_lon_from_kakao(address, kakao_api_key):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {kakao_api_key}"}
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["documents"]:
            lat = float(data["documents"][0]["y"])
            lon = float(data["documents"][0]["x"])
            return lat, lon
    return None, None

def get_restaurant_address(restaurant_id, postgres_conn_str):
    # reviews 테이블에서 road_address 조회 (DistanceCalculator.py와 동일)
    conn = psycopg2.connect(postgres_conn_str)
    cursor = conn.cursor()
    query = "SELECT road_address FROM reviews WHERE id = %s;"
    cursor.execute(query, (restaurant_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    return None

def calculate_distance(restaurant_id, user_lat, user_lon, postgres_conn_str, kakao_api_key):
    address = get_restaurant_address(restaurant_id, postgres_conn_str)
    if not address:
        return None
    dest_lat, dest_lon = get_lat_lon_from_kakao(address, kakao_api_key)
    if dest_lat is None or dest_lon is None:
        return None
    return haversine(user_lat, user_lon, dest_lat, dest_lon)
