from selenium import webdriver
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


def xg_crawler(round_number):
    try:
        xg_data = ["순위,선수명,구단,출전수,출전시간(분),슈팅,득점,xG,득점/xG,90분당 xG"]
        xg_columns = xg_data[0].split(",")
        # K 리그 데이터 포털 데이터 센터 접속
        print("Connecting to data center...")
        time.sleep(DELAY)
        driver.execute_script("moveMainFrame('0011');")

        print("Connecting to Additional record...")
        time.sleep(DELAY)
        driver.execute_script("moveMainFrame('0194');")  # 부가기록
        driver.execute_script("setDisplayMenu('subMenuLayer', '0432')")  # 기대득점
        driver.execute_script("moveMainFrame('0433');")
        html = driver.page_source
        xg_soup = BeautifulSoup(html, "html.parser")
        xg_table = xg_soup.find("table")

        if xg_table:  # 테이블이 존재하는 경우에만 처리
            xg_rows = xg_table.find_all('tr')
            for row in xg_rows[1:]:
                cols = row.find_all(['td', 'th'])  # 'td'와 'th' 모두 찾기
                cols = [ele.text.strip() for ele in cols]  # 텍스트를 추출하고 공백 제거
                xg_data.append(cols)
        else:
            print("No data found")
    except NoSuchElementException as e:
        print(f"No such element: {e}")
    except TimeoutException as e:
        print(f"Timeout occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
    # csv파일로 저장
    xg_output_file = f"data/{round_number}-round-xg.csv"
    with open(xg_output_file, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(xg_columns)  # 컬럼 이름 작성
        writer.writerows(xg_data[1:])  # 데이터 작성
    print(f"Data has been written to \n{xg_output_file}")
