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

keys = Keys()

target_url = 'https://brand.naver.com/labnoshmall/products/6424979696'
next_list_count = 100
sleepDelay = 1
df = pd.DataFrame(columns=['review', 'one_month', 'repeat_purchase'])
df_idx = 0

service = Service()
browser = webdriver.Chrome(service=service)
sleep(sleepDelay * 3)
browser.get(target_url)
sleep(sleepDelay)

browser.find_element(By.CSS_SELECTOR,
                     '#content > div > div.z7cS6-TO7X > div._27jmWaPaKy > ul > li:nth-child(2) > a').click()
sleep(sleepDelay * 2)

start_time = time.time()  # 크롤링 시작 시간 기록

while next_list_count > 0:

    for page in range(2, 12):
        try:
            browser.find_element(By.CSS_SELECTOR,
                                 f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a:nth-child({str(page)}').click()  # 각 페이지 클릭
            sleep(sleepDelay)

            for review_number in range(1, 20 + 1):

                review_table = browser.find_elements(By.CSS_SELECTOR,
                                                     f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > ul > li:nth-child({str(review_number)}')
                for review in review_table:
                    df.loc[df_idx] = [review.find_element(By.CSS_SELECTOR, f'div._3z6gI4oI6l').text, "-", "-"]
                    df_idx += 1

        except:
            print("마지막 페이지")
            break

    try:
        browser.find_element(By.CSS_SELECTOR,
                             f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a.fAUKm1ewwo._2Ar8-aEUTq').click()
        next_list_count -= 1
        sleep(sleepDelay)

    except:
        print("마지막 목록")
        break

end_time = time.time()  # 크롤링 종료 시간 기록
elapsed_time = end_time - start_time  # 소요된 시간 계산

print("크롤링 완료")
print(f"소요된 시간: {elapsed_time} 초")

csv_file_name = '크롤링.csv'
df.to_csv(csv_file_name, index=False, encoding='utf-8-sig')
print(f"{csv_file_name} 파일로 저장 완료!")

browser.quit()

print(df.head())
