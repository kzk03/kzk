import pandas as pd

# ファイルの読み込み
file_path = '../results/repository_data_with_repo.csv'  # ファイルパスを指定
data = pd.read_csv(file_path)

# 'created_at' を datetime 形式に変換 (ISO 8601形式のデータを自動処理)
data['created_at'] = pd.to_datetime(data['created_at'], format="%Y-%m-%dT%H:%M:%SZ", utc=True)

# データを時系列順に並べ替え
data = data.sort_values(by=['developer', 'created_at'])

# zookeeperリポジトリを定義
zookeeper_repo = 'apache/zookeeper'

# 開発者ごとの履歴を追跡
def track_movements(group):
    visited_before = set()
    visited_after = set()
    seen_zookeeper = False

    for _, row in group.iterrows():
        current_repo = row['repo']

        if current_repo == zookeeper_repo:
            seen_zookeeper = True
        elif seen_zookeeper:
            visited_after.add(current_repo)
        else:
            visited_before.add(current_repo)
    
    return pd.Series({'before': list(visited_before), 'after': list(visited_after)})

# 開発者ごとの移動を記録
movements = data.groupby('developer').apply(track_movements).reset_index()

# before, afterを展開して集計
before_movements = movements.explode('before')[['developer', 'before']].dropna()
after_movements = movements.explode('after')[['developer', 'after']].dropna()

# ユニークな開発者をリポジトリごとにカウント
unique_to_zookeeper = before_movements['before'].value_counts().reset_index()
unique_to_zookeeper.columns = ['repo', 'count']

unique_from_zookeeper = after_movements['after'].value_counts().reset_index()
unique_from_zookeeper.columns = ['repo', 'count']

# 結果をCSVに保存
unique_to_zookeeper.to_csv('zookeeper_pre_contribution2.csv', index=False, encoding='utf-8-sig')
unique_from_zookeeper.to_csv('zookeeper_post_contribution2.csv', index=False, encoding='utf-8-sig')

print("結果を以下のファイルに保存しました：")
print("zookeeper_pre_contribution2.csv")
print("zookeeper_post_contribution2.csv")
