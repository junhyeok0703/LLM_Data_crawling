import time
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def setup_webdriver():
    options = Options()
    options.headless = True
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def navigate_to_reviews(driver, url):
    driver.get(url)
    sleep(1)  # 대기 시간을 조정하여 웹 페이지 로드를 기다립니다.
    driver.find_element(By.CSS_SELECTOR, '#content > div > div.z7cS6-TO7X > div._27jmWaPaKy > ul > li:nth-child(2) > a').click()
    sleep(2)

def collect_reviews(driver, next_list_count):
    df = pd.DataFrame(columns=['summary', 'grade', 'review'])
    df_idx = 0
    while next_list_count > 0:
        for page in range(2, 11):  #리뷰 페이지 1에서 시작 10까지
            try:
                driver.find_element(By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a:nth-child({str(page)}').click()
                sleep(1)
                for review_number in range(1, 21):
                    review_table = driver.find_elements(By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > ul > li:nth-child({str(review_number)}')
                    for review in review_table:
                        summary = review.find_element(By.CSS_SELECTOR, 'div._2FXNMst_ak').text
                        grade = review.find_element(By.CSS_SELECTOR, 'div._2V6vMO_iLm > em').text
                        review_text = review.find_element(By.CSS_SELECTOR, 'div._3z6gI4oI6l').text
                        df.loc[df_idx] = [summary, grade, review_text]
                        df_idx += 1
            except Exception as e:
                print("페이지 로딩 중 오류 발생:", e)
                break
        try:
            driver.find_element(By.CSS_SELECTOR, '#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a.fAUKm1ewwo._2Ar8-aEUTq').click()
            next_list_count -= 1
            sleep(1)
        except:
            print("마지막 목록에 도달했습니다.")
            break
    return df

def main():
    start_time = time.time()
    target_url = 'https://brand.naver.com/mayflower/products/2267603786'
    driver = setup_webdriver()
    navigate_to_reviews(driver, target_url)
    df = collect_reviews(driver, 10)  # 'next_list_count'를 조정하여 필요한 만큼의 페이지를 넘길 수 있습니다.
    driver.quit()
    df.to_csv('brand_cawing.csv', index=False, encoding='utf-8-sig')
    print("CSV 파일 저장 완료")
    end_time = time.time()
    print(f"크롤링 완료 시간: {end_time - start_time}초")
    print(df)

if __name__ == "__main__":
    main()
