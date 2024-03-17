
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

#brand

target_url = 'https://brand.naver.com/mayflower/products/4414087271'
next_list_count = 1  #다음버튼 즉 1~10에서 11~20으로 가게
sleepDelay = 1
df = pd.DataFrame(columns=['summary','grade', 'review'])# 요약, 상품리뷰
df_idx = 0

#대충 웹드라이브 크롬이랑 맞춰서 설치 ㅇㅇ
service = Service()
browser = webdriver.Chrome(service=service)
sleep(sleepDelay * 3)
browser.get(target_url)
sleep(sleepDelay)


#리뷰클릭
browser.find_element(By.CSS_SELECTOR, '#content > div > div.z7cS6-TO7X > div._27jmWaPaKy > ul > li:nth-child(2) > a').click()
sleep(sleepDelay * 2)

#다음 몇변 누를지
while next_list_count > 0:
    #1~10페이지중 몇까지 갈지
    for page in range(2, 7):
        try:
            browser.find_element(By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a:nth-child({str(page)}').click() #리뷰페이지변환
            #REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > ul > li:nth-child(1) > div > div > div > div._3-1uaKhzq4 > div > div._1McWUwk15j > div._3i1mVq_JBd > div._3HKlxxt8Ii > div._2V6vMO_iLm > em
            #REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > ul > li:nth-child(1) > div > div > div > div._3-1uaKhzq4 > div > div._1McWUwk15j > div._3i1mVq_JBd > div._3HKlxxt8Ii > div._2FXNMst_ak
            sleep(sleepDelay)
            for review_number in range(1,20+1):
                #리뷰데이터 추출
                review_table = browser.find_elements(By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > ul > li:nth-child({str(review_number)}')
                for review in review_table:
                    df.loc[df_idx] = [review.find_element(By.CSS_SELECTOR, 'div._2FXNMst_ak').text,review.find_element(By.CSS_SELECTOR, 'div._2V6vMO_iLm > em').text, review.find_element(By.CSS_SELECTOR, f'div._3z6gI4oI6l').text]
                    df_idx += 1

        except:
            print("마지막 페이지")
            break


    try:
        #다음 누르기
        browser.find_element(By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a.fAUKm1ewwo._2Ar8-aEUTq').click()
        next_list_count -= 1
        sleep(sleepDelay)

    except:
        print("마지막 목록")
        break

print("크롤링 완료")

browser.quit()
df.to_csv('크롤링_결과.csv', index=False, encoding='utf-8-sig')
print("CSV 파일 저장 완료")
print(df)
