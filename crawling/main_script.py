import pandas as pd
from multiprocessing import Pool
import time

# collect_reviews 함수와 setup_webdriver 함수 import
from data_crawling import collect_reviews, setup_webdriver

def main():
    start_time = time.time()
    global shared_driver
    shared_driver = setup_webdriver()  # 공유 웹 드라이버 초기화
    tasks = [(10, i) for i in range(1, 5)]  # 병렬 작업에 전달할 인자 설정 (next_list_count, first_page)

    with Pool(processes=4) as pool:  # 병렬 처리 실행
        results = pool.map(collect_reviews, tasks)

    final_df = pd.concat(results)  # 결과 데이터프레임 합치기
    final_df.to_csv('brand_crawling.csv', index=False, encoding='utf-8-sig')

    end_time = time.time()
    print("CSV 파일 저장 완료")
    print(f"크롤링 완료 시간: {end_time - start_time}초")
    print(final_df)

if __name__ == "__main__":
    main()
