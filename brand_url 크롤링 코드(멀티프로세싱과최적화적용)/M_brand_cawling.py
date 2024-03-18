import re
import time
from time import sleep
import re, requests, csv
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
import konlpy
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import PIL
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Pool
import time

# 멀티 프로세싱 적용 + 최적화코드 + brand url 크롤링코드 (거의 최종) 25초 -> 20초 -> 18초
# 남은거 로딩시간줄이기, 중간에 sleep 줄이기

def collect_reviews(args):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from time import sleep
    import pandas as pd

    next_list_count, first_page = args
    options = Options()
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
    # 사용자 에이전트 설정
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    df = pd.DataFrame(columns=['num', 'summary', 'grade', 'review'])

    df_idx = 0  # 데이터프레임 인덱스 초기화

    try:
        url = "https://brand.naver.com/mayflower/products/2267603786"
        driver.get(url)
        sleep(2)  # 페이지 로딩 대기

        # 첫 번째 코드에서 제공된 선택자를 적용하여 리뷰 탭으로 이동
        driver.find_element(By.CSS_SELECTOR,
                            '#content > div > div.z7cS6-TO7X > div._27jmWaPaKy > ul > li:nth-child(2) > a').click()
        sleep(3)  # 리뷰 탭 로딩 대기
        while next_list_count > 0:
            for page in range((first_page - 1) * 3 + 2, (
                                                                first_page - 1) * 3 + 5):  # 리뷰 페이지를 설정하여서 처음페이지는 프로세스의 번호가 first_page가 된다 즉 1번프로세스면 1+1부터 2부터 시작하게 시작한다.  그후에 page+4를 하여 프로세스수만큼 증가하면서 서로 다른 페이지를 돌면서 리스트에 저장하게 된다.
                try:
                    driver.find_element(By.CSS_SELECTOR,
                                        f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a:nth-child({page})').click()
                    sleep(1)
                    now_page_html = driver.find_element(By.CSS_SELECTOR,
                                                        f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div').get_attribute(
                        'innerHTML')
                    soup = BeautifulSoup(now_page_html, 'html.parser')
                    target_elements = soup.find_all('a', {'aria-current': 'true', 'role': 'menuitem'})
                    base_num = 0
                    for elem in target_elements:
                        base_num = (((int)(elem.text)) - 1) * 20
                    df_idx = 0
                    for review_number in range(1, 21):
                        review_table = driver.find_elements(By.CSS_SELECTOR,
                                                            f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > ul > li:nth-child({review_number})')
                        for review in review_table:
                            summary = review.find_element(By.CSS_SELECTOR, 'div._2FXNMst_ak').text
                            grade = review.find_element(By.CSS_SELECTOR, 'div._2V6vMO_iLm > em').text
                            review_text = review.find_element(By.CSS_SELECTOR, 'div._3z6gI4oI6l').text
                            df.loc[base_num + df_idx] = [base_num + df_idx, summary, grade, review_text]
                            print(f"리뷰 추가됨: {df_idx}, {summary}, {grade}, {review_text}")  # 리뷰가 추가될 때마다 출력
                            df_idx += 1
                except Exception as e:
                    print("페이지 로딩 중 오류 발생:", e)
                    break
            try:
                driver.find_element(By.CSS_SELECTOR,
                                    '#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a.fAUKm1ewwo._2Ar8-aEUTq').click()
                next_list_count -= 1
                sleep(1)
            except Exception as e:
                print("다음 페이지 목록으로 이동 중 오류 발생:", e)
                break

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        driver.quit()

    return df


def main():
    start_time = time.time()
    tasks = [(10, i) for i in range(1, 5)]

    with Pool(processes=4) as pool:
        results = pool.map(collect_reviews, tasks)

    final_df = pd.concat(results)
    final_df.sort_values(by=['num'], inplace=True)
    final_df.drop_duplicates(subset=['num'], keep='first', inplace=True)
    final_df.reset_index(drop=True, inplace=True)
    final_df.to_csv('brand_crawling.csv', index=False, encoding='utf-8-sig')

    end_time = time.time()
    print("CSV 파일 저장 완료")
    print(f"크롤링 완료 시간: {end_time - start_time}초")
    print(final_df)
    print(final_df.index)


if __name__ == "__main__":
    main()