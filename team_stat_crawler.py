from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import csv
import os
import time

DELAY = 5
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
driver.get(os.environ.get("K_LEAGUE_DATA_PORTAL"))


def data_center(round_number):
    # TODO: 추출할 컬럼 재정의
    # 추출할 컬럼 설정
    data = [
        "구단,상대,점유율,패스,키패스,공격진영 패스,중앙지역 패스,수비진영 패스,롱패스,중거리패스,단거리패스,전방패스,횡패스,후방패스,크로스,패스성공률(%)"
    ]
    columns = data[0].split(",")  # 컬럼 이름을 분리

    try:
        # K 리그 데이터 포털 데이터 센터 접속
        print("Connecting to data center...")
        driver.execute_script("moveMainFrame('0011');")

        print("Connecting to Match Center...")
        round_element = driver.find_element(By.ID, 'selRoundId')  # 라운드 요소 선택
        round_ = Select(round_element)
        rounds = round_.options

        # 라운드 선택 반복문
        for round_num in range(1, len(rounds)):
            time.sleep(DELAY)
            round_.select_by_index(round_num)

            match_element = driver.find_element(By.ID, 'selGameId')
            match_ = Select(match_element)
            matches = match_.options

            # 경기 선택 반복문
            for match_num in range(1, len(matches)):
                team_data_home = []  # 데이터 초기화
                team_data_away = []
                time.sleep(DELAY)
                match_.select_by_index(match_num)
                driver.execute_script("moveMainFrame('0013');")  # Match Summary

                time.sleep(DELAY)
                round_element = driver.find_element(By.ID, 'selRoundId')  # 라운드 요소 선택
                round_ = Select(round_element)
                round_.select_by_index(round_num)
                time.sleep(DELAY)
                match_element = driver.find_element(By.ID, 'selGameId')
                match_ = Select(match_element)
                match_.select_by_index(match_num)

                time.sleep(DELAY)
                print(f"Get data from {match_num} of {round_num} Round")
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table')

                # TODO: 점유율 데이터 크롤링
                if table:  # 테이블이 존재하는 경우에만 처리
                    home_team_name = driver.find_element(By.CLASS_NAME, 'main-soccer-teamName-txt')
                    away_team_name = driver.find_element(By.CLASS_NAME, 'main-soccer-teamName-txt01')
                    team_data_home.append(home_team_name.text)
                    team_data_away.append(away_team_name.text)
                    team_data_home.append(away_team_name.text)
                    team_data_away.append(home_team_name.text)

                    # data-idx="5"인 div 태그를 찾기
                    div_element = driver.find_element(By.CSS_SELECTOR, 'div.match-summary-btn-txtBox[data-idx="5"]')

                    # 그 안의 span 태그에 있는 텍스트 추출
                    span_text = div_element.find_elements(By.TAG_NAME, 'span')
                    span_text.pop(1)
                    team_data_home.append(span_text[0].text)
                    team_data_away.append(span_text[1].text)
                    print(f"Crawled data from {match_num} of {round_num} Round")
                    driver.execute_script("moveMainFrameMc('0297')")
                    data1 = driver.find_element(By.XPATH, '//*[@id="highcharts-26"]/div[2]/div[12]/span/span')
                    print(data1.text)
                    for div_num in range(1, 13):
                        home_pass_data = driver.find_element(
                            By.XPATH, f'//*[@id="highcharts-26"]/div[2]/div[{div_num}]/span/span')
                        print(home_pass_data.text)
                        team_data_home.append(home_pass_data.text)

                    data.append(team_data_home)
                    data.append(team_data_away)
                    print(data)

                    # TODO: 패스 데이터 크롤링

                match_element = driver.find_element(By.ID, 'selGameId')
                match_ = Select(match_element)

            round_element = driver.find_element(By.ID, 'selRoundId')  # 라운드 요소 선택
            round_ = Select(round_element)

    # 예외처리
    except NoSuchElementException as e:
        print(f"No such element: {e}")
    except TimeoutException as e:
        print(f"Timeout occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    # csv파일로 저장
    output_file = f"data/{round_number}-round-team-data.csv"
    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(columns)  # 컬럼 이름 작성
        writer.writerows(data[1:])  # 데이터 작성
    print(f"Saved data to {output_file}")


data_center(32)
