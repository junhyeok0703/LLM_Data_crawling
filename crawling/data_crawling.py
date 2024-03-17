import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool
import time
from time import sleep

# 공유 웹 드라이버
shared_driver = None

def setup_webdriver():
    options = Options()
    options.headless = True
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def navigate_to_reviews(url):
    global shared_driver
    if shared_driver is None:
        shared_driver = setup_webdriver()  # 공유 웹 드라이버 초기화
    shared_driver.get(url)
    sleep(1)  # 대기 시간을 조정하여 웹 페이지 로드를 기다립니다.
    shared_driver.find_element(By.CSS_SELECTOR, '#content > div > div.z7cS6-TO7X > div._27jmWaPaKy > ul > li:nth-child(2) > a').click()
    sleep(2)  # 페이지 전환 대기

def collect_reviews(args):
    global shared_driver
    next_list_count, first_page = args

    try:
        url = "https://brand.naver.com/mayflower/products/4414087271"
        navigate_to_reviews(url)

        df = pd.DataFrame(columns=['summary', 'grade', 'review'])
        current_page = first_page  # 시작 페이지 번호
        page_increment = 4  # 페이지 증가량

        for _ in range(next_list_count):
            sleep(2)  # 페이지 로딩을 위한 대기 시간
            # 현재 페이지의 리뷰 수집
            review_elements = shared_driver.find_elements(By.CSS_SELECTOR, '#REVIEW > ul > li')
            for review in review_elements:
                summary = review.find_element(By.CSS_SELECTOR, 'div._2FXNMst_ak').text
                grade = review.find_element(By.CSS_SELECTOR, 'div._2V6vMO_iLm > em').text
                review_text = review.find_element(By.CSS_SELECTOR, 'div._3z6gI4oI6l').text
                df = df.append({'summary': summary, 'grade': grade, 'review': review_text}, ignore_index=True)

            # 페이지 이동 로직
            if current_page + page_increment > 10:  # '다음' 페이지 버튼 클릭이 필요한 경우
                next_page_btn = shared_driver.find_element(By.CSS_SELECTOR,
                                                    '#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a.fAUKm1ewwo._2Ar8-aEUTq')
                next_page_btn.click()
                sleep(2)  # '다음' 페이지 로딩 대기
            else:  # 특정 페이지 번호 클릭
                # 페이지 번호를 클릭하여 이동
                page_btns = shared_driver.find_elements(By.CSS_SELECTOR,
                                                 '#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a')
                page_btns[current_page - 1 + page_increment].click()  # current_page는 1부터 시작하므로 -1 조정
                sleep(2)

            current_page += page_increment  # 다음 리뷰 페이지 번호 업데이트

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        if shared_driver:
            shared_driver.quit()

    return df
