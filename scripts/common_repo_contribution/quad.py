import pandas as pd
import ast
from itertools import combinations
from collections import defaultdict

# データの読み込み（CSVファイルを読み込む場合）
file_path = "/Users/kazuki-h/newresearch/results/movement/Zout/zookeeper_post_contribution_with_developers.csv"  # ファイルパスを指定
df = pd.read_csv(file_path)

# 1. developersカラムをリスト形式に変換
df['developers'] = df['developers'].apply(ast.literal_eval)

# 2. 開発者4人組（クワッド）ごとの共通リポジトリを収集
quad_to_repos = defaultdict(set)  # 4人組ごとにリポジトリを保持

for _, row in df.iterrows():
    repo = row['after']  # リポジトリ名
    developers = row['developers']  # リポジトリに貢献した開発者リスト
    
    # 開発者4人組を生成して、リポジトリを記録
    for quad in combinations(developers, 4):  # 4人組のすべての組み合わせを生成
        quad = tuple(sorted(quad))  # 順序を統一（('A', 'B', 'C', 'D') の形式に固定）
        quad_to_repos[quad].add(repo)

# 3. 4人組ごとの共通リポジトリ情報をデータフレームに変換
quad_common_repo_details = [
    {
        "developer_1": quad[0],
        "developer_2": quad[1],
        "developer_3": quad[2],
        "developer_4": quad[3],
        "common_repos_count": len(repos),  # 共通リポジトリ数
        "common_repos": list(repos)       # 共通リポジトリ名
    }
    for quad, repos in quad_to_repos.items()
]

# 結果をデータフレームに変換
df_quads = pd.DataFrame(quad_common_repo_details)

# 結果をソートして表示
df_quads.sort_values(by="common_repos_count", ascending=False, inplace=True)

# 4. 結果をCSVに保存
output_path = "./../../results/common_repoCon/out_quad_common_repos_with_details.csv"
df_quads.to_csv(output_path, index=False)

print(f"✅ 結果を {output_path} に保存しました！")
print(df_quads.head())
