import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options

def scroll_to_top(driver):
    """페이지를 맨 위로 스크롤"""
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
 
def get_faq_content(driver):
    """현재 탭의 FAQ 내용을 가져옵니다."""
    faq_list = []
    dl_elements = driver.find_elements(By.CLASS_NAME, "new_faq_dl")
    
    for dl in dl_elements:
        question = dl.find_element(By.TAG_NAME, "p").text
        
        try:
            dl.find_element(By.TAG_NAME, "dt").click()
            time.sleep(0.5)
        except:
            pass
        
        answer = dl.find_element(By.TAG_NAME, "dd").text
        
        faq_list.append({
            'question': question,
            'answer': answer
        })
        
    return faq_list

def crawl_all_tabs():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        url = "https://www.applyhome.co.kr/cu/cub/selectFAQList.do#faqSub0"
        driver.get(url)
        
        time.sleep(3)
        
        scroll_to_top(driver)
        
        all_faqs = []
        
        for i in range(5):
            sub_id = f"faqSub{i}"
            try:
                sub_button = driver.find_element(By.CSS_SELECTOR, f'a[href="#{sub_id}"]')
                sub_button.click()
                time.sleep(2)
                
                faqs = get_faq_content(driver)
                all_faqs.extend(faqs)
                
            except Exception as e:
                print(f"Error on tab {sub_id}: {e}")
        
        return all_faqs
        
    finally:
        driver.quit()

try:
    all_faqs = crawl_all_tabs()
    
    for i, faq in enumerate(all_faqs, 1):
        print(f"\nQ{i}. {faq['question']}")
        print(f"A{i}. {faq['answer']}\n")
        print("-" * 80)
    
    with open("./data/all_faqs.json", 'w', encoding='utf-8') as f:
        json.dump(all_faqs, f, indent=4, ensure_ascii=False)  # JSON 저장 시 UTF-8 설정
        
except Exception as e:
    print(f"오류 발생: {str(e)}")