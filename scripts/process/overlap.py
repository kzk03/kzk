import pandas as pd

# ファイルを読み込む
pre_contributions = pd.read_csv('../movement/zookeeper_pre_contribution_with_developers.csv')
post_contributions = pd.read_csv('../movement/zookeeper_post_contribution_with_developers.csv')

# 開発者リストを文字列からリスト形式に変換
pre_contributions['developers'] = pre_contributions['developers'].apply(eval)
post_contributions['developers'] = post_contributions['developers'].apply(eval)

# 重複を計算する関数
def count_overlapping_developers(row):
    pre_developers = set(row['pre_developers'])
    post_developers = set(row['post_developers'])
    return len(pre_developers & post_developers)

# 各リポジトリの重複を計算
overlap_results = []

for pre_idx, pre_row in pre_contributions.iterrows():
    for post_idx, post_row in post_contributions.iterrows():
        overlap = count_overlapping_developers({
            'pre_developers': pre_row['developers'],
            'post_developers': post_row['developers']
        })
        overlap_results.append({
            'pre_repo': pre_row['before'],
            'post_repo': post_row['after'],
            'overlap_count': overlap
        })

# 結果を DataFrame に変換
overlap_df = pd.DataFrame(overlap_results)

# 結果を確認
print(overlap_df)

# 結果を CSV に保存
overlap_df.to_csv('repository_overlap_counts.csv', index=False, encoding='utf-8-sig')
print("重複数を保存しました: repository_overlap_counts.csv")