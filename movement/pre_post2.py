import pandas as pd

# データの読み込み
file_path = '/Users/kazuki-h/scripts/results/repository_data_with_repo.csv'  # CSVファイルのパスを指定してください
data = pd.read_csv(file_path)

# データの時系列順に並べ替え
data['date'] = pd.to_datetime(data['created_at'], utc=True)  # UTCタイムゾーンを指定して日付を変換
data = data.sort_values(by=['developer', 'date'])

# zookeeperリポジトリを定義
zookeeper_repo = 'zookeeper'

# 開発者ごとの移動を追跡し、zookeeper貢献前後を分ける
def track_pre_post_zookeeper(group):
    visited_before = []
    visited_after = []
    seen_zookeeper = False
    
    for _, row in group.iterrows():
        current_repo = row['repo_base']
        
        if current_repo == zookeeper_repo:
            seen_zookeeper = True
        elif seen_zookeeper:
            visited_after.append({'developer': row['developer'], 'repo': current_repo})
        else:
            visited_before.append({'developer': row['developer'], 'repo': current_repo})
    
    return pd.DataFrame({'before': [visited_before], 'after': [visited_after]})

# 開発者ごとの貢献履歴を取得
pre_post_movements = data.groupby('developer', group_keys=False).apply(track_pre_post_zookeeper).reset_index(drop=True)

# 前後のデータを展開
pre_movements = pre_post_movements.explode('before').dropna(subset=['before'])
post_movements = pre_post_movements.explode('after').dropna(subset=['after'])

# リストを展開して個別の開発者とリポジトリを取得
pre_movements = pd.DataFrame(pre_movements['before'].tolist())
post_movements = pd.DataFrame(post_movements['after'].tolist())

# 集計
pre_summary = pre_movements.groupby(['repo', 'developer']).size().reset_index(name='count')
post_summary = post_movements.groupby(['repo', 'developer']).size().reset_index(name='count')

# 結果をCSVに保存
pre_csv_path = 'zookeeper_pre_contribution_detailed.csv'
post_csv_path = 'zookeeper_post_contribution_detailed.csv'

pre_summary.to_csv(pre_csv_path, index=False, encoding='utf-8-sig')
post_summary.to_csv(post_csv_path, index=False, encoding='utf-8-sig')

print(f"Zookeeperに貢献する前の移動元リポジトリを {pre_csv_path} に保存しました。")
print(f"Zookeeperに貢献した後の移動先リポジトリを {post_csv_path} に保存しました。")
