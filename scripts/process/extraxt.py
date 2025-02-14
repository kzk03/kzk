import pandas as pd

# CSV ファイルからデータを読み込む
df = pd.read_csv('/Users/kazuki-h/newresearch/results/monthly_contributions.csv')

# 'apache/zookeeper' のみを抽出
zookeeper_df = df[df['repository'] == 'apache/zookeeper']

# month でグループ化し、contribution_count を合計し、貢献人数をカウント
grouped = zookeeper_df.groupby('month').agg(
    total_contributions=('contribution_count', 'sum'),
    unique_contributors=('developer', 'nunique')
).reset_index()

grouped.to_csv('/Users/kazuki-h/newresearch/results/monthly_contributions.csv', index=False)