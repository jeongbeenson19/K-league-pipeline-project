import pandas as pd


with open("k-league-data-20240524-1601", mode='r') as file:
    data = pd.read_csv(file)
    df = pd.DataFrame(data)

name = df['선수명'].tolist()
print(len(name))

