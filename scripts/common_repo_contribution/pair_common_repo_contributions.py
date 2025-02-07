import ast
from collections import defaultdict
from itertools import combinations

import pandas as pd

# データの読み込み（CSVから）
file_path = "../results/movement/Zout/zookeeper_post_contribution_with_developers.csv"  # CSVファイルのパス

df = pd.read_csv(file_path)

# 1. developersカラムをリスト形式に変換
df['developers'] = df['developers'].apply(ast.literal_eval)

# 2. リストの要素を展開（1人ずつのデータに分割）
expanded_df = df.explode('developers')

# 3. 開発者ペアごとの共通リポジトリ数を計算
pair_to_repos = defaultdict(set)  # ペアごとにリポジトリを保持

# 元のデータフレームを使ってペアを収集
for _, row in df.iterrows():
    repo = row['after']  # リポジトリ名
    developers = row['developers']  # リポジトリに貢献した開発者リスト
    
    # 開発者ペアを生成して、リポジトリを記録
    for pair in combinations(developers, 2):  # すべてのペアを生成
        pair = tuple(sorted(pair))  # 順序を統一（('A', 'B') と ('B', 'A')を同一視）
        pair_to_repos[pair].add(repo)

# 4. ペアごとの共通リポジトリ情報をデータフレームに変換
pair_common_repo_details = [
    {
        "developer_1": pair[0],
        "developer_2": pair[1],
        "common_repos_count": len(repos),  # 共通リポジトリ数
        "common_repos": list(repos)       # 共通リポジトリ名
    }
    for pair, repos in pair_to_repos.items()
]

# 結果をデータフレームに変換
df_pairs = pd.DataFrame(pair_common_repo_details)

# 結果をソートして表示
df_pairs.sort_values(by="common_repos_count", ascending=False, inplace=True)

# 5. 結果をCSVに保存
output_path = "../results/out_common_repos.csv"
df_pairs.to_csv(output_path, index=False)

print(f"✅ 結果を {output_path} に保存しました！")
print(df_pairs.head())
