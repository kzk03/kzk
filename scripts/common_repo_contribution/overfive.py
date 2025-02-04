import pandas as pd
import ast
from itertools import combinations
from collections import defaultdict

# データの読み込み（CSVファイルを読み込む場合）
file_path = "/Users/kazuki-h/newresearch/results/movement/Zinto/zookeeper_pre_contribution_with_developers.csv"  # ファイルパスを指定
df = pd.read_csv(file_path)

# 1. developersカラムをリスト形式に変換
df['developers'] = df['developers'].apply(ast.literal_eval)

def analyze_common_repos(group_size):
    """
    任意の人数のグループに対する共通リポジトリ分析を行う
    :param group_size: グループのサイズ（例: 5人組なら5, 6人組なら6）
    :return: 共通リポジトリ情報のデータフレーム
    """
    group_to_repos = defaultdict(set)  # グループごとにリポジトリを保持

    # グループごとの共通リポジトリを収集
    for _, row in df.iterrows():
        repo = row['before']  # リポジトリ名
        developers = row['developers']  # リポジトリに貢献した開発者リスト

        # 指定されたグループサイズで組み合わせを生成
        for group in combinations(developers, group_size):
            group = tuple(sorted(group))  # 順序を統一（例: ('A', 'B', 'C', 'D', 'E')）
            group_to_repos[group].add(repo)

    # グループごとの共通リポジトリ情報をデータフレームに変換
    group_common_repo_details = [
        {
            **{f"developer_{i+1}": group[i] for i in range(group_size)},  # 各開発者を列に展開
            "common_repos_count": len(repos),  # 共通リポジトリ数
            "common_repos": list(repos)       # 共通リポジトリ名
        }
        for group, repos in group_to_repos.items()
    ]

    # 結果をデータフレームに変換
    df_groups = pd.DataFrame(group_common_repo_details)

    # 結果をソートして表示
    df_groups.sort_values(by="common_repos_count", ascending=False, inplace=True)
    
    return df_groups

# 2. 5人組から10人組までを一気に分析
results = {}
for group_size in range(5, 13):  # 5人組から10人組まで
    print(f"🔍 {group_size}人組を分析中...")
    results[group_size] = analyze_common_repos(group_size)
    output_path = f"./../../results/common_repoCon/into_{group_size}_common_repos_with_details.csv"
    results[group_size].to_csv(output_path, index=False)
    print(f"✅ {group_size}人組の結果を '{output_path}' に保存しました！")

# 3. 結果のサンプルを表示
for group_size, df_result in results.items():
    print(f"\n🔍 {group_size}人組の結果:")
    print(df_result.head())
