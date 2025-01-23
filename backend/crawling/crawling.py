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
import html

import sys
import os
from dotenv import load_dotenv
 

load_dotenv()
# 모듈 경로 설정.... 이렇게 해줘야 다른 디랙토리에 있는 모듈 가져다 쓸 수 있음... !!
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DB.db_mysql import apt_housing_application_basic_info_insert,apt_housing_application_basic_info_select,apt_housing_competition_rate_insert,apt_housing_application_status_insert,apt_housing_application_status_select,apt_housing_competition_rate_select,unranked_housing_application_basic_info_select,unranked_housing_application_basic_info_insert,unranked_housing_competition_rate_select,unranked_housing_competition_rate_insert,delete,some_condition,apt_schedule_insert,apt_schedule_select
from DB.db_mongodb import mongodb_insert,mongo_delete,select
from DB.s3 import s3_upload,s3_delete_all
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


naver_client_id = os.environ.get('NAVER_ID')
naver_client_secret = os.environ.get('NAVER_PASSWORD')

def base_info_crawling(url,number,type_number,col,select,insert,df_col): # number = 뒤에 어디까지 제거할건지. 들고올 컬럼
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

    save = []
    apartment_names = select
    exit_flag = False

    previous_page_num = None

    while True:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')          

            # 크롤링
            table = soup.find('table', class_=f"tbl_st tbl_tb tbl_center tbl_padding mTbl type{type_number}")
        
            rows = table.find_all('tr')

            for row in rows:
                columns = row.find_all('td')
                filtered_columns = columns[:-number] # 신청현황, 경쟁률 제거하기~ or 경쟁률 제거

                data = [col.get_text(strip=True) for col in filtered_columns]

                if not data:
                    continue
                
                print(data)

                if any(apartment_name['apartment_name'] == data[df_col] for apartment_name in apartment_names): 
                    print("중복있음 기본정보 크롤링 종료")
                    exit_flag = True
                    break
                
                print(data[df_col],"저장완료")
                save.append(data)
            
            if  exit_flag:
                break

            current_page_num, soup = navigate_to_next_page(driver, soup, previous_page_num)
            if current_page_num is None:
                break
            previous_page_num = current_page_num     


    df = pd.DataFrame(save, columns=col)
    insert(df)
    print(df)
    # df.to_csv(f"./data/{dic}/청약모집기본정보.csv")
    driver.quit()
    
def application_status_crawling(url,select,insert,db_table_name):

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    previous_page_num = None
    apartment_names = select
    
    while True:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        for i in range(10):
            try:
                WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "btn_tbl")))
                apply_buttons = driver.find_elements(By.CLASS_NAME, "btn_ap")

                try:
                    img = apply_buttons[i].find_element(By.CLASS_NAME, "new_ic")
                    print("업데이트 아이콘 있어영~")
                    img_exists = True
                except:
                    img_exists = False

                print(f"신청현황 버튼 {i + 1} 클릭 중...")
                apply_buttons[i].click()

                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "iframeDialog")))
                iframe = driver.find_element(By.ID, "iframeDialog")
                driver.switch_to.frame(iframe)

                popup_html = driver.page_source
                popup_soup = BeautifulSoup(popup_html, "html.parser")

                home_name = popup_soup.find("h5", class_="sub_square").get_text(strip=True)
                table = popup_soup.find("table")

                if not table:
                    raise Exception(f"팝업 {home_name}에 테이블이 없습니다.")

                df = pd.read_html(str(table))[0]
                df["apartment_name"] = home_name
                if any(apartment_name['apartment_name'] == df["apartment_name"].iloc[0] for apartment_name in apartment_names):
                    
                    if img_exists == True :
                        delete(db_table_name, home_name)
                        print("중복있음 / 업데이트완료")
                    else:    
                        driver.switch_to.default_content()
                        close_button = driver.find_element(By.XPATH, '/html/body/div[4]/div/button')
                        close_button.click()
                        print("중복있음 / 삽입 x")
                        continue
                # file_name = f"./data/{dic}/application_status/신청현황_{home_name}.csv"
                # df.to_csv(file_name, index=False, encoding="utf-8-sig")
                # print(f"데이터가 '{file_name}' 파일로 저장되었습니다.")

                driver.switch_to.default_content()
                close_button = driver.find_element(By.XPATH, '/html/body/div[4]/div/button')
                close_button.click()

                insert(df)

                time.sleep(1)
        
            except:
                pass
        current_page_num, soup = navigate_to_next_page(driver, soup, previous_page_num)
        if current_page_num is None:
            break
        previous_page_num = current_page_num

        # 제일 처음 크롤링 할 때는 주석처리하기.!!!!!!!
        if previous_page_num == 5:
            return
    driver.quit()

def competition_rate_crawling(url,select,insert,db_table_name):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    previous_page_num =None
    apartment_names = select
    while True:
        # 현재 페이지의 HTML을 BeautifulSoup로 파싱
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        for i in range(10):  
            try:
                WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "btn_tbl")))  
                apply_buttons = driver.find_elements(By.CLASS_NAME, "btn_cp")  
                
                try:
                    img = apply_buttons[i].find_element(By.CLASS_NAME, "new_ic")
                    print("업데이트 아이콘 있어영~!!")
                    img_exists = True
                except:
                    img_exists = False

                print(f"경쟁률 버튼 {i + 1} 클릭 중...")
                apply_buttons[i].click()  

                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "iframeDialog")))  

                # 팝업 내부의 iframe 요소 가져오기
                iframe = driver.find_element(By.ID, "iframeDialog")  
                driver.switch_to.frame(iframe)  

                # iframe 내부 HTML 코드 가져오기
                popup_html = driver.page_source  
                popup_soup = BeautifulSoup(popup_html, "html.parser") 
                table = popup_soup.find("table") 
                home_name = popup_soup.find("h5", class_="sub_square").get_text(strip=True)
                # 테이블이 없는 경우 오류 발생
                if not table:
                    raise Exception("팝업 내부에 테이블을 찾을 수 없습니다.")  

                # 테이블 데이터를 DataFrame으로 변환
                df = pd.read_html(str(table))[0]
                df["apartment_name"] = home_name
                
                if any(apartment_name['apartment_name'] == df["apartment_name"].iloc[0] for apartment_name in apartment_names):

                    if img_exists:
                        # db_table_name이 리스트인지 확인
                        if isinstance(db_table_name, list):
                            # 두 개 테이블 중 삭제 조건을 설정
                            for table_name in db_table_name:
                                if some_condition(table_name, home_name):  # 조건에 맞는 테이블 찾기
                                    delete(table_name, home_name)
                                    break  # 하나만 삭제 후 종료
                        else:
                            # 단일 테이블에서 삭제
                            delete(db_table_name, home_name)
                            print("중복있음 / 업데이트완료")

                    else:
                        driver.switch_to.default_content()
                        close_button = driver.find_element(By.XPATH, '/html/body/div[4]/div/button')
                        close_button.click()
                        print("중복있음 / 삽입 x")
                        continue
                    
                driver.switch_to.default_content()
                close_button = driver.find_element(By.XPATH, '/html/body/div[4]/div/button')
                close_button.click()
            
                print(df)
                insert(df)

                time.sleep(1)

            except Exception as e:
                pass

        current_page_num, soup = navigate_to_next_page(driver, soup, previous_page_num)
        if current_page_num is None:
            break
        previous_page_num = current_page_num
        
        # 제일 처음 크롤링 할 때는 주석처리하기.!!!!!!!
        if previous_page_num == 5:
            return
    driver.quit()


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


def apt_schedule_crawling(url):
    previous_page_num = None
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    target_keywords = ["특별공급", "1순위", "2순위"]
    apartment_names = apt_schedule_select()

    while True:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 'td' 태그에서 텍스트 추출
        tds = soup.find_all('td', class_='txt_l')
        texts = [td.get_text(strip=True) for td in tds]

        for text in texts:
            try:
                print(f"텍스트: {text} 클릭 시도 중...")

                # 텍스트를 기반으로 해당 요소 클릭
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, text)))
                clickable_element = driver.find_element(By.LINK_TEXT, text)
                clickable_element.click()

                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "iframeDialog")))

                # 팝업 내부의 iframe 요소 가져오기
                iframe = driver.find_element(By.ID, "iframeDialog")
                driver.switch_to.frame(iframe)

                pophtml = driver.page_source
                popsoup = BeautifulSoup(pophtml, 'html.parser')



                title_element = popsoup.find('th', scope='col', colspan='2')
                title = title_element.get_text(strip=True)

                if any(apartment_name['apartment_name'] == title for apartment_name in apartment_names): 
                    print("중복있음 기본정보 크롤링 종료")
                    return


                rows = popsoup.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if cells:
                        # 첫 번째 셀의 텍스트 확인
                        first_cell_text = cells[0].get_text(strip=True)
                        if first_cell_text in target_keywords:
                            data = [cell.get_text(strip=True) for cell in cells]
                            
                            # 날짜 처리 로직
                            if "~" in data[1]:  # 날짜 범위일 경우
                                start, end = data[1].split("~")
                                start, end = start.strip(), end.strip()
                            else:  # 단일 날짜일 경우
                                start = end = data[1].strip()


                            
                            print(title, data[0], start, end)
                            # 데이터 삽입
                            apt_schedule_insert(title, data[0], start, end)
                # 팝업 닫기
                driver.switch_to.default_content()
                close_button = driver.find_element(By.XPATH, '/html/body/div[4]/div/button')
                close_button.click()

                time.sleep(1)

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

# apt
def apt_crawling():
    url = "https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancListView.do"
    dic = "apt"
    col = ['지역', '주택구분', '분양/임대', '주택명', '시공사', '문의처', '모집공고일', '청약기간', '담청자발표']

    base_info_crawling(url,2,34,col,apt_housing_application_basic_info_select(),apt_housing_application_basic_info_insert,3)
    competition_rate_crawling(url,apt_housing_competition_rate_select(),apt_housing_competition_rate_insert,"apt_housing_competition_rate")
    application_status_crawling(url,apt_housing_application_status_select(),apt_housing_application_status_insert,"apt_housing_application_status")
    apt_schedule_crawling(url)
    housing_application_announcement_download(url,dic)

# unranked
def unranked_craling():
    url = "https://www.applyhome.co.kr/ai/aia/selectAPTRemndrLttotPblancListView.do"
    dic = "unranked"
    col = ['지역', '주택명', '시행사', '모집공고일', '청약기간', '담청자발표']
    competition_rate_table_list = ["unranked_housing_competition_rate_1","unranked_housing_competition_rate_2"]

    base_info_crawling(url,1,36,col,unranked_housing_application_basic_info_select(),unranked_housing_application_basic_info_insert,1)
    competition_rate_crawling(url,unranked_housing_competition_rate_select(),unranked_housing_competition_rate_insert,competition_rate_table_list)
    housing_application_announcement_download(url,dic)

def get_article_image(news_url):
    try:
        # 뉴스 URL로 HTTP GET 요청
        response = requests.get(news_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')

        # 이미지 태그 추출
        img_tag = soup.find('meta', property='og:image')  # Open Graph 이미지 태그
        if img_tag and img_tag.get('content'):
            return img_tag['content']
        else:
            print("이미지를 찾을 수 없습니다.")
            return None

    except Exception as e:
        print(f"이미지 가져오기 중 오류 발생: {e}")
        return None

def naver_news_crawling():
    # 검색할 키워드 설정 (UTF-8 인코딩)
    encText1 = urllib.parse.quote("부동산 청약")
    encText2 = urllib.parse.quote("부동산 정책")

    # 두 검색어를 'and'로 결합
    query = encText1 + "+" + encText2

    # 뉴스 검색 API URL 설정 (날짜순 정렬, 10개의 기사 요청)
    url = "https://openapi.naver.com/v1/search/news?query=" + query + "&display=10&sort=sim"  # 정확도순, 10개의 기사

    # API 요청 설정
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", naver_client_id)
    request.add_header("X-Naver-Client-Secret", naver_client_secret)

    # API 호출 및 응답 처리
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    collection = "news"
    
    # 기존 데이터 삭제
    mongo_delete(collection)

    if rescode == 200:
        response_body = response.read().decode('utf-8')

        # JSON 데이터를 파싱
        news_data = json.loads(response_body)

        # 각 뉴스 아이템에서 필요한 정보를 추출하고 출력
        for item in news_data['items']:
            # HTML 태그 및 특수문자 제거
            title = html.unescape(item['title'].replace('<b>', '').replace('</b>', ''))
            link = item['link']
            description = html.unescape(item['description'].replace('<b>', '').replace('</b>', ''))
            pubDate = item['pubDate']

            # 뉴스 상세 페이지에서 이미지 URL 추출
            image_url = get_article_image(link)

            # 중복 이미지 URL 확인
            data = select(collection)
            images = [item["image"] for item in data]
            if image_url in images:
                print(f"이미 존재하는 이미지 URL: {image_url}, 저장하지 않습니다.")
                continue

            # MongoDB에 저장할 데이터
            mydict = {
                "title": title,
                "link": link,
                "description": description,
                "pubDate": pubDate,
                "image": image_url
            }

            # MongoDB에 데이터 삽입            
            mongodb_insert(collection, mydict)

            # 출력
            print(f"Title: {title}")
            print(f"Link: {link}")
            print(f"Description: {description}")
            print(f"Published Date: {pubDate}")
            print(f"Image: {image_url}")
            print("\n")
        
    else:
        print("Error Code:" + str(rescode))

if __name__ == "__main__":
    print(datetime.datetime.now())

    s3_delete_all()

    print("아파트 청약 데이터 크롤링 시작")
    apt_crawling()

    print("무순위 청약 데이터 크롤링 시작")
    unranked_craling()

    print("청약 뉴스 크롤링 시작")
    naver_news_crawling()
    print()
    print()
    pass






