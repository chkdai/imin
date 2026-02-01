import streamlit as st
import pandas as pd
from pathlib import Path

# スクリプトの場所を基準にパスを解決
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'

df = pd.read_csv(DATA_DIR / 'streamlit.csv')
df['割合'] = round(df['外国人人口'] / df['総人口'] * 100, 2)

st.title('外国人人口割合')

# 都道府県の選択
pref_list = df[df['level'] == 'pref']['都道府県'].tolist()
selected_pref = st.selectbox('都道府県を選択', ['全国'] + pref_list)

if selected_pref == '全国':
    # 全国：都道府県一覧を表示（都道府県番号の昇順）
    df_display = df[df['level'] == 'pref'].sort_values('都道府県番号')
else:
    # 都道府県が選択された場合
    df_pref = df[df['都道府県'] == selected_pref]

    # 区がある市は除外し、代わりに区を表示
    cities_with_wards = df_pref[df_pref['level'] == 'ward']['parent_code'].unique()
    df_cities_without_wards = df_pref[(df_pref['level'] == 'city') & (~df_pref['index'].isin(cities_with_wards))]
    df_wards = df_pref[df_pref['level'] == 'ward']
    df_display = pd.concat([df_cities_without_wards, df_wards])

    # 割合で降順ソート
    df_display = df_display.sort_values('割合', ascending=False)

# 表示カラムを選択
display_cols = ['都道府県', '市区町村', '総人口', '外国人人口', '割合']
st.dataframe(df_display[display_cols].reset_index(drop=True))
