import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool
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
    sleep(1)  # 대기 시간을 조정하여 웹 페이지 로드를 기다립니다.
    driver.find_element(By.CSS_SELECTOR,
                        '#content > div > div.z7cS6-TO7X > div._27jmWaPaKy > ul > li:nth-child(2) > a').click()
    sleep(2)  # 페이지 전환 대기


def collect_reviews(args):
    driver, next_list_count, first_page = args
    df = pd.DataFrame(columns=['summary', 'grade', 'review'])
    a = first_page  # 시작 페이지 번호
    page_increment = 4  # 페이지 증가량

    navigate_to_reviews(driver, "https://brand.naver.com/mayflower/products/4414087271")

    for _ in range(next_list_count):
        sleep(2)  # 페이지 로딩을 위한 대기 시간
        # 현재 페이지의 리뷰 수집
        review_elements = driver.find_elements(By.CSS_SELECTOR, '#REVIEW > ul > li')
        for review in review_elements:
            summary = review.find_element(By.CSS_SELECTOR, 'div._2FXNMst_ak').text
            grade = review.find_element(By.CSS_SELECTOR, 'div._2V6vMO_iLm > em').text
            review_text = review.find_element(By.CSS_SELECTOR, 'div._3z6gI4oI6l').text
            df = df.append({'summary': summary, 'grade': grade, 'review': review_text}, ignore_index=True)

        # 페이지 이동 로직
        if a + page_increment > 10:  # '다음' 페이지 버튼 클릭이 필요한 경우
            try:
                next_page_btn = driver.find_element(By.CSS_SELECTOR,
                                                    '#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a.fAUKm1ewwo._2Ar8-aEUTq')
                next_page_btn.click()
                sleep(2)  # '다음' 페이지 로딩 대기
            except Exception as e:
                print(f"다음 페이지 버튼 클릭 중 오류: {e}")
                break
        else:  # 특정 페이지 번호 클릭
            try:
                # 페이지 번호를 클릭하여 이동
                page_btns = driver.find_elements(By.CSS_SELECTOR,
                                                 '#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a')
                page_btns[a - 1 + page_increment].click()  # current_page는 1부터 시작하므로 -1 조정
                sleep(2)
            except Exception as e:
                print(f"페이지 {a} 이동 중 오류: {e}")
                break

        a += page_increment  # 다음 리뷰 페이지 번호 업데이트

    return df


def main():
    start_time = time.time()

    # 프로세스 풀 생성
    pool = Pool(processes=4)

    # 각 프로세스에 전달할 인자 설정
    tasks = [(setup_webdriver(), 10, i) for i in range(1, 5)]

    # 병렬 처리 실행
    results = pool.map(collect_reviews, tasks)

    # 데이터프레임 합치기
    final_df = pd.concat(results)
    final_df.to_csv('brand_crawling.csv', index=False, encoding='utf-8-sig')

    end_time = time.time()
    print("CSV 파일 저장 완료")
    print(f"크롤링 완료 시간: {end_time - start_time}초")
    print(final_df)


if __name__ == "__main__":
    main()
