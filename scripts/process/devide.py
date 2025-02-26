import pandas as pd

# 入力 CSV の読み込み（"repo" 列に "owner/repo" の形式の文字列があると仮定）
df = pd.read_csv('./../../results/dependencies/all_dependencies2.csv', encoding='utf-8')


# "repo" 列を "/" で分割して "owner" と "repo" の2列に展開
df[['owner', 'repo']] = df['repo'].str.split('/', expand=True)

# もともとの "repo" 列が不要なら削除することもできます
# df.drop(columns=['repo'], inplace=True)

# 必要に応じて列の順序を調整し、出力 CSV に保存
df.to_csv('./../../results/dependencies/devideRepo.csv', index=False, encoding='utf-8')
