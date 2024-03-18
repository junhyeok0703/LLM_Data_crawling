import time
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_webdriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver
def navigate_to_reviews(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#content > div > div.z7cS6-TO7X > div._27jmWaPaKy > ul > li:nth-child(2) > a'))
    ).click()

def collect_reviews(driver, next_list_count):
    df = pd.DataFrame(columns=['summary', 'grade', 'review'])
    df_idx = 0
    while next_list_count > 0:
        for page in range(2, 7):
            try:
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a:nth-child({str(page)})'))
                ).click()
                sleep(1)
                review_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > ul > li'))
                )
                for review in review_elements:
                    summary = review.find_element(By.CSS_SELECTOR, 'div._2FXNMst_ak').text
                    grade = review.find_element(By.CSS_SELECTOR, 'div._2V6vMO_iLm > em').text
                    review_text = review.find_element(By.CSS_SELECTOR, 'div._3z6gI4oI6l').text
                    df.loc[df_idx] = [summary, grade, review_text]
                    df_idx += 1
            except Exception as e:
                print(f"페이지 로딩 중 오류 발생: {e}")
                break

        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a.fAUKm1ewwo._2Ar8-aEUTq'))
            ).click()
            next_list_count -= 1
        except Exception as e:
            print("마지막 목록에 도달했습니다.", e)
            break
    return df

def main():
    start_time = time.time()
    target_url = 'https://brand.naver.com/goldhome/products/4884369353?NaPm=ct%3Dltvdojbc%7Cci%3Da25b2af35d52dcbbd2b7c41ed6e1dee848bb168b%7Ctr%3Dslcc%7Csn%3D671050%7Chk%3D3e6462f9700d1cc05cd16aeddf05d8bc4865fd22'
    print("크롤링을 시작합니다...")
    driver = setup_webdriver()
    navigate_to_reviews(driver, target_url)
    df = collect_reviews(driver, 1000)
    driver.quit()
    df.to_csv('brand_crawling2.csv', index=False, encoding='utf-8-sig')
    print("CSV 파일 저장 완료")
    end_time = time.time()
    print(f"크롤링 완료 시간: {end_time - start_time}초")

if __name__ == "__main__":
    main()
