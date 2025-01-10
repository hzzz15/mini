import pandas as pd

# CSV 데이터 로드
songs_data = pd.read_csv("data/songs.csv")

print(songs_data.head())
print(songs_data.columns)
print(songs_data["Mood"].unique())

