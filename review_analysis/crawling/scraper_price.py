"""
카카오 맵에서 메뉴 및 가격을 크롤링하는 모듈입니다.

수집된 결과는 업데이트된 CSV 파일(kakak_map_price.csv)로 저장됩니다.

기존 데이터에 머지하실 경우 "지번주소","사업장명"가 모두 일치 할 경우 
pd.merge(original df, price df, on=['col', '지번주소', '사업장명'], how='outer')로
머지 시켜주기
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



class KakaoMapScraper:
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
        각 식당에 대해 카카오맵에서 정보를 수집하여 DataFrame을 업데이트하고,
        최종 결과를 CSV 파일로 저장합니다.
        """
        # 추가할 컬럼들을 DataFrame에 미리 생성합니다.
        columns_to_add = [
            "메뉴"
        ]

        for col in columns_to_add:
            if col not in self.df.columns:
                self.df[col] = ""

        # 각 식당에 대해 처리
        for index, row in self.df.iterrows():
            
            if row["Processed"] == "Yes":
                continue

            road_address: str = row["지번주소"]
            business_name: str = row["사업장명"]

            # 기본값 초기화
            menu: list[List[str,int]] = []

            try:
                print(f"[INFO] 검색 시작: {business_name} ({road_address})")
                logging.info(f"검색 시작: {business_name} ({road_address})")
                self.driver.get("https://map.kakao.com")
                random_sleep(2, 4)

                # 검색창에 도로명주소 입력 후 검색
                search_box = self.driver.find_element(By.XPATH, "//input[contains(@class, 'tf_keyword')]")
                search_box.clear()
                search_box.send_keys(road_address)
                search_box.send_keys(Keys.RETURN)
                random_sleep(3, 5)



                target_place = None

                while target_place == None:

                    try:
                        place_elements = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, "//a[@data-id='name']"))
                        )
                    except Exception as e:
                        print(f"[ERROR] 검색 결과를 불러오지 못함: {e}")
                        break


                    for place in place_elements:
                        place_name = place.get_attribute("title").replace(" ", "")  # 'title' 속성에서 장소 이름 가져오기
                        print(place_name, business_name.replace(" ", ""))
                        if business_name.replace(" ", "") in place_name or place_name in business_name.replace(" ", ""):
                            target_place = place
                            check = "Good"
                            break
                    if check == "Good":
                        break

                    # "더보기" 버튼 클릭 시도
                    try:
                        more_button = self.driver.find_element(By.XPATH, "//a[@id='info.search.place.more']")
                        
                        self.driver.execute_script("arguments[0].scrollIntoView();", more_button)
                        time.sleep(1)

                        more_button.click()
                        random_sleep(2, 4)
                        print("[INFO] '더보기' 버튼 클릭 완료!")
                        logging.info("'더보기' 버튼 클릭 완료!")

                    except NoSuchElementException:
                        print(f"[WARNING] '{business_name}' - '더보기' 버튼 없음, 스킵")
                        logging.warning(f"'{business_name}' - '더보기' 버튼 없음, 스킵")
                        break
                    
                    except Exception as e:
                        print(f"[ERROR] '더보기' 버튼 클릭 실패, 스킵")
                        logging.warning(f"'더보기' 버튼 클릭 실패: {e}")
                        break
                
                if check != "Good":
                    continue

                                 
                if target_place:
                    try:
                        # target_place의 상위 요소 중에서 "상세보기" 하이퍼링크 찾기
                        moreview_link = target_place.find_element(By.XPATH, "./ancestor::li//a[@data-id='moreview']")
                        #self.driver.execute_script("arguments[0].scrollIntoView(false);", moreview_link)
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", moreview_link)                        
                        time.sleep(3)

                        # self.driver.execute_script("window.scrollBy(0, 150);")  # 150px 아래로 이동
                        # time.sleep(1)

                        # try:
                        #     WebDriverWait(self.driver, 5).until(
                        #         EC.invisibility_of_element_located((By.ID, "dimmedLayer"))
                        #     )
                        #     print("[INFO] dimmedLayer 사라짐, 클릭 가능 상태!")
                        #     logging.info("[INFO] dimmedLayer 사라짐, 클릭 가능 상태!")

                        # except TimeoutException:
                        #     print("[WARNING] dimmedLayer가 여전히 존재함, 강제 클릭 시도")
                        #     logging.warning("[WARNING] dimmedLayer가 여전히 존재함, 강제 클릭 시도")


                        # moreview_link.click()  # 상세보기 링크 클릭

                        place_url = moreview_link.get_attribute("href")
                        print(f"[INFO] 이동할 URL: {place_url}")
                        self.driver.get(place_url) 
                        time.sleep(3)


                        print(f"[INFO] '{business_name}' 상세보기 버튼 클릭 완료!")
                        logging.info(f"'{business_name}' 상세보기 버튼 클릭 완료!")



                    except NoSuchElementException:
                        print(f"[ERROR] '{business_name}' - 검색 결과에서 버튼을 찾을 수 없습니다.")
                        logging.warning(f"'{business_name}' - 조상 <button> 태그를 찾을 수 없습니다.")
                        continue
                    except Exception as e:
                        print(f"[ERROR] '{business_name}' 버튼 클릭 실패: {e}")
                        logging.warning(f"'{business_name}' 버튼 클릭 실패: {e}")
                        continue
                else:
                    print(f"[WARNING] '{business_name}' - 검색 결과 없음, 스킵")
                    logging.warning(f"'{business_name}' - 검색 결과 없음, 스킵")
                    continue



                try:
                    # "메뉴 목록" 바로 다음에 있는 "더보기" 버튼 찾기
                    more_button = self.driver.find_element(By.XPATH, "//ul[contains(@class, 'list_menu')]/following-sibling::a[contains(@class, 'link_more')]")

                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", more_button)                        

                    time.sleep(3)

                    more_button.click()
                    time.sleep(2)
                    print("[INFO] '메뉴 더보기' 버튼 클릭 완료!")
                    logging.info("'메뉴 더보기' 버튼 클릭 완료!")

                except NoSuchElementException:
                    print("[WARNING] '메뉴 더보기' 버튼 없음, 스킵")
                    logging.warning("'메뉴 더보기' 버튼 없음, 스킵")

                except Exception as e:
                    print(f"[ERROR] '메뉴 더보기' 버튼 클릭 실패: {e}")
                    logging.warning(f"'메뉴 더보기' 버튼 클릭 실패: {e}")
                    continue

                try:
                    menu_items = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'menu_fst') or @data-page]")

                    for item in menu_items:
                        menu_name = ""
                        menu_price = None  # 가격이 없는 경우 대비

                        # 메뉴명 가져오기 (예외 처리)
                        try:
                            menu_name_element = item.find_element(By.XPATH, ".//span[contains(@class, 'loss_word')]")
                            menu_name = menu_name_element.text.strip()
                        except Exception:
                            print("[WARNING] 메뉴명을 찾을 수 없음")
                            continue

                        # 가격 가져오기 (예외 처리)
                        try:
                            price_element = item.find_element(By.XPATH, ".//em[contains(@class, 'price_menu')]")
                            price_text = price_element.text.strip().replace(',', '')  # 쉼표 제거 후 숫자로 변환
                            menu_price = int(price_text)
                        except Exception:
                            print(f"[WARNING] '{menu_name}' - 가격 정보를 찾을 수 없음")
                            menu_price = None  # 가격이 없을 경우 None 처리

                        # 메뉴 추가 (가격이 없는 경우에도 추가)
                        menu.append([menu_name, menu_price])

                except NoSuchElementException:
                    print("메뉴 없음")
                    logging.warning("메뉴 없음")
                    continue
                
                except Exception as e:
                    print("메뉴 없음")
                    logging.warning("메뉴 없음")
                    continue


                # DataFrame에 수집된 데이터 저장
                self.df.at[index, "메뉴"] = menu

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
                continue

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
    input_csv = "price.csv"
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

    time.sleep(1)

    # 크롤러 인스턴스 생성 및 실행
    scraper = KakaoMapScraper(driver, df)
    scraper.collect_reviews()

if __name__ == "__main__":
    main()
