import pandas as pd

# ファイルのパスを指定（ローカル環境）
file_path = "../results/contributions_by_repository.csv"  

# CSVを読み込む
contributions_data = pd.read_csv(file_path)

# ユーザーごとの貢献数を集計
user_contributions = contributions_data.groupby('user_login')[['pr_count', 'issue_count']].sum().reset_index()
user_contributions['total_contributions'] = user_contributions['pr_count'] + user_contributions['issue_count']

# リポジトリごとの貢献数を集計
repo_contributions = contributions_data.groupby('repository')[['pr_count', 'issue_count']].sum().reset_index()
repo_contributions['total_contributions'] = repo_contributions['pr_count'] + repo_contributions['issue_count']

# ファイルに保存
user_contributions_file = "../results/user_contributions.csv"
repo_contributions_file = "../results/repository_contributions.csv"

user_contributions.to_csv(user_contributions_file, index=False)
repo_contributions.to_csv(repo_contributions_file, index=False)

print(f"ユーザーごとの貢献データを {user_contributions_file} に保存しました。")
print(f"リポジトリごとの貢献データを {repo_contributions_file} に保存しました。")