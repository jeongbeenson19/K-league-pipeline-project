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
        "년도,선수명,구단,포지션,등번호,출전시간(분),"
        "득점,도움,슈팅,유효 슈팅,차단된슈팅,벗어난슈팅,PA내 슈팅,PA외 슈팅,"
        "오프사이드,프리킥,코너킥,스로인,"
        "드리블 시도,드리블 성공,드리블 성공%,"
        "패스 시도,패스 성공,패스 성공%,키패스,전방 패스 시도,전방 패스 성공,전방 패스 성공%,후방 패스 시도,후방 패스 성공,후방 패스 성공%,"
        "횡패스 시도,횡패스 성공,횡패스 성공%,"
        "공격지역패스 시도,공격지역패스 성공,공격지역패스 성공%,수비지역패스 시도,수비지역패스 성공,수비지역패스 성공%,"
        "중앙지역패스 시도,중앙지역패스 성공,중앙지역패스 성공%,롱패스 시도,롱패스 성공,롱패스 성공%,중거리패스 시도,중거리패스 성공,중거리패스 성공%,"
        "숏패스 시도,숏패스 성공,숏패스 성공%,크로스 시도,크로스 성공,크로스 성공%,"
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
        driver.execute_script("setDisplayMenu('subMenuLayer', '0207');")  # 선수기록
        driver.execute_script("javascript:moveMainFrame('0373');")  # 년도별 선수기록
        meeting_element = driver.find_element(By.ID, 'selectMeetSeq')  # 대회 요소 선택
        meeting = Select(meeting_element)
        meetings = meeting.options

        # K리그1 & K리그2 데이터 수집을 위한 반복문
        for meet_index in range(1, len(meetings)):  # 첫 번째 옵션은 '선택'이므로 건너뜀
            print(f"Selecting meeting {meet_index} of {len(meetings) - 1}")
            meeting.select_by_index(meet_index)
            time.sleep(DELAY)

            # 팀 선택 박스를 다시 가져와서 Select 객체를 새로 만듦
            team_element = driver.find_element(By.ID, 'selectTeamId')
            team = Select(team_element)
            options = team.options

            # 대회별 출전 팀별 데이터 수집을 위한 반복문
            for index in range(1, len(options)):  # 첫 번째 옵션은 '선택'이므로 건너뜀
                print(f"Selecting team {index} of {len(options) - 1}")
                team.select_by_index(index)

                button_search = driver.find_element(By.ID, 'btnSearch')
                button_search.click()

                time.sleep(DELAY)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table')

                if table:  # 테이블이 존재하는 경우에만 처리
                    team_name = soup.find('p', id='txtTeamName').text
                    print(team_name)
                    rows = table.find_all('tr')
                    for row in rows[2:-1]:
                        cols = row.find_all(['td', 'th'])  # 'td'와 'th' 모두 찾기
                        cols = [ele.text.strip() for ele in cols]  # 텍스트를 추출하고 공백 제거
                        cols.insert(2, team_name)
                        data.append(cols)

                # 다음 옵션을 선택하기 위해 Select 객체를 다시 생성
                team_element = driver.find_element(By.ID, 'selectTeamId')
                team = Select(team_element)

            # 다음 옵션을 선택하기 위해 Select 객체를 다시 생성
            meeting_element = driver.find_element(By.ID, 'selectMeetSeq')
            meeting = Select(meeting_element)

    except NoSuchElementException as e:
        print(f"No such element: {e}")
    except TimeoutException as e:
        print(f"Timeout occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    # csv파일로 저장
    output_file = f"data/{round_number}-round-data.csv"
    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(columns)  # 컬럼 이름 작성
        writer.writerows(data[1:])  # 데이터 작성
