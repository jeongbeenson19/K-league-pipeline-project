import os
import numpy as np
import pandas as pd


# 변환 적용을 위한 쉼표 제거를 위한 함수
def remove_commas(value):
    if isinstance(value, str):
        return value.replace(",", "")
    return value


# 변환 적용을 위한 쉼표 제거 및 정수 변환 함수
def convert_to_int(value):
    value = remove_commas(value)
    try:
        return int(value)
    except ValueError:
        return value


# 전처리 함수
def preprocessing(round_number):
    # CSV 파일 경로
    input_data_file = f'data/{round_number}-round-data.csv'
    input_xg_file = f'data/{round_number}-round-xg.csv'
    input_team_data_file = f'data/{round_number}-round-team-data.csv'
    output_preprocessed_file = f'data/preprocessed/{round_number}-round-preprocessed.csv'

    # 파일이 존재하는지 확인
    if not os.path.exists(input_data_file):
        print(f"Input data files for round {round_number} do not exist. Crawling data...")
        import crawler
        player_data = crawler.data_center(round_number=round_number)

    if not os.path.exists(input_xg_file):
        print(f"Input xG data files for round {round_number} do not exist. Crawling data...")
        import xG_crawler
        xG = xG_crawler.xg_crawler(round_number=round_number)

    if not os.path.exists(input_team_data_file):
        print(f"Input team data files for round {round_number} do not exist. Crawling data")
        import team_stat_crawler
        team_stat = team_stat_crawler.data_center(round_number=round_number)

    data = pd.read_csv(input_data_file)
    xg_data = pd.read_csv(input_xg_file)
    team_data = pd.read_csv(input_team_data_file)
    df = pd.DataFrame(data)

    # 드리블 성공% 및 패스 성공% 등 퍼센트 컬럼에 대해서는 따로 처리하지 않음
    percent_columns = [
        '드리블 성공%', '패스 성공%', '전방 패스 성공%', '후방 패스 성공%', '횡패스 성공%',
        '공격지역패스 성공%', '수비지역패스 성공%', '중앙지역패스 성공%', '롱패스 성공%', '중거리패스 성공%',
        '숏패스 성공%', '크로스 성공%', '경합 지상 성공%', '경합 공중 성공%', '태클 성공%'
    ]

    # HTML에서 추출된 문자열로 이루어진 데이터를 정수형으로 변환
    for col in df.columns:
        if col not in percent_columns:
            df[col] = df[col].apply(convert_to_int)

    # MF와 FW가 함께 존재하는 경우 FW로 처리
    def resolve_position(positions):
        if 'FW' in positions.values:
            return 'FW'
        elif 'MF' in positions.values:
            return 'MF'
        else:
            return positions.iloc[0]

    # 선수 이름과 포지션을 기준으로 그룹화하여 합계 계산
    # 합계를 구할 수 없는 열(예: 선수 이름, 포지션 등)은 첫 번째 값으로 대체
    grouped_df = df.groupby(['선수명', '구단'], as_index=False).agg(
        {
            '선수명': 'first',
            '구단': 'first',
            '포지션': resolve_position,
            '등번호': 'first',
            '출전시간(분)': 'sum',
            '득점': 'sum',
            '도움': 'sum',
            '슈팅': 'sum',
            '유효 슈팅': 'sum',
            '차단된슈팅': 'sum',
            '벗어난슈팅': 'sum',
            'PA내 슈팅': 'sum',
            'PA외 슈팅': 'sum',
            '오프사이드': 'sum',
            '프리킥': 'sum',
            '코너킥': 'sum',
            '스로인': 'sum',
            '드리블 시도': 'sum',
            '드리블 성공': 'sum',
            '드리블 성공%': 'mean',
            '패스 시도': 'sum',
            '패스 성공': 'sum',
            '패스 성공%': 'mean',
            '키패스': 'sum',
            '전방 패스 시도': 'sum',
            '전방 패스 성공': 'sum',
            '전방 패스 성공%': 'mean',
            '후방 패스 시도': 'sum',
            '후방 패스 성공': 'sum',
            '후방 패스 성공%': 'mean',
            '횡패스 시도': 'sum',
            '횡패스 성공': 'sum',
            '횡패스 성공%': 'mean',
            '공격지역패스 시도': 'sum',
            '공격지역패스 성공': 'sum',
            '공격지역패스 성공%': 'mean',
            '수비지역패스 시도': 'sum',
            '수비지역패스 성공': 'sum',
            '수비지역패스 성공%': 'mean',
            '중앙지역패스 시도': 'sum',
            '중앙지역패스 성공': 'sum',
            '중앙지역패스 성공%': 'mean',
            '롱패스 시도': 'sum',
            '롱패스 성공': 'sum',
            '롱패스 성공%': 'mean',
            '중거리패스 시도': 'sum',
            '중거리패스 성공': 'sum',
            '중거리패스 성공%': 'mean',
            '숏패스 시도': 'sum',
            '숏패스 성공': 'sum',
            '숏패스 성공%': 'mean',
            '크로스 시도': 'sum',
            '크로스 성공': 'sum',
            '크로스 성공%': 'mean',
            '경합 지상 시도': 'sum',
            '경합 지상 성공': 'sum',
            '경합 지상 성공%': 'mean',
            '경합 공중 시도': 'sum',
            '경합 공중 성공': 'sum',
            '경합 공중 성공%': 'mean',
            '태클 시도': 'sum',
            '태클 성공': 'sum',
            '태클 성공%': 'mean',
            '클리어링': 'sum',
            '인터셉트': 'sum',
            '차단': 'sum',
            '획득': 'sum',
            '블락': 'sum',
            '볼미스': 'sum',
            '파울': 'sum',
            '피파울': 'sum',
            '경고': 'sum',
            '퇴장': 'sum',
        }
    ).reset_index()

    # Feature engineering - Defensive Action

    xg_df = pd.DataFrame(xg_data)
    # xG 데이터 기존 데이터 프레임에 병합
    xg_df = xg_df.drop(columns=['순위', '출전수', '출전시간(분)', '슈팅', '득점', '90분당 xG'])
    merge_condition = ['선수명', '구단']
    merged_df = pd.merge(grouped_df, xg_df, on=merge_condition, how='outer')
    merged_df = merged_df.drop_duplicates(subset='index', keep='first')

    # Feature engineering - Defensive Action
    merged_df['Defensive Action'] = (merged_df['태클 시도'] + merged_df['클리어링']
                                     + merged_df['인터셉트'] + merged_df['차단'] + merged_df['블락'])

    # Feature engineering - Possession Won
    merged_df['Possession won'] = (merged_df['획득'] + merged_df['태클 성공'] + merged_df['인터셉트'])

    # 경기당 데이터로 변환할 컬럼
    columns_to_normalize = [
        '득점', '도움', '슈팅', '유효 슈팅', '차단된슈팅', '벗어난슈팅', 'PA내 슈팅', 'PA외 슈팅',
        '오프사이드', '프리킥', '코너킥', '스로인', '드리블 시도', '드리블 성공', '패스 시도', '패스 성공',
        '키패스', '전방 패스 시도', '전방 패스 성공', '후방 패스 시도', '후방 패스 성공', '횡패스 시도',
        '횡패스 성공', '공격지역패스 시도', '공격지역패스 성공', '수비지역패스 시도', '수비지역패스 성공',
        '중앙지역패스 시도', '중앙지역패스 성공', '롱패스 시도', '롱패스 성공', '중거리패스 시도',
        '중거리패스 성공', '숏패스 시도', '숏패스 성공', '크로스 시도', '크로스 성공', '경합 지상 시도',
        '경합 지상 성공', '경합 공중 시도', '경합 공중 성공', '태클 시도', '태클 성공', '클리어링',
        '인터셉트', '차단', '획득', '블락', '볼미스', '파울', '피파울', '경고', '퇴장', 'Defensive Action', 'Possession won', 'xG'
    ]

    # 대상 컬럼의 데이터를 (출전시간 / 90)으로 나눈 새로운 열을 생성
    for col in columns_to_normalize:
        new_col_name = f'{col}/90'
        num_matches = merged_df['출전시간(분)'] / 90
        num_matches.replace(0, np.nan, inplace=True)  # 0을 NaN으로 대체하여 무한대 값 발생 방지
        merged_df[new_col_name] = merged_df[col] / num_matches

    merged_df = merged_df.fillna(0)  # NaN 값을 0으로 대체

    team_df = team_data.iloc[:25]

    # HTML에서 추출된 문자열로 이루어진 데이터를 정수형으로 변환
    for col in team_df.columns:
        if col not in percent_columns:
            team_df.loc[:, col] = team_df[col].apply(convert_to_int)

    team_df.to_csv(input_team_data_file, index=False)
    # 합쳐진 데이터 저장
    merged_df.to_csv(output_preprocessed_file, index=False)
    print(f"Data has been written to {output_preprocessed_file}")

    # 데이터 프레임으로 리턴
    return merged_df
