# distance_utils.py
import math
import geocoder
import requests
import psycopg2
import os

try:
    import gps
    GPS_ENABLED = True
except ImportError:
    GPS_ENABLED = False

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 지구 반지름 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_gps_location():
    # GPS 기능이 활성화되어 있으면 위치를 시도하고, 있지 않거나 실패하면 None, None을 반환합니다.
    if not GPS_ENABLED:
        return None, None
    try:
        session = gps.gps(mode=gps.WATCH_ENABLE)
        report = session.next()
        if report.get('class') == 'TPV':
            return report.lat, report.lon
    except Exception:
        return None, None

def get_current_location():
    # GPS로 위치를 시도하고, 성공하면 그 좌표를 사용합니다.
    # 실패하면 고정 좌표 (37.56578, 126.9386)를 반환합니다.
    lat, lon = get_gps_location()
    if lat is not None and lon is not None:
        return lat, lon
    return (37.56578, 126.9386)

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