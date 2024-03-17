import time
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Pool


def setup_webdriver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def navigate_to_reviews(driver, url, start_page):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#content > div > div.z7cS6-TO7X > div._27jmWaPaKy > ul > li:nth-child(2) > a'))
    ).click()
    # 이동할 시작 페이지 설정
    if start_page > 1:
        driver.get(f"{url}&page={start_page}")


def collect_reviews(start_page):
    driver = setup_webdriver()
    target_url = 'https://brand.naver.com/goldhome/products/4884369353'
    navigate_to_reviews(driver, target_url, start_page)

    df = pd.DataFrame(columns=['summary', 'grade', 'review'])
    df_idx = 0
    next_list_count = 5  # 예시로 설정한 값, 필요에 따라 조정

    # 페이지네이션을 따라가며 데이터 수집
    while next_list_count > 0:
        try:
            review_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, '#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > ul > li'))
            )
            for review in review_elements:
                summary = review.find_element(By.CSS_SELECTOR, 'div._2FXNMst_ak').text
                grade = review.find_element(By.CSS_SELECTOR, 'div._2V6vMO_iLm > em').text
                review_text = review.find_element(By.CSS_SELECTOR, 'div._3z6gI4oI6l').text
                df.loc[df_idx] = [summary, grade, review_text]
                df_idx += 1
            # 다음 페이지로 이동
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            '#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a.fAUKm1ewwo._2Ar8-aEUTq'))
            )
            next_button.click()
            sleep(1)
            next_list_count -= 1
        except Exception as e:
            print(f"Error while navigating: {e}")
            break

    driver.quit()
    return df


def main():
    start_time = time.time()
    num_processes = 4  # 사용할 프로세스 수
    start_pages = [1, 2, 3, 4]  # 각 프로세스의 시작 페이지

    with Pool(num_processes) as p:
        results = p.map(collect_reviews, start_pages)

    # 데이터프레임 병합
    final_df = pd.concat(results)
    final_df.to_csv('brand_crawling_parallel.csv', index=False, encoding='utf-8-sig')

    end_time = time.time()
    print(f"크롤링 완료 시간: {end_time - start_time}초")


if __name__ == "__main__":
    main()
