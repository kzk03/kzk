import pandas as pd

# CSVファイルの読み込み
file_path = "/Users/kazuki-h/newresearch/results/issue_pr/developer_merge_contributions.csv"  # 実際のファイルパスを指定
df = pd.read_csv(file_path)

# developer のユニークなリストを取得
unique_developers = df['developer'].dropna().unique().tolist()

# repo のユニークなリストを取得
unique_repos = df['repo'].dropna().unique().tolist()

# developer のリストを保存
developer_df = pd.DataFrame({'developer': unique_developers})
developer_output_path = "unique_developer_list.csv"
developer_df.to_csv(developer_output_path, index=False, encoding="utf-8")

# repo のリストを保存
repo_df = pd.DataFrame({'repo': unique_repos})
repo_output_path = "unique_repo_list.csv"
repo_df.to_csv(repo_output_path, index=False, encoding="utf-8")

print(f"DeveloperリストのCSV: {developer_output_path}")
print(f"RepoリストのCSV: {repo_output_path}")