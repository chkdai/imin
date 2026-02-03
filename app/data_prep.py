import pandas as pd
from pathlib import Path

###############################################
# データの読み込みとmerge
###############################################
# スクリプトの場所を基準にパスを解決
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'

file_ttl = DATA_DIR / '000892952.xlsx'
df_ttl = pd.read_excel(file_ttl, skiprows=5)
df_ttl = df_ttl.iloc[:, [0,1,2,5]]
df_ttl.columns=['index','都道府県','市区町村','総人口']
# display(df_ttl.head())

file_gaijin = DATA_DIR / '000892960.xlsx'
df_gaijin = pd.read_excel(file_gaijin, skiprows=5)
df_gaijin = df_gaijin.iloc[:, [0,1,2,5]]
df_gaijin.columns=['index','都道府県','市区町村','外国人人口']
# display(df_gaijin.head())

file_dantai = DATA_DIR / 'dantai_code.csv'
df_dantai = pd.read_csv(file_dantai)
df_dantai.columns = ['index', 'level']

df = pd.merge(df_ttl, df_gaijin, on=['index','都道府県','市区町村'], how='left')
df = pd.merge(df, df_dantai, on=['index'], how='left')

###############################################
# 都道府県番号を追加
###############################################
pref_list = [
    '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県',
    '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県',
    '福井県', '山梨県', '長野県', '岐阜県', '静岡県', '愛知県', '三重県', '滋賀県', '京都府',
    '大阪府', '兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
    '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県',
    '宮崎県', '鹿児島県', '沖縄県'
]

# 1. 辞書を作成（1番から開始。2桁の文字列にする場合は zfill を使用）
pref_map = {name: str(i + 1).zfill(2) for i, name in enumerate(pref_list)}

# 2. 確認
print(pref_map)
# 結果例: {'北海道': '01', '青森県': '02', ..., '沖縄県': '47'}
###############################################

# 1. 抽出：pref_mapのキー（都道府県名）に含まれる行だけを残す
df_filtered = df[df['都道府県'].isin(pref_map.keys())].copy()

# 2. 都道府県番号の付与：pref_mapを使って「01」「11」「12」などを入れる
df_filtered['都道府県番号'] = df_filtered['都道府県'].map(pref_map)

# 3. カラムの並べ替えと選択
# 元の「index」と、新しく作った「都道府県番号」を含め、ご指定の順番に整理します
df_final = df_filtered[['index', 'level', '都道府県番号', '都道府県', '市区町村', '総人口', '外国人人口']]

# 4. 並べ替え：都道府県番号(JIS順) → 元のindex順
# これにより、北海道から沖縄までが正しい順序で並びます
df_final = df_final.sort_values(['都道府県番号', 'index']).reset_index(drop=True)

# ###############################################
# # 5. 階層レベル(level)と親コード(parent_code)を追加
# ###############################################
# import re

# def get_level(row):
#     """階層レベルを判定"""
#     if row['市区町村'] == '-':
#         return 'pref'  # 都道府県
#     # 「○○市△△区」形式（政令指定都市の区）
#     if re.match(r'.+市.+区$', str(row['市区町村'])):
#         return 'ward'
#     return 'city'  # 市町村

# def extract_city_name(shikuchoson):
#     """「札幌市中央区」から「札幌市」を抽出"""
#     match = re.match(r'(.+市).+区$', str(shikuchoson))
#     if match:
#         return match.group(1)
#     return None

# df_final['level'] = df_final.apply(get_level, axis=1)

# # 都道府県コードのマッピング（index → 都道府県行）
# pref_index_map = df_final[df_final['level'] == 'pref'].set_index('都道府県')['index'].to_dict()

# # 市のindexマッピング（都道府県+市名 → index）
# city_index_map = {}
# for _, row in df_final[df_final['level'] == 'city'].iterrows():
#     key = (row['都道府県'], row['市区町村'])
#     city_index_map[key] = row['index']

# def get_parent_code(row):
#     """親コードを取得"""
#     if row['level'] == 'pref':
#         return None
#     elif row['level'] == 'ward':
#         city_name = extract_city_name(row['市区町村'])
#         if city_name:
#             return city_index_map.get((row['都道府県'], city_name))
#     else:  # city
#         return pref_index_map.get(row['都道府県'])
#     return None

# df_final['parent_code'] = df_final.apply(get_parent_code, axis=1)

# 結果の確認
print(df_final.head(20))

df_final.to_csv(DATA_DIR / 'streamlit.csv', index=False)

