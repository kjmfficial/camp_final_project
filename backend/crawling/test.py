from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import requests
import urllib.request
import urllib.parse
import json
import datetime
from dateutil.parser import parse
import shutil
  
import sys
import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()
# 모듈 경로 설정.... 이렇게 해줘야 다른 디랙토리에 있는 모듈 가져다 쓸 수 있음... !!
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DB.db_mysql import apt_housing_application_basic_info_insert,apt_housing_application_basic_info_select,apt_housing_competition_rate_insert,apt_housing_application_status_insert,apt_housing_application_status_select,apt_housing_competition_rate_select,unranked_housing_application_basic_info_select,unranked_housing_application_basic_info_insert,unranked_housing_competition_rate_select,unranked_housing_competition_rate_insert,delete,some_condition,apt_schedule_insert,apt_schedule_select
from DB.db_mongodb import mongodb_insert,mongo_delete
from DB.s3 import s3_upload

# Selenium 설정
service = Service(executable_path='/home/ubuntu/chromedriver-linux64/chromedriver')
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-extensions')


def housing_application_announcement_download(url, dic):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    previous_page_num = None

    while True:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        tds = soup.find_all('td', class_='txt_l')
        texts = [td.get_text(strip=True) for td in tds]

        for text in texts:
            try:
                print(f"텍스트: {text} 클릭 시도 중...")

                # 텍스트 기반 요소 클릭
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, text)))
                clickable_element = driver.find_element(By.LINK_TEXT, text)
                clickable_element.click()

                time.sleep(1)

                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "iframeDialog")))
                iframe = driver.find_element(By.ID, "iframeDialog")
                driver.switch_to.frame(iframe)

                pophtml = driver.page_source
                popsoup = BeautifulSoup(pophtml, 'html.parser')

                target_row = popsoup.find('th', text='모집공고일')
                if target_row:
                    target_cell = target_row.find_next('td').get_text(strip=True)
                    result = target_cell.split('(')[0].strip()
                    announcement_date = parse(result)
                else:
                    print("모집공고일 항목이 없습니다.")
                    continue

                now = datetime.datetime.today()
                if (now - announcement_date).days > 30:
                    print("현재 날짜에서 1달 전 후 청약 공고를 모두 다운받았습니다.")
                    return

                pdf_down_button = popsoup.find('a', class_='radius_btn')
                if pdf_down_button:
                    pdf_url = pdf_down_button['href']
                    print(f"PDF URL: {pdf_url}")
                    
                    title_element = popsoup.find('th', scope='col', colspan='2')
                    if title_element:
                        title = title_element.get_text(strip=True)
                        s3_key = f"{dic}/{title}_모집공고.pdf"
                        
                        # PDF 다운로드
                        response = requests.get(pdf_url, stream=True)
                        if response.status_code == 200:
                            print(f"PDF 다운로드 성공: {pdf_url}")
                            print(f"PDF 데이터 크기: {len(response.content)} bytes")
                        else:
                            print(f"PDF 다운로드 실패: 상태 코드 {response.status_code}, URL: {pdf_url}")

                        # S3 업로드 호출
                        if response.content and s3_key:
                            s3_upload(response.content, s3_key)
                        else:
                            print("업로드를 진행할 데이터나 경로가 유효하지 않습니다.")

                # 팝업 닫기
                driver.switch_to.default_content()
                close_button = driver.find_element(By.XPATH, '/html/body/div[4]/div/button')
                close_button.click()

            except Exception as e:
                print(f"텍스트 '{text}' 클릭 실패: {e}")

        current_page_num, soup = navigate_to_next_page(driver, soup, previous_page_num)
        if current_page_num is None:
            break
        previous_page_num = current_page_num

    driver.quit()

def navigate_to_next_page(driver, soup, previous_page_num):
    div = soup.find("div", class_="pageview")
    if not div:
        print("페이지 네비게이션을 찾을 수 없습니다.")
        return None, soup

    current_page = div.find("a", title="현재페이지")
    if current_page:
        current_page_num = int(current_page.get_text(strip=True))
        print(f"현재 페이지: {current_page_num}")
        if current_page_num == previous_page_num:
            print("마지막 페이지에 도달했습니다.")
            return None, soup
    else:
        print("현재 페이지를 찾을 수 없습니다.")
        return None, soup

    if current_page_num % 10 == 0:  # 현재 페이지가 10의 배수인 경우
        try:
            next_button = driver.find_element(By.XPATH, "//a[span[@class='blind'][text()='다음 페이지로']]")
            next_button.click()

            WebDriverWait(driver, 10).until(EC.staleness_of(next_button))
            time.sleep(2)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            print("더 이상 다음 페이지가 없습니다.")
            return None, soup
    else:  # 10의 배수가 아닌 경우, 다음 페이지 버튼 클릭
        next_page_num = current_page_num + 1
        try:
            next_page_button = driver.find_element(By.LINK_TEXT, str(next_page_num))
            next_page_button.click()
            time.sleep(2)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            print(f"{next_page_num} 페이지로 이동 실패: {e}")
            return None, soup

    return current_page_num, soup





if __name__ =="__main__":
    url = "https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancListView.do"
    dic = "apt"
    col = ['지역', '주택구분', '분양/임대', '주택명', '시공사', '문의처', '모집공고일', '청약기간', '담청자발표']

   
    housing_application_announcement_download(url,dic)

    url = "https://www.applyhome.co.kr/ai/aia/selectAPTRemndrLttotPblancListView.do"
    dic = "unranked"
    col = ['지역', '주택명', '시행사', '모집공고일', '청약기간', '담청자발표']
    competition_rate_table_list = ["unranked_housing_competition_rate_1","unranked_housing_competition_rate_2"]

    housing_application_announcement_download(url,dic)