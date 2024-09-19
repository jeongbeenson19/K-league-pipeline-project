from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import time
import csv
import os

DELAY = 3
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
driver.get(os.environ.get("K_LEAGUE_DATA_PORTAL"))


def data_center(round_number):

    # 추출할 컬럼 설정
    data = [
        "년도,구단,"
        "득점,도움,슈팅,유효 슈팅,블락된슈팅,벗어난슈팅,PA내 슈팅,PA외 슈팅,"
        "프리킥 슈팅, 프리킥 유효슈팅, 프리킥 크로스 시도, 프리킥 크로스 성공, 프리킥 크로스 성공%,"
        "오프사이드,코너킥,스로인,"
        "드리블 시도,드리블 성공,드리블 성공%,"
        "패스 시도,패스 성공,패스 성공%,키패스,전방 패스 시도,전방 패스 성공,전방 패스 성공%,후방 패스 시도,후방 패스 성공,후방 패스 성공%,"
        "횡패스 시도,횡패스 성공,횡패스 성공%,"
        "공격진영패스 시도,공격진영패스 성공,공격진영패스 성공%,수비진영패스 시도,수비진영패스 성공,수비진영패스 성공%,"
        "중앙진영패스 시도,중앙진영패스 성공,중앙진영패스 성공%,롱패스 시도,롱패스 성공,롱패스 성공%,중거리패스 시도,중거리패스 성공,중거리패스 성공%,"
        "단거리패스 시도,단거리패스 성공,단거리패스 성공%,크로스 시도,크로스 성공,크로스 성공%,"
        "경합 지상 시도,경합 지상 성공,경합 지상 성공%,경합 공중 시도,경합 공중 성공,경합 공중 성공%,태클 시도,태클 성공,태클 성공%,"
        "클리어링,인터셉트,차단,획득,블락,볼미스,파울,피파울,경고,퇴장"
    ]
    columns = data[0].split(",")  # 컬럼 이름을 분리

    try:
        # K 리그 데이터 포털 데이터 센터 접속
        print("Connecting to data center...")
        time.sleep(DELAY)
        driver.execute_script("moveMainFrame('0011');")

        print("Connecting to Additional record...")
        time.sleep(DELAY)
        driver.execute_script("moveMainFrame('0194');")  # 부가기록
        driver.execute_script("setDisplayMenu('subMenuLayer', '0195');")  # 팀기록
        driver.execute_script("javascript:moveMainFrame('0197');")  # 년도별 팀기록
        meeting_element = driver.find_element(By.ID, 'selectMeetSeq')  # 대회 요소 선택
        meeting = Select(meeting_element)
        meeting.select_by_index(0)
        time.sleep(DELAY)

        button_search = driver.find_element(By.ID, 'btnSearch')
        button_search.click()

        print("Searching...")

        time.sleep(DELAY)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')

        if table:  # 테이블이 존재하는 경우에만 처리
            rows = table.find_all('tr')
            for row in rows[2:-1]:
                cols = row.find_all(['td', 'th'])  # 'td'와 'th' 모두 찾기
                cols = [ele.text.strip() for ele in cols]  # 텍스트를 추출하고 공백 제거
                data.append(cols)

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
