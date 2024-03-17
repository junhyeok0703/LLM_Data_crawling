from multiprocessing import Pool
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from time import sleep


def setup_webdriver():
    options = Options()
    options.headless = True
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def navigate_to_reviews(driver, url):
    driver.get(url)
    sleep(1)
    driver.find_element(By.CSS_SELECTOR,
                        '#content > div > div.z7cS6-TO7X > div._27jmWaPaKy > ul > li:nth-child(2) > a').click()
    sleep(2)


def collect_reviews(args):
    next_list_count, first_page = args
    driver = setup_webdriver()
    url = "https://brand.naver.com/mayflower/products/4414087271"
    navigate_to_reviews(driver, url)

    df = pd.DataFrame(columns=['summary', 'grade', 'review'])
    current_page = first_page

    for _ in range(next_list_count):
        # 페이지 로딩 대기
        sleep(2)

        # 현재 페이지의 리뷰 수집 로직
        review_elements = driver.find_elements(By.CSS_SELECTOR, '#REVIEW > ul > li')
        for review in review_elements:
            summary = review.find_element(By.CSS_SELECTOR, 'div._2FXNMst_ak').text
            grade = review.find_element(By.CSS_SELECTOR, 'div._2V6vMO_iLm > em').text
            review_text = review.find_element(By.CSS_SELECTOR, 'div._3z6gI4oI6l').text
            df = df.append({'summary': summary, 'grade': grade, 'review': review_text}, ignore_index=True)

        # 페이지 이동 로직
        # (여기에 코드 추가)

        # 다음 페이지로 업데이트
        current_page += 4

    driver.quit()
    return df


def worker_init():
    print("Initializing worker process.")


def main():
    start_time = time.time()
    tasks = [(10, i) for i in range(1, 5)]

    with Pool(processes=4, initializer=worker_init) as pool:
        results = pool.map(collect_reviews, tasks)

    final_df = pd.concat(results)
    final_df.to_csv('brand_crawling.csv', index=False, encoding='utf-8-sig')

    end_time = time.time()
    print("CSV 파일 저장 완료")
    print(f"크롤링 완료 시간: {end_time - start_time}초")


if __name__ == "__main__":
    main()
