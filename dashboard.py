import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Output, Input, State
import pandas as pd
from polar_bar_chart import PolarBarChart
from transform import preprocessing


# Dash 애플리케이션 생성
app = dash.Dash(__name__)

RECENTLY_UPDATED_ROUND = 33

updated_round_detect = preprocessing(RECENTLY_UPDATED_ROUND)

data = pd.read_csv(f'data/preprocessed/{RECENTLY_UPDATED_ROUND}-round-preprocessed.csv')
df = pd.DataFrame(data)

app.layout = html.Div([
    # Dropdowns are aligned and set with specific width
    html.Div([
        # Header Section
        html.Header([
            html.H1("K LEAGUE DASHBOARD", style={'textAlign': 'center', 'color': 'white'}),
        ], style={
            'backgroundColor': '#003366',  # K리그 색상과 어울리는 배경색
            'padding': '20px',
            'marginBottom': '30px'
        })]),
    html.Div([
        dcc.Dropdown(
            id='team-dropdown',
            options=[{'label': team, 'value': team} for team in df['구단'].unique()],
            value=df['구단'].unique()[0],
            style={'width': '260px', 'marginRight': '10px'}  # 너비 설정
        ),
        dcc.Dropdown(
            id='player-dropdown',
            style={'width': '260px'}  # 너비 설정
        ),
    ], style={'textAlign': 'center', 'display': 'flex', 'justifyContent': 'center'}),  # 전체 Dropdowns를 중앙에 배치

    # 라운드 번호 입력을 위한 드래그바와 버튼
    html.Div([
        html.Label("Select Round Number"),
        dcc.Slider(
            id='round-slider',
            min=20,
            max=RECENTLY_UPDATED_ROUND,  # 예시로 1~38 라운드 설정
            value=RECENTLY_UPDATED_ROUND,  # 기본값으로 27라운드 설정
            marks={i: str(i) for i in range(20, RECENTLY_UPDATED_ROUND + 1)},
            step=1,
        ),
    ], style={'width': '540px', 'margin': '20px auto', 'textAlign': 'center'}),

    # TODO MF <-> FW 전환 기능
    # TODO Hover 정보에 percentile_rank() 적용 전 raw_data 출력
    html.Div([
        dcc.Graph(id='radar-chart')
    ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin': '10px auto'}),

    # Checklist
    dcc.Checklist(
        id='column-checklist',
        options=[{'label': col, 'value': col} for col in df.columns if col not in ['index', '선수명', '구단', '포지션', '등번호']],
        value=['득점', '도움', '키패스'],  # 기본 선택 컬럼
        inline=True,
        style={
            'display': 'grid',
            'grid-template-columns': 'repeat(7, 1fr)',  # 7열로 배치
            'gap': '10px',  # 항목 간의 간격
            'margin': '20px 0'  # 상하 마진 추가
        }
    ),
])


@app.callback(
    Output('team-dropdown', 'options'),
    [Input('round-slider', 'value')]
)
def update_team_dropdown(selected_round):
    # 슬라이드 바에서 선택한 라운드에 해당하는 CSV 파일을 로드
    df = pd.read_csv(f'data/preprocessed/{selected_round}-round-preprocessed.csv')
    options = [{'label': team, 'value': team} for team in df['구단'].unique()]
    return options


@app.callback(
    Output('player-dropdown', 'options'),
    [Input('team-dropdown', 'value')],
    [State('round-slider', 'value')]
)
def update_player_dropdown(selected_team, selected_round):
    if selected_team is None:
        return []

    # 슬라이드 바에서 선택한 라운드에 해당하는 CSV 파일을 로드
    df = pd.read_csv(f'data/preprocessed/{selected_round}-round-preprocessed.csv')
    options = [{'label': player, 'value': player} for player in df[df['구단'] == selected_team]['선수명'].unique()]
    return options


@app.callback(
    Output('radar-chart', 'figure'),
    [Input('round-slider', 'value'),
     Input('player-dropdown', 'value'),
     Input('team-dropdown', 'value'),
     Input('column-checklist', 'value')]
)
def update_chart(selected_round, selected_player, selected_team, selected_columns):
    if not selected_player or not selected_team or not selected_columns:
        fig = go.Figure()
        fig.update_layout(
            annotations=[{
                'text': f"No data available for player {selected_player}",
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
        return fig

    # 슬라이드 바에서 선택한 라운드에 해당하는 CSV 파일을 로드
    df = pd.read_csv(f'data/preprocessed/{selected_round}-round-preprocessed.csv')

    # RadarChart 클래스의 인스턴스를 생성하여 데이터를 처리하고 그래프를 생성
    chart = PolarBarChart(player_name=selected_player, team_name=selected_team,
                          round_number=selected_round, df=df, radar_columns=selected_columns)
    return chart.get_figure()


if __name__ == '__main__':
    app.run_server(debug=True)
