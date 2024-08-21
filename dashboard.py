import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd
from scipy.stats import rankdata
import numpy as np


class RadarChart(object):
    def __init__(self, player_name, team_name, round_number, df, radar_columns):
        self.fig = go.Figure()
        self.teams_division_2 = ['수원', '전남', '천안', '안산', '서울E', '성남', '김포', '충북청주', '안양', '충남아산', '부산', '부천']
        self.df = df
        self.df = self.df[~self.df['구단'].isin(self.teams_division_2)]
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
            (self.radar_scaled_df["구단"] == team_name)
            ][self.radar_columns]

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
                        'size': 20
                    },
                    'x': 0.5,
                    'y': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'middle'
                }],
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgb(0,0,0,0)'
            )
            return self.fig

        categories = self.radar_columns
        values = self.target_df.values.flatten().tolist()

        # Close the loop
        values += values[:1]
        categories += categories[:1]

        self.fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=self.player_name,
            line=dict(color='red')
        ))

        self.fig.update_layout(
            width=540,
            height=540,
            polar=dict(
                bgcolor='rgba(255, 255, 255, 0.1)',
                radialaxis=dict(
                    range=[0, 100],
                ),
                angularaxis=dict(
                    showgrid=False,
                ),
            ),
            plot_bgcolor='rgb(0,22,72)',
            paper_bgcolor='rgb(0,89,167)',
            title=dict(
                text=f"{self.player_name} Radar Chart until {self.round_number} Round",
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
                      size=10,
                      color='white',
                      )
        )

        return self.fig


# Dash 애플리케이션 생성
app = dash.Dash(__name__)

data = pd.read_csv('data/preprocessed/27-round-preprocessed.csv')

df = pd.DataFrame(data)

# 레이아웃 설정
app.layout = html.Div([
    dcc.Dropdown(
        id='player-dropdown',
        options=[{'label': player, 'value': player} for player in df['선수명'].unique()],
        value=df['선수명'].iloc[0]
    ),
    dcc.Graph(id='radar-chart')
])

# 레이아웃 설정
app.layout = html.Div([
    dcc.Dropdown(
        id='team-dropdown',
        options=[{'label': team, 'value': team} for team in df['구단'].unique()],
        value=df['구단'].unique()[0]
    ),
    dcc.Dropdown(
        id='player-dropdown'
    ),
    dcc.Graph(id='radar-chart'),
    dcc.Checklist(
        id='column-checklist',
        options=[{'label': col, 'value': col} for col in df.columns if col not in ['index', '선수명', '구단', '포지션', '등번호']],
        value=['득점/xG', '슈팅/90'],  # 기본 선택 컬럼
        inline=True
    ),
])


# 콜백: 선수 선택에 따라 기본 선수 설정
@app.callback(
    dash.dependencies.Output('player-dropdown', 'value'),
    [dash.dependencies.Input('player-dropdown', 'options')]
)
def set_players_value(available_options):
    return available_options[0]['value'] if available_options else None


# 콜백: 구단 선택에 따라 선수 목록을 업데이트
@app.callback(
    dash.dependencies.Output('player-dropdown', 'options'),
    [dash.dependencies.Input('team-dropdown', 'value')]
)
def set_players_options(selected_team):
    filtered_df = df[df['구단'] == selected_team]
    return [{'label': player, 'value': player} for player in filtered_df['선수명'].unique()]


# 콜백: 선택된 컬럼과 선수에 따라 레이더 차트 업데이트
@app.callback(
    dash.dependencies.Output('radar-chart', 'figure'),
    [dash.dependencies.Input('player-dropdown', 'value'),
     dash.dependencies.Input('team-dropdown', 'value'),
     dash.dependencies.Input('column-checklist', 'value')]
)
def update_chart(selected_player, selected_team, selected_columns):
    if not selected_player or not selected_team or not selected_columns:
        return go.Figure()

    chart = RadarChart(player_name=selected_player, team_name=selected_team,
                       round_number=27, df=df, radar_columns=selected_columns)
    return chart.get_figure()


if __name__ == '__main__':
    app.run_server(debug=True)