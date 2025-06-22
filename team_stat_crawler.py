from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import re
import os
import time
import numpy as np
import pandas as pd

FIXED_DELAY = 3
DELAY = 15  # 최대 대기 시간 (초)
MEET_YEAR = 2
SEQ = 1

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
driver.get(os.environ.get("K_LEAGUE_DATA_PORTAL"))

wait = WebDriverWait(driver, DELAY)

def data_center(meet_year, seq):
    data = [
        ["년도", "라운드", "구단", "감독", "상대", "득점", "실점", "점유율", "패스성공률(%)", "패스 성공", "키패스", "공격진영 패스",
         "중앙지역 패스", "수비진영 패스", "롱패스", "중거리패스", "단거리패스", "전방패스", "횡패스", "후방패스", "크로스"]
    ]

    try:
        print("Connecting to data center...")
        driver.execute_script("moveMainFrame('0011');")

        print("Connecting to Match Center...")
        year_element = wait.until(EC.presence_of_element_located((By.ID, 'selMeetYear')))
        year_select = Select(year_element)
        year_select.select_by_index(MEET_YEAR)
        time.sleep(FIXED_DELAY)

        print("Selecting Match Year")
        seq_element = wait.until(EC.presence_of_element_located((By.ID, 'selMeetSeq')))
        seq_select = Select(seq_element)
        seq_select.select_by_index(SEQ)
        time.sleep(FIXED_DELAY)

        round_element = wait.until(EC.presence_of_element_located((By.ID, 'selRoundId')))
        round_select = Select(round_element)
        rounds = round_select.options
        print("Selecting Match Round")

        for round_num in range(9, len(rounds)):
            time.sleep(FIXED_DELAY)
            round_element = wait.until(EC.element_to_be_clickable((By.ID, 'selRoundId')))
            round_select = Select(round_element)
            round_select.select_by_index(round_num)

            match_element = wait.until(EC.presence_of_element_located((By.ID, 'selGameId')))
            match_select = Select(match_element)
            matches = match_select.options

            for match_num in range(1, len(matches)):
                time.sleep(FIXED_DELAY)
                team_data_home = []
                team_data_away = []

                match_element = wait.until(EC.element_to_be_clickable((By.ID, 'selGameId')))
                match_select = Select(match_element)
                match_select.select_by_index(match_num)

                driver.execute_script("moveMainFrame('0013');")  # Match Summary

                year_element = wait.until(EC.presence_of_element_located((By.ID, 'selMeetYear')))
                year_select = Select(year_element)
                year_select.select_by_index(MEET_YEAR)

                print("Selecting Match Year")
                seq_element = wait.until(EC.presence_of_element_located((By.ID, 'selMeetSeq')))
                seq_select = Select(seq_element)
                print(seq_element)
                seq_select.select_by_index(SEQ)

                # 라운드 재설정
                round_element = wait.until(EC.element_to_be_clickable((By.ID, 'selRoundId')))
                round_select = Select(round_element)
                round_select.select_by_index(round_num)

                # 경기 재설정
                match_element = wait.until(EC.element_to_be_clickable((By.ID, 'selGameId')))
                match_select = Select(match_element)
                match_select.select_by_index(match_num)

                print(f"Get data from match {match_num} of round {round_num}")
                wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table')

                if table:
                    print("Table found")
                    home_team_name = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'main-soccer-teamName-txt')))
                    away_team_name = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'main-soccer-teamName-txt01')))
                    score = driver.find_elements(By.CSS_SELECTOR, '.main-soccer-teamName-txt02')
                    managers = driver.find_elements(By.CSS_SELECTOR, '.main-soccer-txt02.mt5')

                    team_data_home.extend([meet_year, round_num, home_team_name.text, managers[0].text.strip(), away_team_name.text])
                    team_data_away.extend([meet_year, round_num, away_team_name.text, managers[1].text.strip(), home_team_name.text])
                    print(team_data_home)
                    print(team_data_away)

                    div_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.match-summary-btn-txtBox[data-idx="5"]'))
                    )
                    span_text = div_element.find_elements(By.TAG_NAME, 'span')
                    span_text.pop(1)
                    team_data_home.append(span_text[0].text)
                    team_data_away.append(span_text[1].text)

                    button = wait.until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//*[@id="msForm"]/div[2]/div[1]/div/div/ul/li[7]/div/div[3]/button'))
                    )
                    button.click()
                    print('clicked button')

                    try:
                        pass_element = wait.until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, 'match-summary-btn-middle-detail')))
                        pass_text = pass_element[0].text
                        print("원본 pass_text:", pass_text)
                        pass_text = re.findall(r'\((\d{2})\)', pass_text)
                        print("추출된 pass_text 리스트:", pass_text)

                        if len(pass_text) >= 2:
                            team_data_home.append(pass_text[0])
                            team_data_away.append(pass_text[1])
                        else:
                            print("❗ 패스 관련 수치가 부족합니다. None으로 채웁니다.")
                            team_data_home.append(None)
                            team_data_away.append(None)

                    except (IndexError, TimeoutException) as e:
                        print(f"❗ 패스 데이터 추출 중 오류 발생: {e}")
                        team_data_home.append(None)
                        team_data_away.append(None)

                    driver.execute_script("moveMainFrameMc('0297')")

                    for label in range(1, 13):
                        xpath = f'/html/body/div[1]/div[6]/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[{label}]/span/span'
                        teamstats_label = wait.until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )

                        # text가 비어있지 않을 때까지 대기
                        WebDriverWait(driver, 10).until(
                            lambda d: driver.execute_script("return arguments[0].textContent",
                                                            teamstats_label).strip() != '')

                        stat_text = driver.execute_script("return arguments[0].textContent", teamstats_label).strip()
                        team_data_home.append(stat_text)
                    data.append(team_data_home)

                    for label in range(1, 13):
                        xpath = f'/html/body/div[1]/div[6]/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[3]/div[{label}]/span/span'
                        teamstats_label = wait.until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )

                        WebDriverWait(driver, 10).until(
                            lambda d: driver.execute_script("return arguments[0].textContent",
                                                            teamstats_label).strip() != '')

                        stat_text = driver.execute_script("return arguments[0].textContent", teamstats_label).strip()
                        team_data_away.append(stat_text)
                    data.append(team_data_away)
                    print(f"Crawled data from match {match_num} of round {round_num}")
                    print(team_data_home)
                else:
                    print(f"No table founded")
                    break

    except NoSuchElementException as e:
        print(f"No such element: {e}")
    except TimeoutException as e:
        print(f"Timeout occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    # 데이터프레임 변환
    df = pd.DataFrame(data[1:], columns=data[0])

    # 숫자형 변환 (필요한 컬럼)
    numeric_cols = ['패스 성공', '패스성공률(%)', '공격진영 패스', '단거리패스', '전방패스']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['패스성공률(%)'] = df['패스성공률(%)'] / 100
    df['패스'] = np.floor(df['패스 성공'] / (df['패스성공률(%)']))
    df['공격진영 패스 비율'] = df['공격진영 패스'] / df['패스']
    df['단거리패스 비율'] = df['단거리패스'] / df['패스']
    df['전방패스 비율'] = df['전방패스'] / df['패스']

    output_file = f"data/{meet_year}-{seq}-team-data.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Saved data to {output_file}")


data_center(2023, '하나은행 K리그1-9')
