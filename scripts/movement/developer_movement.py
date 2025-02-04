import pandas as pd

# ファイルの読み込み
file_path = '/Users/kazuki-h/scripts/results/issue_pr/developer_merge_contributions.csv'
data = pd.read_csv(file_path)

# 'created_at' を datetime 形式に変換
data['created_at'] = pd.to_datetime(data['created_at'], errors='coerce', utc=True)
data = data.dropna(subset=['created_at']).sort_values(by=['developer', 'created_at'])

# 'repo' 列からリポジトリ名を抽出
data['repo'] = data['repo'].str.extract(r'repos/([^/]+/[^/]+)$')[0]
print("修正後の 'repo' 列:")
print(data['repo'].head())

# zookeeper リポジトリの定義
zookeeper_repo = 'apache/zookeeper'

# zookeeper_repo に関連するデータを確認
print("zookeeper_repo に関連するデータ:")
zookeeper_data = data[data['repo'] == zookeeper_repo]
print(zookeeper_data)

# 移動を追跡する関数
def track_movements(group):
    visited_before = set()
    visited_after = set()
    seen_zookeeper = False

    for _, row in group.iterrows():
        current_repo = row['repo']
        print(f"Processing repo: {current_repo}, seen_zookeeper: {seen_zookeeper}")

        if current_repo == zookeeper_repo:
            seen_zookeeper = True
        elif seen_zookeeper:
            visited_after.add(current_repo)
        else:
            visited_before.add(current_repo)
    return pd.Series({'before': list(visited_before), 'after': list(visited_after)})

# 開発者ごとの移動を記録
movements = data.groupby('developer').apply(track_movements).reset_index()
print("movements のデバッグ:")
print(movements)

# before, after を展開して集計
before_movements = movements.explode('before')[['developer', 'before']].dropna()
after_movements = movements.explode('after')[['developer', 'after']].dropna()

print("before_movements のデバッグ:")
print(before_movements)

print("after_movements のデバッグ:")
print(after_movements)

# リポジトリごとにユニークな開発者名のリストを作成
before_grouped = before_movements.groupby('before').agg(
    count=('developer', 'nunique'),
    developers=('developer', lambda x: list(x.unique()))
).reset_index()

after_grouped = after_movements.groupby('after').agg(
    count=('developer', 'nunique'),
    developers=('developer', lambda x: list(x.unique()))
).reset_index()

# CSVに保存
before_grouped.to_csv('zookeeper_pre_contribution_with_developers.csv', index=False, encoding='utf-8-sig')
after_grouped.to_csv('zookeeper_post_contribution_with_developers.csv', index=False, encoding='utf-8-sig')

print("結果を以下のファイルに保存しました：")
print("zookeeper_pre_contribution_with_developers.csv")
print("zookeeper_post_contribution_with_developers.csv")