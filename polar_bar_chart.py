import plotly.graph_objects as go
import numpy as np
from scipy.stats import rankdata


class PolarBarChart(object):
    def __init__(self, player_name, team_name, round_number, df, radar_columns):
        self.fig = go.Figure()
        self.teams_division_2 = [
            '경남', '수원', '전남', '천안', '안산', '서울E', '성남', '김포', '충북청주', '안양', '충남아산', '부산', '부천'
        ]
        self.df = df
        self.player_name = player_name
        self.team_name = team_name
        self.round_number = round_number
        self.player_position = self.df[self.df['선수명'] == player_name]["포지션"].values[0]
        self.string_column = ['index', '선수명', '구단', '포지션', '등번호']
        self.radar_columns = radar_columns

        # 특정 선수의 포지션과 팀 기준으로 필터링
        self.relative_df = df[df['포지션'] == self.player_position]
        self.relative_df = self.relative_df[self.relative_df['출전시간(분)'] >= 450]

        # 퍼센타일 스케일링
        def percentile_rank(x):
            if len(np.unique(x)) == 1:
                return np.zeros(len(x))
            ranks = rankdata(x)
            scaled = 100 * (ranks - 1) / (len(ranks) - 1)
            return scaled

        self.radar_scaled_df = self.relative_df.copy()
        self.radar_scaled_df[self.radar_columns] = self.relative_df[self.radar_columns].apply(percentile_rank)

        # 특정 선수의 데이터 추출
        self.target_df = self.radar_scaled_df[
            (self.radar_scaled_df["선수명"] == player_name) &
            (self.radar_scaled_df["구단"] == team_name)][self.radar_columns]

    def get_figure(self):
        if self.target_df.empty:
            # 빈 차트 대신 텍스트 표시
            self.fig.update_layout(
                annotations=[{
                    'text': f"No data available for player {self.player_name}",
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {
                        'size': 20,
                        'family': 'MyCustomFont, sans-serif',
                        'color': 'white'
                    },
                    'x': 0.5,
                    'y': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'middle'
                }],
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgb(0,89,167)',
                width=960,
                height=540,
                xaxis=dict(
                    showgrid=False,  # x축 그리드 라인 숨기기
                    zeroline=False,  # x축 기준선 숨기기
                    visible=False,  # x축 자체 숨기기
                ),
                yaxis=dict(
                    showgrid=False,  # y축 그리드 라인 숨기기
                    zeroline=False,  # y축 기준선 숨기기
                    visible=False,  # y축 자체 숨기기
                )
            )
            return self.fig

        else:
            categories = self.radar_columns
            values = self.target_df.values.flatten().tolist()

            # Close the loop
            values += values[:1]
            categories += categories[:1]

            opacities = [
                0.4 if value <= 30 else
                0.6 if value <= 70 else
                0.8 if value <= 90 else 1
                for value in values
            ]

            self.fig.add_trace(go.Barpolar(
                r=values,
                theta=categories,
                name=self.player_name,
                marker=dict(
                    color='#003366',
                    line=dict(
                        color='#003366'
                    ),
                    opacity=opacities
                )
            ))

            self.fig.update_layout(
                width=960,
                height=540,
                polar=dict(
                    bgcolor='rgba(255, 255, 255, 0.1)',
                    radialaxis=dict(
                        range=[0, 100],
                    ),
                    angularaxis=dict(
                        direction='clockwise',
                        showgrid=False,
                        rotation=0
                    ),
                ),
                plot_bgcolor='rgb(0,22,72)',
                paper_bgcolor='rgb(0,89,167)',
                title=dict(
                    text=f"K LEAGUE Chart",
                    x=0.5,  # 제목 중앙 정렬
                    y=0.95,  # 제목 위치 위에서 90%
                    xanchor='center',
                    yanchor='top',
                    font=dict(
                        size=25,
                        family="MyCustomFont, sans-serif",
                        color="white"  # 제목 색상 변경
                    ),
                    pad=dict(
                        b=30,
                    )
                ),
                font=dict(family='MyCustomFont, sans-serif',
                          size=15,
                          color='white',
                          ),
                annotations=[
                    go.layout.Annotation(
                        text=(
                            f'R o u n d:'
                            '<br>'
                            f'N  a  m  e:'
                            '<br>'
                            f'T  e  a  m:'
                            '<br>'
                            f'Position:'
                        ),
                        align='left',
                        x=0.85,
                        y=0.9,
                        xanchor='left',
                        yanchor='top',
                        font=dict(
                            size=17,
                            family="MyCustomFont, sanserif",
                            color="white"
                        )
                    ),
                    go.layout.Annotation(
                        text=(
                            f'{self.round_number}라운드'
                            '<br>'
                            f'{self.player_name}'
                            '<br>'
                            f'{self.team_name}'
                            '<br>'
                            f'{self.player_position}'
                        ),
                        align='right',
                        x=1.05,
                        y=0.9,
                        xanchor='right',
                        yanchor='top',
                        font=dict(
                            size=17,
                            family="MyCustomFont, sanserif",
                            color="white"
                        )
                    )
                ]
            )

            return self.fig
