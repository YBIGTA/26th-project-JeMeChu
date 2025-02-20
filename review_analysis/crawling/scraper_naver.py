"""
네이버 지도에서 식당 리뷰 및 세부 정보를 크롤링하는 모듈입니다.

입력 CSV 파일(restaurant_df.csv)로부터 식당 정보를 읽어와,
각 식당에 대해 네이버 지도에서 검색 후 상세 페이지에 접근하여
아래와 같은 정보를 수집합니다.
  - 전화번호, 운영시간, 소개, 편의시설 및 서비스, 주차 정보
  - "이런점이 좋았어요" 항목 (라벨과 좋아요 개수)
  - 최신 리뷰 최대 300개 (리뷰 작성일 및 텍스트)

수집된 결과는 업데이트된 CSV 파일(updated_naver_map_data.csv)로 저장됩니다.
"""

import time
import random
import logging
import re
import os

from typing import Any, Dict, List

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 로깅 설정
logging.basicConfig(
    filename="crawling.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def random_sleep(min_wait: float = 1.0, max_wait: float = 3.0) -> None:
    """
    min_wait와 max_wait 사이의 임의의 시간(초)만큼 대기합니다.
    
    Args:
        min_wait: 최소 대기 시간(초)
        max_wait: 최대 대기 시간(초)
    """
    time.sleep(random.uniform(min_wait, max_wait))

class NaverMapScraper:
    """
    네이버 지도에서 식당 정보를 크롤링하는 클래스입니다.
    """
    
    def __init__(self, driver: webdriver.Chrome, df: pd.DataFrame) -> None:
        """
        초기화합니다.
        
        Args:
            driver: Selenium WebDriver 인스턴스.
            df: '도로명주소'와 '사업장명' 컬럼을 포함한 식당 정보 DataFrame.
        """
        self.driver = driver
        self.df = df
        self.total_rows = len(self.df)

        if "Processed" not in self.df.columns:
            self.df["Processed"] = ""

    def collect_reviews(self) -> None:
        """
        각 식당에 대해 네이버 지도에서 정보를 수집하여 DataFrame을 업데이트하고,
        최종 결과를 CSV 파일로 저장합니다.
        """
        # 추가할 컬럼들을 DataFrame에 미리 생성합니다.
        columns_to_add = [
            "전화번호", "운영시간", "총 리뷰 개수", "소개",
            "편의시설 및 서비스", "주차 정보", "이런점이 좋았어요", "최신 300개 리뷰"
        ]
        for col in columns_to_add:
            if col not in self.df.columns:
                self.df[col] = ""

        # 각 식당에 대해 처리
        for index, row in self.df.iterrows():

            if row["Processed"] == "Yes":
                continue
            road_address: str = row["도로명주소"]
            business_name: str = row["사업장명"]

            # 기본값 초기화
            phone: str = "정보 없음"
            total_reviews: int = 0
            intro: str = "정보 없음"
            services: List = []
            parking: str = "정보 없음"
            seating_types: List = []
            good_points: List[List[Any]] = []
            collected_reviews: List[Dict[str, str]] = []
            operation_data: Dict = {}

            try:
                print(f"[INFO] 검색 시작: {business_name} ({road_address})")
                logging.info(f"검색 시작: {business_name} ({road_address})")
                self.driver.get("https://map.naver.com/")
                random_sleep(2, 4)

                # 검색창에 도로명주소 입력 후 검색
                search_box = self.driver.find_element(By.XPATH, "//input[contains(@class, 'input_search')]")
                search_box.clear()
                search_box.send_keys(road_address)
                search_box.send_keys(Keys.RETURN)
                random_sleep(3, 5)

                # "더보기" 버튼 클릭 시도
                try:
                    more_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'link_more')]")
                    more_button.click()
                    random_sleep(2, 4)
                except NoSuchElementException:
                    print(f"[WARNING] '{business_name}' - '더보기' 버튼 없음, 스킵")
                    logging.warning(f"'{business_name}' - '더보기' 버튼 없음, 스킵")

                # 검색 결과 중에서 식당명을 포함한 요소를 찾음
                place_elements = self.driver.find_elements(By.XPATH, "//strong[contains(@class, 'search_title')]")
                target_place = None
                for place in place_elements:
                    if business_name.strip() in place.text.strip() or place.text.strip() in business_name.strip():
                        target_place = place
                        break

                if target_place:
                    try:
                        search_link = target_place.find_element(
                            By.XPATH, "./ancestor::button[@class='link_search']"
                        )
                        search_link.click()
                        time.sleep(3)
                        print(f"[INFO] '{business_name}' 버튼 클릭 완료!")
                        logging.info(f"'{business_name}' 버튼 클릭 완료!")
                    except NoSuchElementException:
                        print(f"[ERROR] '{business_name}' - 검색 결과에서 버튼을 찾을 수 없습니다.")
                        logging.warning(f"'{business_name}' - 조상 <button> 태그를 찾을 수 없습니다.")
                    except Exception as e:
                        print(f"[ERROR] '{business_name}' 버튼 클릭 실패: {e}")
                        logging.warning(f"'{business_name}' 버튼 클릭 실패: {e}")
                else:
                    print(f"[WARNING] '{business_name}' - 검색 결과 없음, 스킵")
                    logging.warning(f"'{business_name}' - 검색 결과 없음, 스킵")
                    continue

                # iframe 로딩 후 진입
                WebDriverWait(self.driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it((By.ID, "entryIframe"))
                )
                print("[INFO] entryIframe 진입 완료")
                logging.info("entryIframe 진입 완료")

                # 영업 시간 버튼
                try:
                    hours_tab = self.driver.find_element(By.XPATH, "//div[contains(@class, 'A_cdD')]")
                    hours_tab.click()
                    print("[INFO] 영업 시간 버튼 클릭 완료!")
                    logging.info("영업 시간 버튼 클릭 완료!")
                    random_sleep(2, 3)
                except NoSuchElementException:
                    print("[WARNING] 영업시간 버튼을 찾지 못했습니다.")
                    logging.warning("영업시간 버튼을 찾지 못했습니다.")
                
                valid_days = ["월", "화", "수", "목", "금", "토", "일"]  # 요일 리스트

                try:
                    # 모든 요일 및 영업시간 요소 찾기
                    days = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'w9QyJ')]//span[1]")
                    raw_data = [day.text.strip() for day in days[2:]]  # 불필요한 앞 2개 데이터 제외
                    print("[DEBUG] raw_data:", raw_data)

                    # 요일과 영업시간 매핑 (2개씩 묶어서 처리)
                    for item in raw_data:
                        # 개행 문자가 있는 항목만 처리 (즉, "요일\n영업시간 ..." 형식인 경우)
                        if "\n" in item:
                            parts = item.split("\n")
                            # parts[0]는 요일, parts[1]은 바로 뒤에 있는 영업시간 정보
                            if len(parts) >= 2:
                                day = parts[0].strip()
                                hours = parts[1].strip()
                                if day in valid_days:
                                    operation_data[day] = hours

                    print("[DEBUG] operation_data (unsorted):", operation_data)
                    # 현재까지 '정보없음'인 경우 정리: 당일만 휴무인 경우
                    sorted_operation_data = {day: operation_data.get(day, "정보 없음") for day in valid_days}
                    print("[INFO] 영업시간 크롤링 완료:", sorted_operation_data)
                    logging.info(f"영업시간 크롤링 완료: {sorted_operation_data}")

                except Exception as e:
                    print("[ERROR] 영업시간 수집 오류 발생:", e)
                    logging.error("영업시간 수집 오류 발생: " + str(e))

                try:
                    phone_element = self.driver.find_element(By.XPATH, "//div[@class='vV_z_']//span[@class='xlx7Q']")
                    phone = phone_element.text
                    print("[INFO] 전화번호:", phone)
                    logging.info(f"전화번호: {phone}")
                except Exception as e:
                    print("[ERROR] 전화번호 수집 오류 발생:", e)
                    logging.error(f"전화번호 수집 오류 발생: {e}")

                time.sleep(1)
                # '정보' 탭 클릭
                try:
                    review_tab = self.driver.find_element(By.XPATH, "//a[contains(@class, 'fvwqf') and .//span[contains(@class, 'iNSaH') and text()='정보']]")
                    review_tab.click()
                    print("[INFO] 정보 탭 클릭 완료!")
                    logging.info("정보 탭 클릭 완료!")
                    random_sleep(2, 3)
                except NoSuchElementException:
                    print("[WARNING] '정보' 탭을 찾지 못했습니다.")
                    logging.warning("'정보' 탭을 찾지 못했습니다.")

                time.sleep(1)
                # 펼쳐보기 클릭
                try:
                    expand_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//a[contains(@class, 'OWPIf')]//span[contains(@class, 'place_blind') and contains(text(), '펼쳐보기')]")
                        )
                    )
                    
                    # 일반 click() 호출이 안 될 경우 JavaScript click() 사용
                    self.driver.execute_script("arguments[0].click();", expand_button)
                    print("[INFO] '펼쳐보기' 버튼 클릭 완료!")
                    logging.info("'펼쳐보기' 버튼 클릭 완료!")
                except Exception as e:
                    print("[WARNING] '펼쳐보기' 버튼을 찾지 못했습니다.", e)
                    logging.warning(f"'펼쳐보기' 버튼을 찾지 못했습니다.: {e}")
                
                # 소개 텍스트 추출
                try:
                    desc_div = self.driver.find_element(
                        By.XPATH,
                        "//div[contains(@class, 'T8RFa') and contains(@class, 'CEyr5')]"
                    )
                    intro = desc_div.text.strip()
                    print("[INFO] 소개 텍스트 추출 완료:")
                    logging.info("소개 텍스트 추출 완료")
                    print(intro)
                except Exception as e:
                    intro = "정보 없음"
                    print("[ERROR] 소개 텍스트 추출 실패:", e)
                    logging.error(f"소개 텍스트 추출 실패: {e}")
                
                # 서비스 추출
                try:
                    services_ul = self.driver.find_element(By.XPATH, "//ul[contains(@class, 'JU0iX')]")
                    services_lis = services_ul.find_elements(By.XPATH, ".//li[contains(@class, 'c7TR6')]")
                    for li in services_lis:
                        try:
                            services_text = li.find_element(By.XPATH, ".//div[contains(@class, 'owG4q')]").text.strip()
                            services.append(services_text)
                        except Exception as ex:
                            print("[WARN] 서비스 항목 추출 오류:", ex)
                            logging.warning(f"서비스 항목 추출 오류: {ex}")
                    print("[INFO] 서비스 추출 완료:", services)
                    logging.info("서비스 추출 완료")
                except Exception as e:
                    print("[ERROR] 서비스 추출 실패:", e)
                    logging.error(f"서비스 추출 실패: {e}")
                
                # 주차 정보 추출
                try:
                    parking_div = self.driver.find_element(
                        By.XPATH, 
                        "//div[contains(@class, 'qbROU')]//div[contains(@class, 'TZ6eS')]"
                    )
                    parking = parking_div.text.strip()
                    print("[INFO] 주차 정보 추출 완료:", parking)
                    logging.info("주차 정보 추출 완료")
                except Exception as e:
                    parking = "정보 없음"
                    print("[ERROR] 주차 정보 추출 실패:", e)
                    logging.info(f"주차 정보 추출 실패: {e}")
                
                # 좌석 정보 추출
                try:
                    seating_ul = self.driver.find_element(
                        By.XPATH, 
                        "//div[contains(@class, 'place_section_content')]//ul[contains(@class, 'GXptY')]"
                    )
                    seating_lis = seating_ul.find_elements(By.XPATH, ".//li[contains(@class, 'Lw5L1')]")
                    for li in seating_lis:
                        try:
                            seating_text = li.find_element(By.XPATH, ".//div[contains(@class, '_2eVI0')]").text.strip()
                            seating_types.append(seating_text)
                        except Exception as ex:
                            print("[WARN] 좌석 정보 추출 오류:", ex)
                            logging.warning(f"좌석 정보 추출 오류: {ex}")
                    print("[INFO] 좌석 정보 추출 완료:", seating_types)
                    logging.info("좌석 정보 추출 완료")
                except Exception as e:
                    print("[ERROR] 좌석 정보 추출 실패:", e)
                    logging.error(f"좌석 정보 추출 실패: {e}")

                # '리뷰' 탭 클릭
                try:
                    review_tab = self.driver.find_element(By.XPATH, "//span[normalize-space(text())='리뷰']")
                    review_tab.click()
                    print("[INFO] 리뷰 탭 클릭 완료!")
                    logging.info("리뷰 탭 클릭 완료!")
                    random_sleep(2, 3)
                except NoSuchElementException:
                    print("[WARNING] '리뷰' 탭을 찾지 못했습니다.")
                    logging.warning("'리뷰' 탭을 찾지 못했습니다.")

                # "이런점이 좋았어요" 항목 수집 (최대 4개)
                try:
                    items = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'MHaAm')]")
                    for item in items[:4]:
                        label_elem = item.find_element(By.XPATH, ".//span[contains(@class,'t3JSf')]")
                        label_text = label_elem.text.strip()

                        count_elem = item.find_element(By.XPATH, ".//span[contains(@class,'CUoLy')]")
                        count_text = count_elem.text.strip()

                        match = re.search(r'\d+', count_text)
                        count_val = int(match.group()) if match else 0

                        good_points.append([label_text, count_val])
                    print(f"[INFO] '이런점이 좋았어요' 수집 완료: {good_points}")
                    logging.info(f"'이런점이 좋았어요' 수집 완료: {good_points}")
                except NoSuchElementException:
                    print("[WARNING] '이런점이 좋았어요' 항목을 찾지 못했습니다.")
                    logging.warning("'이런점이 좋았어요' 항목을 찾지 못했습니다.")
                except Exception as e:
                    print(f"[WARNING] '이런점이 좋았어요' 수집 중 오류: {e}")
                    logging.warning(f"'이런점이 좋았어요' 수집 중 오류: {e}")

                # 총 리뷰 수 수집
                try:
                    count_elem = self.driver.find_element(By.XPATH, "//em[@class='place_section_count']")
                    count_text = count_elem.text.strip()
                    total_reviews = int(count_text)
                    print(f"[INFO] 총 리뷰 수: {total_reviews}")
                    logging.info(f"총 리뷰 수: {total_reviews}")
                except NoSuchElementException:
                    print("[WARNING] 총 리뷰 수를 찾을 수 없습니다.")
                    logging.warning("총 리뷰 수를 찾을 수 없습니다.")
                except ValueError:
                    print(f"[WARNING] 리뷰 수 텍스트를 숫자로 변환할 수 없음: {count_text}")
                    logging.warning(f"리뷰 수 텍스트를 숫자로 변환할 수 없음: {count_text}")

                # 최신순 정렬 클릭
                try:
                    latest_sort = self.driver.find_element(By.XPATH, "//a[contains(., '최신순')]")
                    latest_sort.click()
                    print("[INFO] 최신순 클릭 완료")
                    logging.info("최신순 클릭 완료")
                    random_sleep(2, 4)
                except Exception:
                    print("[WARNING] 최신순 클릭 불가")
                    logging.warning("최신순 클릭 불가")

                # 리뷰 최대 300개 수집
                MAX_REVIEWS = 300
                while len(collected_reviews) < MAX_REVIEWS:
                    review_elements = self.driver.find_elements(
                        By.XPATH,
                        "//li[contains(@class,'place_apply_pui') and contains(@class,'EjjAW')]"
                    )
                    new_reviews = []
                    for rev in review_elements:
                        try:
                            date_elem = rev.find_element(By.XPATH, ".//time[@aria-hidden='true']")
                            review_date = date_elem.text.strip()
                        except NoSuchElementException:
                            review_date = ""

                        try:
                            text_anchor = rev.find_element(
                                By.XPATH,
                                ".//div[contains(@class,'pui__vn15t2')]//a[@data-pui-click-code='rvshowmore']"
                            )
                            review_text = text_anchor.text.strip()
                        except NoSuchElementException:
                            review_text = ""

                        if review_text:
                            new_reviews.append({
                                "date": review_date,
                                "text": review_text
                            })

                    collected_reviews.extend(new_reviews)
                    print(f"[INFO] 현재까지 수집된 리뷰: {len(collected_reviews)}개")
                    logging.info(f"[진행상황] 현재까지 수집된 리뷰: {len(collected_reviews)}개")

                    # "더보기" 버튼 클릭하여 추가 리뷰 로딩
                    try:
                        more_button = self.driver.find_element(
                            By.XPATH,
                            "//a[contains(@class,'fvwqf') and contains(., '더보기')]"
                        )
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                        more_button.click()
                        print("[INFO] '더보기' 버튼 클릭 완료!")
                        logging.info("'더보기' 버튼 클릭 완료!")
                        random_sleep(2, 4)
                    except NoSuchElementException:
                        print("[WARNING] 더보기 버튼을 더 이상 찾을 수 없으므로 반복 종료")
                        logging.warning("더보기 버튼을 더 이상 찾을 수 없으므로 반복 종료")
                        break

                print(f"[INFO] 최종 수집된 리뷰: 총 {len(collected_reviews)}개")
                logging.info(f"최종 수집된 리뷰: 총 {len(collected_reviews)}개")

                # DataFrame에 수집된 데이터 저장
                self.df.at[index, "전화번호"] = phone
                self.df.at[index, "운영시간"] = operation_data
                self.df.at[index, "총 리뷰 개수"] = total_reviews
                self.df.at[index, "소개"] = intro
                self.df.at[index, "편의시설 및 서비스"] = services
                self.df.at[index, "주차 정보"] = parking
                self.df.at[index, "좌석 정보"] = seating_types
                self.df.at[index, "이런점이 좋았어요"] = str(good_points)
                self.df.at[index, "최신 300개 리뷰"] = str(collected_reviews[:300])

                print(f"[INFO] '{business_name}' 데이터프레임 저장 완료")
                logging.info(f"'{business_name}' 데이터프레임 저장 완료")

                # 식당 처리 완료 표시
                self.df.at[index, "Processed"] = "Yes"
                
                # 현재 식당 처리가 끝난 후 기본 컨텐츠로 전환
                self.driver.switch_to.default_content()

                # 진행 상황 저장 
                temp_output = "restaurant_temp.csv"
                self.df.to_csv(temp_output, index=False, encoding="utf-8-sig")  
                print(f"[INFO] 현재 진행 상황 저장됨 - {self.total_rows}개 중 {index+1}개 업데이트")
                print(f"[INFO] 현재 csv 상 위치: ")

            except Exception as e:
                print(f"[ERROR] '{business_name}' 크롤링 중 오류 발생: {e}")
                logging.error(f"'{business_name}' 크롤링 중 오류 발생: {e}")

        # 모든 식당 처리 후 드라이버 종료 및 CSV 저장
        self.driver.quit()
        output_filename = "naver_data.csv"
        self.df.to_csv(output_filename, index=False, encoding="utf-8-sig")
        print(f"[INFO] 크롤링 완료! CSV 파일로 저장됨: {output_filename}")
        logging.info(f"크롤링 완료! CSV 파일로 저장됨: {output_filename}")

        # if os.path.exists("restaurant_temp.csv"):
        #     os.remove("restaurant_temp.csv")
        #     print(f"임시 파일 'restaurant_temp.csv' 삭제 완료.")

def main() -> None:
    """
    메인 함수:
      - CSV 파일로부터 식당 정보를 읽어옴
      - Selenium WebDriver 및 크롬 옵션 설정
      - NaverMapScraper 인스턴스를 생성하여 크롤링 작업 실행
    """
    input_csv = "restaurant_df.csv"
    temp_csv = "restaurant_temp.csv"

    if os.path.exists(temp_csv):
        try:
            df = pd.read_csv(temp_csv, encoding="UTF-8")
            print(f"[INFO] 임시 파일 '{temp_csv}'에서 데이터를 불러왔습니다.")
        except Exception as e:
            print(f"[ERROR] 임시 파일 읽기 오류: {e}")
            logging.error(f"[ERROR] 임시 파일 읽기 오류: {e}")
            df = pd.read_csv(input_csv, encoding="UTF-8")
            print(f"[INFO] 원본 파일 '{input_csv}'에서 데이터를 불러왔습니다.")
    else:
        try:
            df = pd.read_csv(input_csv, encoding="UTF-8")
            print(f"[INFO] 원본 파일 '{input_csv}'에서 데이터를 불러왔습니다.")
        except Exception as e:
            print(f"[ERROR] CSV 파일 읽기 오류: {e}")
            logging.error(f"CSV 파일 읽기 오류: {e}")
            return

    # 크롬 옵션 설정
    chrome_options = Options()
    # headless 모드 사용 시 아래 주석 해제
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )

    # Selenium WebDriver 초기화
    driver = webdriver.Chrome(options=chrome_options)

    # 크롤러 인스턴스 생성 및 실행
    scraper = NaverMapScraper(driver, df)
    scraper.collect_reviews()

if __name__ == "__main__":
    main()
