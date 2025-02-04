import pandas as pd
import ast
from itertools import combinations
from collections import defaultdict

# データの読み込み（CSVファイルを読み込む場合）
file_path = "/Users/kazuki-h/newresearch/results/movement/Zout/zookeeper_post_contribution_with_developers.csv"  # ファイルパスを指定
df = pd.read_csv(file_path)

# 1. developersカラムをリスト形式に変換
df['developers'] = df['developers'].apply(ast.literal_eval)

# 2. 開発者トリプルごとの共通リポジトリを収集
triple_to_repos = defaultdict(set)  # トリプルごとにリポジトリを保持

for _, row in df.iterrows():
    repo = row['after']  # リポジトリ名
    developers = row['developers']  # リポジトリに貢献した開発者リスト
    
    # 開発者トリプルを生成して、リポジトリを記録
    for triple in combinations(developers, 3):  # 3人組のすべての組み合わせを生成
        triple = tuple(sorted(triple))  # 順序を統一（('A', 'B', 'C') の形式に固定）
        triple_to_repos[triple].add(repo)

# 3. トリプルごとの共通リポジトリ情報をデータフレームに変換
triple_common_repo_details = [
    {
        "developer_1": triple[0],
        "developer_2": triple[1],
        "developer_3": triple[2],
        "common_repos_count": len(repos),  # 共通リポジトリ数
        "common_repos": list(repos)       # 共通リポジトリ名
    }
    for triple, repos in triple_to_repos.items()
]

# 結果をデータフレームに変換
df_triples = pd.DataFrame(triple_common_repo_details)

# 結果をソートして表示
df_triples.sort_values(by="common_repos_count", ascending=False, inplace=True)

# 4. 結果をCSVに保存
output_path = "./../../results/common_repoCon/out_triple_common_repos_with_details.csv"
df_triples.to_csv(output_path, index=False)

print(f"✅ 結果を {output_path} に保存しました！")
print(df_triples.head())
